# ThermoTwin ML

Predictive early warning for vaccine fridges, built from temperature readings only (what eVIN loggers record).

```
simulator -> freeze labels -> digital twin (Virtual Vial) -> features -> LightGBM hazard model
          -> calibration -> alert threshold under a false-alert budget -> Replay Benchmark
```

## Run

```bash
pip install -r requirements.txt
python scripts/train.py              # 240 fridges x 21 days, about 45 s
python scripts/train.py --units 80 --days 14   # quick run
python -m pytest -q                  # tests
```

Trained models go to `artifacts/models.pkl` (freeze, heat and cause models plus alert thresholds); benchmark CSVs,
`summary.json` and logs go to `results/`. The backend's inference service loads `artifacts/models.pkl`.

## Modules

| File | What it does |
|---|---|
| `thermotwin/simulator.py` | ColdChain Gym: 3-node RC fridge physics (air, product, enclosure) at 1-minute steps, thermostat, doors, Indian room temperatures, and injected faults: thermostat drifting cold, relay stuck on, compressor wear, gasket leak, power cut, stuck or drifting probe. Logs every 10 minutes. |
| `thermotwin/labels.py` | Freeze event = true vaccine temperature <= -0.5 °C for 60 min. Reference time for lead time = true vaccine temperature crossing 0 °C. Labels come only from simulator ground truth. |
| `thermotwin/twin.py` | Kalman filter per fridge: state [air, slope, vial]; vial follows Newton's law of cooling with the class time constant (fleet prior). Outputs the Virtual Vial, its uncertainty and physics forecasts at 30/60/120 min. |
| `thermotwin/features.py` | Temperature-only features plus twin outputs. |
| `thermotwin/model.py` | LightGBM discrete-time hazard over twelve 10-minute slots; cumulative risk, time-to-breach P10/P50/P90, isotonic calibration, SHAP explanations. |
| `thermotwin/benchmark.py` | Policies P0 (<= 0 °C), P1 WHO (<= -0.5 °C for 60 min), P2 early rule (<= 2 °C for 30 min), P3 ThermoTwin; recall, lead time, false alerts per fridge-month. |

## Live demo

The live demo now runs from the backend services: `python ../backend/run_all.py`. See [../backend/README.md](../backend/README.md).

## Current result (simulated, held-out fridges, two seeds)

| | Seed 0 | Seed 1 |
|---|---|---|
| Freeze caught (ThermoTwin) | 41/41 | 41/41 |
| Median warning before vaccine reaches 0 °C | 100 min | 110 min |
| False alerts per fridge-month (budget 1.0) | 0.45 | 0.27 |
| WHO rule: warning | 30 min after | 30 min after |
| Early rule (<= 2 °C, 30 min): false alerts | 3.18 | 5.68 |
| Heat caught (ThermoTwin) | 27/31, 30 min | 7/10, 40 min |
| Cause classifier accuracy | 91% | 91% |
| Virtual Vial error (raw air) | 0.08 °C (0.46) | 0.07 °C (0.38) |

All policies use the same incident counting (alerts on one fridge within 6 h are one incident). Thresholds are tuned on
validation fridges with a 20% margin under the false-alert budget. Simulated results, not field results.

## Deep-learning baseline (same fleet, splits, calibration, budget, benchmark)

`python scripts/run_baselines.py --seed 0 --epochs 6` trains an LSTM on the raw air sequence (6 h window, no physics);
`python scripts/tradeoff.py` compares warning time at matched false-alert rates.

| Freeze, held-out fridges | Seed 0 | Seed 1 |
|---|---|---|
| ThermoTwin: caught · warning · false/fridge-month | 41/41 · 100 min · 0.45 | 41/41 · 110 min · 0.27 |
| LSTM (raw air): caught · warning · false/fridge-month | 41/41 · 110 min · 0.60 | 39/41 · 90 min · 0.15 |
| Best warning at <= 0.5 false/fridge-month (TT vs LSTM) | 100 vs 110 min | 110 vs 90 min |
| Best warning at <= 0.25 false/fridge-month (TT vs LSTM) | 50 vs 80 min | 80 vs 90 min |

Conclusion: on warning time the two are comparable; the LSTM is ahead at very strict false-alert budgets. ThermoTwin's
advantage is what the twin adds: the vaccine's estimated temperature, cause and steps, what-if scenarios and holdover.
The LightGBM model is not smaller or faster than this LSTM (about 1.4 MB vs 0.12 MB). Heat: both catch 27-30 of 31 with 30-40 min.

## Modules added

| File | What it does |
|---|---|
| `thermotwin/cause.py` | Cause classifier (cooling too hard, power cut, weak cooling, sensor fault, none) scored against injected faults; rule-based Sensor check |
| `thermotwin/pipeline.py` | Shared training and evaluation for freeze, heat and cause |

## Next

- Chronos/TimesFM baseline; hybrid (LSTM on twin features)
- Realism checks against public fridge traces; cross-simulator test
- Lifeboat-routing calculation in code
