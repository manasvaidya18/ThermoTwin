# ThermoTwin prediction engine

Predictive early warning for vaccine fridges, built from temperature readings only (what eVIN loggers record).

An independent FastAPI service. The Django backend sends it readings; it returns, for every reading, the vaccine's
estimated temperature, the risk and countdown, the likely cause, the reasons, and the slow-loop maintenance outputs.

```
Reading from sensor -> trust check -> digital twin (Kalman filter: Virtual Vial, trend, forecasts +30/+60/+120 min)
  -> feature engineering (now, last 10/30 min, 1/3/6 h, Virtual Vial, forecasts)
       every 10-min reading: Freeze LightGBM, Heat LightGBM -> likely cause (LightGBM) -> recovery check (door opening)
                             -> SHAP reasons
       rolling 1-day window: Cooling Health Index -> compressor-life LightGBM (days until service)
  -> alert (decided by the backend's alerts app)
```

| Folder | What's inside |
|---|---|
| `app/` | `main.py` FastAPI app (`/health`, `/info`, `/score`, `/validate`), `config.py`, `schemas.py` (input/output contracts) |
| `services/` | `prediction_service.py` (runs the steps above in order), `risk_service.py` (freeze/heat hazard models + cause classifier), `explanation_service.py` (SHAP reasons in plain words), `recovery_service.py` (door-opening check), `maintenance_service.py` (Cooling Health Index + compressor-life model), `model_loader.py` |
| `digital_twin/` | `virtual_vial.py` (Kalman filter: Virtual Vial, trend, forecasts), `thermal_model.py` (3-node RC fridge physics: the ColdChain Gym simulator) |
| `ingestion/` | `data_validator.py` (reading validation + trust check), `preprocessing.py` (feature engineering) |
| `models/` | `models.pkl`: freeze, heat, cause and degradation models plus alert thresholds |
| `training/` | labels, benchmark, training pipeline, LSTM baseline, dataset loaders, and `scripts/` |
| `results/` | benchmark and validation outputs |
| `tests/` | engine tests |

Run the service on its own (from the repo root):

```bash
python -m uvicorn prediction_engine.app.main:app --port 8102
```

Training: simulator -> labels from ground truth -> twin -> features -> LightGBM -> calibration -> alert threshold under
a false-alert budget -> benchmark on held-out fridges. Checked on real data: 123 Bangkok fridges (Virtual Vial) and
real service-dated faults in ultra-low freezers (slow loop).

## Run

```bash
# from the repo root
pip install -r prediction_engine/requirements.txt
python prediction_engine/training/scripts/train.py              # 240 fridges x 21 days, about 45 s
python prediction_engine/training/scripts/train_degradation.py  # slow-loop model: 300 fridges x 60 days, about 30 s
python prediction_engine/training/scripts/evaluate_recovery.py  # door openings vs failures on the test fridges
python prediction_engine/training/scripts/validate_bangkok.py   # Virtual Vial on 123 real fridges (needs the dataset)
python prediction_engine/training/scripts/validate_ult_freezers.py   # slow loop on real freezer faults (needs the dataset)
python -m pytest -q prediction_engine/tests
```

Trained models go to `models/models.pkl` (freeze, heat, cause and degradation models plus alert thresholds); `train.py`
keeps an existing degradation model when it rewrites the file. Benchmark CSVs,
`summary.json` and logs go to `results/`. The engine loads `models/models.pkl` (files saved under the old `thermotwin.*` module names still load).

## Modules (detail)

| File | What it does |
|---|---|
| `digital_twin/thermal_model.py` | ColdChain Gym: 3-node RC fridge physics (air, product, enclosure) at 1-minute steps, thermostat, doors, Indian room temperatures, and injected faults: thermostat drifting cold, relay stuck on, compressor wear, gasket leak, power cut, stuck or drifting probe. Logs every 10 minutes. |
| `training/labels.py` | Freeze event = true vaccine temperature <= -0.5 °C for 60 min. Reference time for lead time = true vaccine temperature crossing 0 °C. Labels come only from simulator ground truth. |
| `digital_twin/virtual_vial.py` | Kalman filter per fridge: state [air, slope, vial]; vial follows Newton's law of cooling with the class time constant (fleet prior). Outputs the Virtual Vial, its uncertainty and physics forecasts at 30/60/120 min. |
| `ingestion/preprocessing.py` | Temperature-only features plus twin outputs. |
| `services/risk_service.py` | LightGBM discrete-time hazard over twelve 10-minute slots; cumulative risk, time-to-breach P10/P50/P90, isotonic calibration, SHAP explanations. |
| `training/benchmark.py` | Policies P0 (<= 0 °C), P1 WHO (<= -0.5 °C for 60 min), P2 early rule (<= 2 °C for 30 min), P3 ThermoTwin; recall, lead time, false alerts per fridge-month. |
| `services/risk_service.py` | Cause classifier (cooling too hard, power cut, weak cooling, sensor fault, none) scored against injected faults; rule-based Sensor check |
| `services/recovery_service.py` | Door-opening recovery check (rule): a sharp rise in one reading that falls back within 30 min while the vaccine estimate barely moves is labelled "door opening, recovering, no action needed" |
| `services/maintenance_service.py` | Slow loop: rolling 24 h window features vs the unit's own baseline, Cooling Health Index, and a LightGBM hazard model over the next 14 days (chance of a degradation failure within 7 days, days until service) |
| `training/datasets.py` | Loaders that convert the Bangkok fridge and Danish freezer datasets to the standard 10-minute reading format |
| `training/pipeline.py` | Shared training and evaluation for freeze, heat and cause |

## Live demo

Run `python scripts/run_demo.py` from the repo root (Django backend + this engine). See the root README.

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

`python prediction_engine/training/scripts/run_baselines.py --seed 0 --epochs 6` trains an LSTM on the raw air sequence (6 h window, no physics);
`python prediction_engine/training/scripts/tradeoff.py` compares warning time at matched false-alert rates.

| Freeze, held-out fridges | Seed 0 | Seed 1 |
|---|---|---|
| ThermoTwin: caught · warning · false/fridge-month | 41/41 · 100 min · 0.45 | 41/41 · 110 min · 0.27 |
| LSTM (raw air): caught · warning · false/fridge-month | 41/41 · 110 min · 0.60 | 39/41 · 90 min · 0.15 |
| Best warning at <= 0.5 false/fridge-month (TT vs LSTM) | 100 vs 110 min | 110 vs 90 min |
| Best warning at <= 0.25 false/fridge-month (TT vs LSTM) | 50 vs 80 min | 80 vs 90 min |

Conclusion: on warning time the two are comparable; the LSTM is ahead at very strict false-alert budgets. ThermoTwin's
advantage is what the twin adds: the vaccine's estimated temperature, cause and steps, what-if scenarios and holdover.
The LightGBM model is not smaller or faster than this LSTM (about 1.4 MB vs 0.12 MB). Heat: both catch 27-30 of 31 with 30-40 min.

## Door openings vs failures (recovery vs intervention)

`python prediction_engine/training/scripts/evaluate_recovery.py`, seed-0 test fridges (48 fridges, 21 days, simulated):

| | Result |
|---|---|
| Normal door openings during healthy periods | 6,300 |
| ... that raised no alert | **99.1%** |
| ... labelled "door opening, recovering" by the rule | 59% (72% of openings of 10 min or more; short ones often leave no visible spike in a 10-minute reading) |
| Fault onsets (no door opening nearby) wrongly labelled as a door opening | 8% (the label is a note only and never suppresses an alert) |
| Real freeze failures caught | 41/41 (benchmark above) |

## Slow loop: degradation and days until service

`python prediction_engine/training/scripts/train_degradation.py`: 300 simulated fridges x 60 days, split 60/20/20 by fridge. Labels: the first time
the vaccine exceeds +8 °C for 60 min while compressor wear or a door-seal leak is active. Threshold chosen on validation
fridges under a budget of 0.5 false maintenance alerts per unit-month (an alert is false only if the unit has no
degradation at all).

| Test fridges (simulated) | Result |
|---|---|
| Degradation failures caught before they happened | **22/30**, median **7 days** of warning |
| Wearing units flagged | 37/45, median 10 days after the wear started |
| False maintenance alerts | 0.25 per unit-month |
| Cooling Health Index | median 98 on healthy unit-days, 91 three to seven days before a failure |

While a compressor wears, the thermostat compensates by running longer, so temperature alone shows only a slow creep:
the unit runs warmer than its own normal, most at its warmest moments, and its cooling dips get weaker. A 3-day baseline
matters: against the first 3 days, that creep correlates about twice as strongly with true capacity loss as against day 1.

## Real-data checks

### Virtual Vial on 123 real household fridges (Bangkok)

Dataset: Paviet-Salomon et al., "Dataset of household cold-chain conditions ... Bangkok", Recherche Data Gouv,
DOI 10.57745/TMWYBQ, CC BY-NC-SA 4.0 (used for validation only). 5 days per fridge at 5-minute steps; the twin sees only
the middle-shelf air temperature (every second reading, so 10-minute steps) and is compared with the product probe
(meat-simulating gel, recorded in 0.5 °C steps, so errors below about 0.15 °C cannot be resolved).

| | Result |
|---|---|
| Best-fit product time constant per fridge | **median 60 min** (middle half 45-120 min): the twin's prior |
| Virtual Vial closer to the product than raw air | 106 of 123 fridges |
| Median per-fridge error, twin vs raw air | 0.58 °C vs 0.67 °C |
| After a one-day calibration at installation (offset learned on day 1, scored on days 2-5) | **median per-fridge error 0.28 °C**, mean 0.53 °C; 83% of readings inside the ± band |

Most of the remaining error is a fixed offset: the product sat in a different spot from the air probe. A one-day
reference measurement at installation removes it.

### Slow loop on real freezer faults (Danish National Biobank)

Dataset: Huang et al., "A labelled dataset for long-term performance of Ultra-low Temperature Freezers", Scientific
Data 2023, Figshare 10.6084/m9.figshare.c.6805332, CC0. Results: `results/ult_freezer_validation.json`
(`python prediction_engine/training/scripts/validate_ult_freezers.py`).

For 23 gradual faults from the service records (12 refrigerant leaks, 11 compressor faults, 17 freezers) we took the
chamber temperature for the 2 months before the service date, resampled it to 10-minute readings, and ran the twin,
features and slow loop against each freezer's own first-week baseline. 23 healthy 3-month windows (no fault within
6 months, start-up months excluded) are the comparison. The degradation model is the one trained on simulated 2-8 °C
fridges, applied unchanged at -80 °C.

| | Result |
|---|---|
| Faults with a maintenance alert in the 14 days before the service call | **17/23 (74%)** |
| Healthy 14-day stretches with a maintenance alert | **14%** (of 128) |
| By fault type | refrigerant leaks **11/12**, compressor faults 6/11 |
| Separation of the model score, last 14 days vs healthy days (AUC) | 0.68 (0.5 = none, 1.0 = perfect) |

Caveats: 23 faults is a small sample; fault dates are service-request dates, and some freezers were probably already
running visibly warm when the service was called, so "before the service call" is not always "before anyone noticed".
The Cooling Health Index's scale (25 points per °C) is set for 2-8 °C units and is too sensitive at -80 °C, where door
openings swing the chamber by tens of degrees; a freezer-specific scale is needed before showing it for freezers.

### Getting the datasets

They are not committed. `prediction_engine/data/external/bangkok/raw/` holds the 123 `.txt` files (Recherche Data Gouv API, one request
per file); `prediction_engine/data/external/ult_freezers/raw/` holds selected monthly Revco logs read out of the Figshare zip with HTTP
range requests (the full archive is 9.8 GB), plus `freezer_faults.csv` and `plan.json` listing the windows used.

## Next

- Longer demo history so the slow loop shows a full wear story live
- Chronos/TimesFM baseline; hybrid (LSTM on twin features)
- Cross-simulator test (Benamirouche et al. 2026 synthetic fridge dataset)
- Lifeboat-routing calculation in code
