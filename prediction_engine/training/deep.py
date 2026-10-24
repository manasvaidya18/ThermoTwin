"""Deep-learning baseline: an LSTM on the raw air-temperature sequence (no physics twin).

Same task as the LightGBM hazard model: P(event starts within the next 2 hours), trained on the same fridges,
calibrated and thresholded the same way, scored by the same benchmark.
Input: the last 36 readings (6 hours) of measured air temperature, plus the fridge class.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
import torch
from sklearn.isotonic import IsotonicRegression
from torch import nn

SEQ = 36
HORIZON = 12


class AirLSTM(nn.Module):
    def __init__(self, hidden: int = 48):
        super().__init__()
        self.lstm = nn.LSTM(input_size=2, hidden_size=hidden, num_layers=2, batch_first=True, dropout=0.1)
        self.head = nn.Sequential(nn.Linear(hidden + 1, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, x: torch.Tensor, cls: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        return self.head(torch.cat([out[:, -1], cls], dim=1)).squeeze(1)


def _windows(air: np.ndarray, units_: np.ndarray, ticks: np.ndarray) -> np.ndarray:
    """(n, SEQ, 2) windows: normalised air and its first difference, padded at the start of the record."""
    a = np.nan_to_num(air, nan=np.nanmedian(air))
    pad = np.concatenate([np.repeat(a[:, :1], SEQ, axis=1), a], axis=1)
    idx = ticks[:, None] + np.arange(1, SEQ + 1)[None, :]          # window ends at the current tick
    w = pad[units_[:, None], idx]
    d = np.diff(w, axis=1, prepend=w[:, :1])
    return np.stack([(w - 4.0) / 4.0, d], axis=2).astype(np.float32)


class LSTMBaseline:
    def __init__(self, seed: int = 0, epochs: int = 4, hidden: int = 48):
        torch.manual_seed(seed)
        torch.set_num_threads(8)
        self.net = AirLSTM(hidden)
        self.epochs = epochs
        self.cal: IsotonicRegression | None = None
        self.train_seconds = 0.0

    @property
    def n_params(self) -> int:
        return sum(p.numel() for p in self.net.parameters())

    def fit(self, air: np.ndarray, is_dom: np.ndarray, units_: np.ndarray, to_next: np.ndarray, in_event: np.ndarray,
            rng: np.random.Generator, far_keep: float = 0.06) -> "LSTMBaseline":
        T = air.shape[1]
        uu, tt = np.meshgrid(units_, np.arange(T), indexing="ij")
        uu, tt = uu.ravel(), tt.ravel()
        tn = to_next[uu, tt]
        ok = ~in_event[uu, tt]
        near = tn <= 2 * HORIZON
        keep = ok & (near | (rng.random(uu.size) < far_keep))
        uu, tt, tn = uu[keep], tt[keep], tn[keep]
        X = torch.from_numpy(_windows(air, uu, tt))
        C = torch.from_numpy(is_dom[uu].astype(np.float32))[:, None]
        y = torch.from_numpy((tn <= HORIZON).astype(np.float32))
        w_np = np.where(tn <= 2 * HORIZON, 1.0, 1.0 / far_keep)
        pos = (tn <= HORIZON)
        # Balance positives against the (re-weighted) negatives so rare events are learned; calibration restores
        # true probabilities afterwards.
        w_np = np.where(pos, w_np * (w_np[~pos].sum() / max(w_np[pos].sum(), 1.0)) * 0.5, w_np)
        w = torch.from_numpy((w_np / w_np.mean()).astype(np.float32))
        opt = torch.optim.Adam(self.net.parameters(), lr=2e-3)
        loss_fn = nn.BCEWithLogitsLoss(reduction="none")
        t0 = time.time()
        self.net.train()
        for _ in range(self.epochs):
            perm = torch.randperm(len(y))
            for i in range(0, len(y), 1024):
                b = perm[i:i + 1024]
                opt.zero_grad()
                loss = (loss_fn(self.net(X[b], C[b]), y[b]) * w[b]).mean()
                loss.backward()
                opt.step()
        self.train_seconds = time.time() - t0
        return self

    @torch.no_grad()
    def raw_risk(self, air: np.ndarray, is_dom: np.ndarray, units_: np.ndarray) -> np.ndarray:
        """(len(units_), T) uncalibrated 2-hour risk for every tick."""
        self.net.eval()
        T = air.shape[1]
        out = np.zeros((len(units_), T), dtype=np.float32)
        for j, u in enumerate(units_):
            ticks = np.arange(T)
            X = torch.from_numpy(_windows(air, np.full(T, u), ticks))
            C = torch.full((T, 1), float(is_dom[u]))
            out[j] = torch.sigmoid(self.net(X, C)).numpy()
        return out

    def calibrate(self, raw: np.ndarray, units_: np.ndarray, to_next: np.ndarray, in_event: np.ndarray) -> None:
        tn = to_next[units_]
        ok = ~in_event[units_]
        self.cal = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1)
        self.cal.fit(raw[ok], (tn[ok] <= HORIZON).astype(float))

    def risk(self, raw: np.ndarray) -> np.ndarray:
        return self.cal.predict(raw.ravel()).reshape(raw.shape)


def time_inference(fn, *args, repeats: int = 3) -> float:
    """Median seconds per call."""
    ts = []
    for _ in range(repeats):
        t0 = time.time()
        fn(*args)
        ts.append(time.time() - t0)
    return float(np.median(ts))


def frame_to_grid(pred: pd.DataFrame, col: str, n: int, T: int) -> np.ndarray:
    g = np.zeros((n, T))
    g[pred["unit"], pred["tick"]] = pred[col]
    return g
