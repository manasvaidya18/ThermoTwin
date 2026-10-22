# ML and Physics Methods for Predicting and Diagnosing Cold-Storage Temperature Excursions (ThermoTwin)

Scope note: research run 2026-10-11. Sources were gathered with web search and page fetches. Where a figure comes from a search-result summary rather than the full paper, that is noted. Citations marked "(from background knowledge, DOI/arXiv given)" are standard references whose identifiers I am confident in but whose full text I did not open this session. The report writer should treat those as lower verification level.

## 1. Grey-box / RC thermal models of refrigerators, vaccine fridges and cold rooms (structures, identification, parameters, digital twins)

### Takeaway
A 2nd or 3rd-order linear RC model (air node + evaporator/heat-exchanger node + envelope or product node), identified by maximum likelihood with a Kalman-filter-based likelihood (CTSM), is the best-documented grey-box structure for a real household freezer. It gives about 0.3 °C residual std at 20 minutes ahead, with a slowest time constant of about 4 h. Published, citable RC parameter values for vaccine fridges and cold rooms are scarce. Most cold-room work uses first-order-plus-delay fits, two-zone air/product lumped models, or CFD.

### Cited Findings
- **Sossan et al. (DTU), "Grey-box Modelling of a Household Refrigeration Unit Using Time Series Data in Application to Demand Side Management", Sustainable Energy, Grids and Networks (accepted; arXiv 2015).** Real data from a Bosch GSN40A2111 333 L domestic freezer, empty and door closed, sampled at 1 s. The compressor was excited with a PRBS on the plug. Max compressor power was about 68 W. — [arXiv:1510.06855](https://arxiv.org/abs/1510.06855) / [ar5iv HTML](https://ar5iv.labs.arxiv.org/html/1510.06855)
  - Model family: (A) 1st order, air node only, heat extraction Q = P·COP. (B) 2nd order, air + heat exchanger. (C) 3rd order, heat exchanger + air + envelope (Ce–Re, Ca–Ra, Cw–Rw). (D) 4th order, rejected as not significant (likelihood-ratio test p = 61%). (E) Nonlinear 3rd order with COP from the reversed Carnot cycle times an efficiency η. — [ar5iv](https://ar5iv.labs.arxiv.org/html/1510.06855)
  - Identification: maximum likelihood via CTSM (R). Model selection by residual autocorrelation, likelihood-ratio (Wilks) tests and cross-validation. — [ar5iv](https://ar5iv.labs.arxiv.org/html/1510.06855)
  - Slowest time constant about 4 hours. Empirical physical estimates: interior air thermal capacity about 5×10² J/K, insulation capacity about 5×10³ J/K, heat-exchanger capacity about 1×10⁴ J/K, insulation thermal resistance about 1.3 K/W. The identified Ca in model E was about two orders of magnitude larger than the empirical air capacity, because the lumped "air" node absorbs other masses. — [ar5iv](https://ar5iv.labs.arxiv.org/html/1510.06855)
  - 20-min-ahead residuals (mean / std, °C) under thermostatic operation: model B 0.15 / 0.73; model C 0.056 / 0.29; model E 0.023 / 0.27. Under PRBS: model A 0.593 / 2.8 (residuals correlated, i.e. poor fit). — [ar5iv](https://ar5iv.labs.arxiv.org/html/1510.06855)
  - Model E (nonlinear) predicted best but performed poorly inside MPC. Linear model C gave the best MPC result. — [ar5iv](https://ar5iv.labs.arxiv.org/html/1510.06855)
- CTSM (Continuous Time Stochastic Modelling) estimates SDE grey-box models by maximum likelihood, with the likelihood evaluated by an (extended) Kalman filter. — [CTSM-R](https://ctsm.info) (from background knowledge)
- Classic structure-selection method for RC grey-box models: forward selection from simple to complex RC networks using likelihood-ratio tests. Bacher, P. & Madsen, H. (2011), "Identifying suitable models for the heat dynamics of buildings", Energy and Buildings 43(7):1511–1522. — [DOI 10.1016/j.enbuild.2011.02.005](https://doi.org/10.1016/j.enbuild.2011.02.005) (from background knowledge)
- In RC models, higher orders need more data and computation to identify. A 2nd-order model reportedly loses little accuracy compared with a 20th-order model (building context). — [arXiv:2009.05889, "Identifying Grey-box Thermal Models with Bayesian Neural Networks"](https://arxiv.org/pdf/2009.05889)
- A grey-box thermal model of a household wine cooler, identified with constrained nonlinear optimisation, reached normalized RMSE 0.132 and a mean deviation of 0.226 from theoretical parameter values. The authors explore the accuracy/interpretability trade-off. — [ingmec.ual.es (RBVM25)](https://ingmec.ual.es/ojs/index.php/RBVM25/article/download/87/62/379)
- **Cold storage, first-order plus delay:** a Brazilian agricultural cold-storage study modelled the dynamics as first-order systems with time delay, summing the effects of compressor activation frequency and thermal load. Errors were <0.11 °C for evaporator-inlet air and <0.09 °C at the chamber centre (real unit). — [SciELO, "A mathematical model for the cold storage of agricultural products"](https://scielo.br/j/rca/a/tF9s7krYB8Y8bL8Pc4qcbXK/?lang=en)
- **Two-zone air/product lumped model:** an older IIR paper models heat transfer between palletised product and fluctuating cold-store air. It agreed closely with finite-difference predictions for solid product, but needed empirical adjustment of heat-transfer parameters for vented apple cartons because airflow speeds up heat transfer. — [IIR FRIDOC, "Simple non-steady-state modelling of a refrigerated room..."](https://iifiir.org/en/fridoc/simple-non-steady-state-modelling-of-a-refrigerated-room-taking-account-9886)
- **Full time-stepping chilled-room model (FRPERC, UK):** walls, room air and food temperatures are solved at each time step. Mean difference from measured centre/surface food temperatures was <0.7 °C. — [Grimsby/FRPERC cold room model](https://grimsby.ac.uk/documents/frperc/projects/coldroom.pdf)
- **Product-node time constants:** an industry application note (Disruptive Technologies) fits Newton's law of cooling, dy/dt = −k(y − T_air), to items in a fridge after a 1-hour door-open step. Fitted k values were water 0.010, yogurt 0.015, oatmeal 0.025, apple 0.010, banana 0.016, meat 0.015, per sample step. The page labels the units inconsistently (W/m²K), and the authors warn the values should be re-identified per deployment. — [Disruptive Technologies application note](https://docs.developer.disruptive-technologies.com/other/application-notes/modeling-fridge-content-temperatures)
- A refrigerator control patent identifies separate transfer functions for each section of the operating cycle. For example, during compressor-off sections the input is outside air temperature and the output is compartment temperature. This is a practical way to identify cooling-on and cooling-off dynamics separately. — [US Patent 11085685](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11085685)
- **Vaccine fridge (WHO PQS) holdover time:** the time in hours during which all points in the vaccine compartment stay between +2 °C and +10 °C at the rated zone's maximum ambient after power is disconnected. — [WHO PQS E003/RF03.2](https://extranet.who.int/prequal/sites/default/files/document_files/PQS_Performance_E003_RF03.2.pdf)
- Example: one solar direct-drive vaccine fridge reports holdover of 3.9 days (94 h 11 min) at +43 °C, and a separately listed autonomy of 82 h 48 min under the WHO PQS protocol. — [WHO PQS E003-059 product sheet](https://extranet.who.int/prequal/sites/default/files/immunization_devices/pdf/e003/E003-059e.pdf)
- **Digital twins:**
  - Xi'an Jiaotong University: a digital twin of a cascade refrigeration system built on a semi-empirical compressor model whose parameters are updated online. It reports 7.42–23.62% better prediction accuracy than a simplified model and up to 13.1% energy saving in a food-factory case. — [XJTU faculty page](https://faculty.xjtu.edu.cn/chuangwang/zh_CN/article/510574/content/30011.htm)
  - Pearson & Clarke (IIR 2024): an AI-based refrigeration digital twin that flags anomalies against expected performance. The authors describe it as early-stage. — [IIR FRIDOC 148877](https://iifiir.org/fr/fridoc/construire-des-jumeaux-numeriques-pour-les-systemes-frigorifiques-a-148877)
  - A TU Delft thesis classifies industrial refrigeration twin models as physics-based, empirical or data-driven, and favours empirical models for accuracy/efficiency (only an excerpt was available). — [TU Delft repository](https://repository.tudelft.nl/file/File_949d5464-95ab-4984-9919-f0713214cd66)
  - Patent CN 121979328 A describes a CFD-based 3-D cold-store digital twin initialised from real-time temperatures, with incoming goods treated as a transient heat source. — [CN121979328A](https://www.goveda.com/patent/CN-121979328-A)

### Inferences
- For ThermoTwin, a 2R2C or 3R3C linear structure is a well-supported default. One version is air node + product/load node + envelope. Another is air node + evaporator node, with compressor power × COP as the cooling input, door-open as an infiltration conductance term, and ambient as a disturbance. The Sossan likelihood-ratio results show 1st order is too simple, while 4th order adds nothing.
- Rough consistency check (my calculation): R_ins ≈ 1.3 K/W × total C ≈ 1.55×10⁴ J/K gives about 2×10⁴ s, or about 5.6 h. This is the same order as the reported ~4 h slowest time constant. For an empty, closed freezer, the air node alone (~5×10² J/K) has a time constant of minutes. A loaded product node adds hours of thermal inertia. That is why air-temperature excursions from door openings can be brief while product temperature lags.
- Because ThermoTwin's training and test data are simulated, the simulator almost certainly uses an RC-type model. Identifying the same structure (online, e.g. with an EKF/UKF on augmented parameter states, or with recursive least squares on a discretised ARX form) should give strong in-distribution and out-of-distribution forecasts. It also gives physically interpretable parameters (UA, C, COP) that directly support cause diagnosis.
- Online parameter tracking doubles as fault diagnosis. Drift in identified UA suggests gasket/insulation degradation. Drift in effective COP or cooling capacity suggests refrigerant leak, condenser fouling or compressor wear. Increased infiltration conductance suggests door left ajar.

### Gaps
- I found no peer-reviewed paper with a published table of identified R/C values or time constants for a WHO-PQS vaccine refrigerator or a commercial walk-in cold room. Sossan's appendix with per-model parameter estimates was not extractable.
- I did not find refrigeration-specific papers using UKF or RLS for parameter identification in this session. Their use is standard in the building RC literature, but I could not cite a refrigerator example.
- No published lead-time-to-excursion numbers from RC models specifically.

## 2. Refrigeration fault detection and diagnosis (faults, signals/features, methods, datasets)

### Takeaway
Refrigeration FDD relies on a small set of physically meaningful features: compressor duty cycle and run time, cycle period, pull-down rate, discharge/suction temperatures and pressures, superheat, evaporator air ΔT, and power. Tree ensembles and SVM-based classifiers routinely report >99% accuracy on lab chiller data (ASHRAE RP-1043). These numbers are inflated by steady-state lab conditions and do not transfer well to mild-severity or field faults. For refrigerated cases and fridges, the best open fault dataset is Sun et al. (ORNL, Scientific Data 2021). A new synthetic 27-fridge degradation dataset (Benamirouche et al., arXiv Sept 2026) is a close analogue to ThermoTwin's simulated setup.

### Cited Findings
- **Duty cycle as the core fault signal (fridges):**
  - Gas leakage in a refrigerator leads to longer compressor operation, i.e. a higher duty cycle. Normal duty cycle varies by time of day (low 2–5 a.m.) and by season, so baselines must be context-aware. — [US12066481B2](https://patents.google.com/patent/US12066481)
  - A gradual upward drift in compressor activation time at constant room temperature indicates reduced efficiency, probably from refrigerant leakage or evaporator ice buildup. — [US Patent 7423546](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7423546)
  - For inverter compressors, faults in the compressor, condenser fan or evaporator fan can be identified from compressor frequency vs time. — [US10208993B2](https://patents.google.com/patent/US10208993)
  - Controllers may deliberately extend compressor run time, and defrost cycles add spikes. Naive duty-cycle detectors can therefore false-alarm. — [Sense community forum](https://community.sense.com/t/fridge-freezer-failure-analysis-notifications/10404) (anecdotal)
- **Heuristic, physics-based decision tree:** Senger, Silveira, Ronzoni & Hermes built a COP-based decision tree for single-door refrigerating appliances covering condenser fouling, evaporator frosting, refrigerant leakage and non-condensable gas. It was tested on an instrumented ice-cream display cabinet. — [IIR FRIDOC 149347](https://iifiir.org/fr/fridoc/arbre-de-decision-base-sur-le-coefficient-de-performance-pour-la-149347)
- **Refrigerant leak detection:**
  - Mtibaa et al., Int. J. Refrigeration 2024: predicts the fault-free receiver liquid level with ML and compares it to the measured level (a residual approach). Validated on real industrial installations. — [HAL hal-04633258](https://hal-bioemco.ccsd.cnrs.fr/CMA/hal-04633258v1)
  - Energies 2024: a CatBoost (categorical gradient boosting) framework for slow and catastrophic leaks in supermarket refrigeration. — [DOAJ, Energies Feb 2024](https://doaj.org/article/13bb1c0752fe4568aabe1172ac28448f)
- **Condenser fouling:** Lee & Kim (Energy Reports 2024) combined virtual sensors with deep learning to detect and isolate condenser fouling in VRF systems and to estimate performance degradation. — [DOAJ, Energy Reports Jun 2024](https://doaj.org/article/038f7fd81259417b9be7f1b3d2a8efba)
- **Multi-class fault classification:** Ebrahimifakhar, Yuill & Kabirikopaei treat rooftop-unit FDD as multi-class classification (undercharge/overcharge, condenser fouling, liquid-line restriction, non-condensables). — [IIR FRIDOC 143690](https://iifiir.org/fr/fridoc/application-de-methodes-de-classification-par-apprentissage-143690)
- **ASHRAE RP-1043 chiller dataset:**
  - McQuay 90-ton (316 kW) centrifugal chiller. Seven faults: reduced condenser water flow, reduced evaporator water flow, refrigerant leak, refrigerant overcharge, excess oil, condenser fouling (tubes plugged), non-condensables (nitrogen added). Four severity levels each; for example, condenser-water-flow fault SL1 = −10%, SL4 = −40%. 27 operating conditions. 65 features sampled every 10 s, including transients. — [arXiv:2011.00187](https://arxiv.org/pdf/2011.00187)
  - Not public; available for purchase from ASHRAE. Many studies use only six faults, dropping excess oil. — [arXiv:2011.00187](https://arxiv.org/pdf/2011.00187)
  - Original report: Comstock, M.C., Braun, J.E. & Bernhard, R. (1999), ASHRAE RP-1043 "Development of analysis tools for the evaluation of fault detection and diagnostics in chillers", Purdue/Ray W. Herrick Labs. (From background knowledge; the author link was not confirmed by search results this session.)
  - Reported accuracies: RF feature selection + SVM, 99.98% overall on RP-1043, with diagnosis time about 50% shorter than SVM alone. — [MDPI Actuators 12(6):242](https://www.mdpi.com/2076-0825/12/6/242/htm). A support vector data description approach outperformed multi-class SVM and PCA-based detection. — [Frontiers Energy Res. 2021, 10.3389/fenrg.2021.755649](https://www.frontiersin.org/articles/10.3389/fenrg.2021.755649/pdf). An LSSVM–AdaBoost model claims advantages for early-stage faults. — [PLOS ONE 2025 (RePEc)](https://ideas.repec.org/a/plo/pone00/0320563.html). An eight-method comparison is in [LAPSE 2023.30598](https://psecommunity.org/wp-content/plugins/wpor/includes/file/2304/LAPSE-2023.30598-1v1.pdf).
  - Work on RP-1043 shows that classifiers struggle with intermediate/low-severity faults and with domain shift between operating conditions (stratification-aware cross-validation, out-of-distribution faults). — [arXiv:2007.03167](https://arxiv.org/pdf/2007.03167); [arXiv:2008.08713](https://arxiv.org/pdf/2008.08713); [arXiv:1909.04202](https://arxiv.org/pdf/1909.04202)
- **Refrigerated display case fault dataset (open):** Sun, Im, Bae, Munk, Kuruganti, Fricke (2021), "Dataset of low global warming potential refrigerant refrigeration system for fault detection and diagnostics", Scientific Data 8:144. — [DOI 10.1038/s41597-021-00927-6](https://doi.org/10.1038/s41597-021-00927-6) / [PMC8159987](https://pmc.ncbi.nlm.nih.gov/articles/PMC8159987/)
  - Lab transcritical CO₂ rack with one medium-temperature (MT) and one low-temperature (LT) display case.
  - Six faults with severities: LT case door open 5/10/15% of the time; LT evaporator ice accumulation mild/moderate/severe; LT expansion valve partially/fully closed; MT evaporator fan failure 25/50/75%; condenser air-path blockage 25/50/75%; MT evaporator air-path blockage 25/50/75%.
  - 1 s logging (3 s for the icing file). Variables include suction/discharge temperatures and pressures, supply/return air temperatures, superheat, and fan and compressor power.
  - Data on figshare ([10.6084/m9.figshare.13232627](https://doi.org/10.6084/m9.figshare.13232627)). The article is CC BY 4.0 and the metadata CC0. No separate data licence was stated.
  - A baseline-file inconsistency exists in Table 4 (BaselineTestA.csv listed for both Fault 1 and Fault 6).
- **Synthetic fridge predictive-maintenance dataset:** Benamirouche, Fass & Ziou, "A Synthetic Multivariate Refrigerator Time-Series Dataset for Predictive Maintenance", arXiv:2609.22229 (3 Sep 2026). 27 refrigerators with 15–20 sensors each; 7,066,161 rows at 1-minute resolution plus 27 failure logs; six progressive degradation types. A "simplified physics-inspired simulator" covers ambient variation, door use, thermostat/compressor, heat exchange, defrost and electrical consumption. The Python generator is included. The arXiv page shows CC BY 4.0 (for the paper). In the nominal 48 h window the compressor is on 21.0% of the time. — [arXiv:2609.22229](https://arxiv.org/abs/2609.22229); duty-cycle figure via [search summary of PDF](https://arxiv.org/pdf/2609.22229)
- Vibration-based detection of simulated refrigerant leakage in refrigeration chambers was presented at LATAM-SHM 2026 (abstract only). — [LATAM-SHM 2026](https://latam-shm2026.cimne.com/event/contribution/b7e2c151-56ed-11f0-87b6-000c29ddfc0c)

### Inferences
- A compact, explainable feature set for ThermoTwin's cause module, with the physical signature of each fault:
  - Compressor duty cycle over rolling windows, normalised by ambient and time-of-day
  - Mean ON/OFF durations and cycle period
  - Pull-down rate after compressor start (°C/min)
  - Warm-up rate during OFF periods
  - Steady-state ON-temperature floor
  - Door-event count and duration
  - Defrost flag
  - Residual between measured temperature and the RC-twin prediction

  Expected signatures:
  - **Leak or compressor wear:** slower pull-down and higher duty cycle at the same ambient.
  - **Gasket leak or door ajar:** faster warm-up during OFF periods, i.e. higher effective UA.
  - **Evaporator icing:** slowly degrading pull-down that resets after defrost.
  - **Condenser fouling:** higher duty cycle that worsens with ambient temperature.
  - **Fan failure:** abrupt change in air-temperature response and stratification.
- Gradient-boosted trees on these features are a strong, explainable baseline (SHAP or feature importance maps directly to physical causes). The RP-1043 >99% results should not be taken as indicative of field or hidden-test performance, particularly at low severity.

### Gaps
- No open, real-world labelled household-fridge or vaccine-fridge fault dataset was found. Sun et al. is a lab rig, and Benamirouche et al. is synthetic.
- I could not retrieve per-severity accuracy tables comparing PCA vs SVM vs RF on RP-1043.
- No peer-reviewed field-validation numbers for duty-cycle-based household fridge FDD; the evidence is mostly patents.

## 3. Time-series forecasting and early warning for temperature excursions (models, lead times, accuracy)

### Takeaway
Peer-reviewed work that forecasts cold-chain or fridge excursions with explicit lead times and alarm-level metrics is very thin. Most published work either detects anomalies after the fact or forecasts temperature in buildings or transport. For buildings, PatchTST-style Transformers lead multi-week horizons, while tree models and persistence are competitive at short horizons. Simple linear models are a necessary baseline because they often match Transformers. No paper found reports 15–60-minute excursion lead times for refrigerators.

### Cited Findings
- **Vaccine-fridge deep learning on the edge:** Harrabi, Hamdi, Ouni & Bel Hadj Tahar (2024), "Real-time temperature anomaly detection in vaccine refrigeration systems using deep learning on a resource-constrained microcontroller", Frontiers in AI 7:1429602. Semi-supervised convolutional autoencoder on an ESP32, trained on real equipment data. Reports 92% accuracy at identifying temperature faults, 0.05 W power and 1.2 MB memory. This is detection, not ahead-of-time forecasting. — [DOI 10.3389/frai.2024.1429602](https://doi.org/10.3389/frai.2024.1429602) / [PMC11324578](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11324578/)
- **Agricultural cold chain LSTM + XGBoost ensemble (PeerJ CS 2024):** predicts loading-environment temperature for a future window. Reported MAE 2.5343 (horizon and units not confirmed from the excerpt). The combined model beat the individual models. — [PeerJ cs-2510](https://peerj.com/articles/cs-2510.pdf)
- **LSTM forecasting for a vaccine packaging room (ITS undergraduate project):** temperature/humidity/pressure on a Raspberry Pi 4 with a BME280, InfluxDB and Grafana, aimed at early warning. Not peer-reviewed. — [ITS repository](https://repository.its.ac.id/115525/)
- **Display cabinet load forecasting:** a CEEMD–IPSO–LSTM hybrid reached R² = 0.9105 for refrigerated display cabinet electrical load, not temperature. — [Open Physics 2021, 10.1515/phys-2021-0043](https://www.degruyterbrill.com/document/doi/10.1515/phys-2021-0043/html)
- **Tree ensembles on display cases:** LightGBM and RF were the most effective of six models for predicting evaporator heat transfer in modular display cases. — [Energies 17(23):6189, 2024](https://ideas.repec.org/a/gam/jeners/v17y2024i23p6189-d1539206.html)
- **Building indoor temperature (closest analogue):**
  - NeurIPS 2025 workshop paper on the Smart Buildings Control Suite compared spline regression, XGBoost, encoder–decoder LSTM, PatchTST and Time-LLM. Classical baselines capture short-term dynamics but degrade over multi-week windows. A modified PatchTST reached MAE 1.76 °F on two-week forecasts. — [NeurIPS 2025 virtual page](https://neurips.cc/virtual/2025/136646)
  - Global Transformer for 133 rooms, built as a residual on top of persistence and compared with LSTM. — [arXiv:2310.20476](https://arxiv.org/pdf/2310.20476)
  - RESCAST-100K (2026) benchmarks LSTM, Transformer, TimeXer, TSMixer and PatchTST for residential load and indoor temperature (384-step context, 96-step horizon at 15 min). — [arXiv:2606.02852](https://arxiv.org/pdf/2606.02852)
- A patent application argues plain LSTMs lag during door-opening disturbances and ambient swings and struggle with multi-scale temperature changes (not peer-reviewed). — [CN122508969A](https://eureka.patsnap.com/patent/CN122508969A)
- **Architecture references (from background knowledge; identifiers given):**
  - PatchTST: Nie et al., ICLR 2023 — [arXiv:2211.14730](https://arxiv.org/abs/2211.14730)
  - Informer: Zhou et al., AAAI 2021 — [arXiv:2012.07436](https://arxiv.org/abs/2012.07436)
  - TCN: Bai, Kolter & Koltun 2018 — [arXiv:1803.01271](https://arxiv.org/abs/1803.01271)
  - DLinear, "Are Transformers Effective for Time Series Forecasting?" (Zeng et al., AAAI 2023), shows simple linear models beat many Transformer variants on long-horizon benchmarks — [arXiv:2205.13504](https://arxiv.org/abs/2205.13504)
- **Survival / time-to-event framing:**
  - Yèche, Burger, Veshchezerova & Rätsch (2024), "Dynamic Survival Analysis for Early Event Prediction". Multivariate time series with binary event labels; a hazard / cumulative-failure estimator followed by a threshold-based alarm policy. — [arXiv:2403.12818](https://arxiv.org/abs/2403.12818)
  - Background: Chen, deep survival analysis tutorial — [arXiv:2410.01086](https://arxiv.org/abs/2410.01086). DL survival review — [arXiv:2305.14961](https://arxiv.org/abs/2305.14961)
- **Monitoring frequency matters:** a CDC-related simulation found that twice-daily current-temperature readings without min/max detected only 4.8–6.4% of excursions. — [CDC Stacks 119983](https://stacks.cdc.gov/view/cdc/119983/cdc_119983_DS1.pdf)
- **Non-ML alternative:** kinetic modelling of vaccine degradation from a few months of forced-degradation data can predict the impact of short excursions with high accuracy. — [TechNet-21 summary](https://www.technet-21.org/en/resources/journal-article/accurate-prediction-of-vaccine-stability-under-real-storage-conditions-and-during-temperature-excursions)
- **Strawberry cold-chain shipments** (6 shipments, 5–10 min sampling, location-aware) are used in the food-engineering literature for shelf-life/temperature analysis. — [arXiv:2103.12895](https://arxiv.org/abs/2103.12895)

### Inferences
- For a 15–60 min horizon at roughly 1-minute resolution, there are two candidate framings:
  - **(a) Direct classification:** "will T exceed 8 °C within h minutes?" with LightGBM on engineered features: current temperature, slopes, time since compressor ON/OFF, door state, duty cycle, RC-twin forecast and residual.
  - **(b) Forecast-then-threshold:** a quantile forecaster (RC twin + LightGBM residual, or a small PatchTST/TCN) with an exceedance probability from the predictive distribution.

  Both are well supported methodologically. (a) is typically easier to calibrate and directly optimises the alert target. A discrete-time hazard model (one LightGBM per horizon bin, or a single model with horizon as a feature) unifies both and yields a time-to-excursion estimate.
- Given the DLinear and NeurIPS 2025 findings, a hackathon team should benchmark simple baselines (persistence, RC twin, linear/LightGBM) before any Transformer. At a 15–60 min horizon, short-term dynamics dominate, which favours tree and physics models.

### Gaps
- No peer-reviewed paper found reporting excursion lead time (minutes), alert precision or false-alarm rate for refrigerator or vaccine-fridge excursion forecasting.
- No paper found applying survival models specifically to cold-chain excursions.
- Head-to-head LightGBM vs LSTM vs PatchTST at sub-hour horizons on refrigeration temperature data was not found.

## 4. Anomaly detection on cold-chain sensor data (isolation forest, autoencoders) and its weaknesses

### Takeaway
On small, real cold-chain datasets, Isolation Forest often beats deep models but still misses many anomalies (F1 about 0.5). Unsupervised detectors confuse normal door-open and defrost events with faults. The TSAD literature shows that many benchmark gains are artefacts of flawed datasets and lenient metrics such as point-adjust.

### Cited Findings
- Pharmaceutical cold chain IoT study: about 8,640 readings (5-min, 30 days). Isolation Forest beat Autoencoder, LSTM and LSTM-Attention with precision 0.686, recall 0.418, F1 0.520, and was also the fastest. The deep models' weaker results were attributed to limited data. — [Jurnal Teknologi dan Manajemen Informatika (2026)](https://jurnal.unmer.ac.id/index.php/jtmi/article/view/17062)
- Cold-chain logistics stream: a modified iForest with subsampling and cross-factor features reached average F1 0.8639 and AUC 0.9064. — [PMC11892858](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11892858/)
- Known iForest weaknesses: misses anomalies in non-axis-aligned or non-linearly separable regions, and has "ghost region" artefacts with misleadingly low scores. — [Deep Isolation Forest, arXiv:2206.06602](https://arxiv.org/pdf/2206.06602)
- Door/defrost confounding: a significant rise in temperature between normal compressor cycles indicates either a door opening or a defrost cycle. Commercial monitors respond by lengthening the alarm delay, e.g. from 30 to 60–90 minutes. — [US10989464](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10989464); [US11725877](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11725877)
- Wu & Keogh: the popular Yahoo, Numenta and NASA benchmarks suffer from triviality, unrealistic anomaly density, mislabeled ground truth and run-to-failure bias. They propose the UCR Anomaly Archive. — [arXiv:2009.13807](https://arxiv.org/abs/2009.13807)
- HPI comprehensive TSAD evaluation: 71 algorithms on 967 datasets. — [HPI Potsdam](https://www.hpi.uni-potsdam.de/naumann/s/time-series-anomaly-detection-evaluation.html)
- Kim et al. (AAAI 2022), "Towards a Rigorous Evaluation of Time-series Anomaly Detection": the point-adjust protocol inflates F1 so much that random anomaly scores can appear state-of-the-art. — [arXiv:2109.05257](https://arxiv.org/abs/2109.05257) (from background knowledge)
- Hundman et al. (KDD 2018): LSTM forecasting with nonparametric dynamic thresholding, designed to control false positives on spacecraft telemetry. — [arXiv:1802.04431](https://arxiv.org/abs/1802.04431) (from background knowledge)
- An ESP32-S3 vaccine-fridge design (compressor-fault detection, gas-based detection of non-vaccine items, exposure tracking) was validated only in simulation. — [engrXiv preprint 8149](https://engrxiv.org/preprint/download/8149/13236/11477)

### Inferences
- For ThermoTwin, an unsupervised detector should not be the primary alarm source. Use it as a secondary "novelty" signal on residuals from the RC twin (residual-based anomaly detection), with explicit masking of known door and defrost events. This addresses the main false-alarm driver.
- Evaluate with event-level metrics (Section 7), not point-adjusted F1.

### Gaps
- No published study separately quantifies false positives caused by door-open vs defrost events in cold-chain anomaly detection.

## 5. Physics-informed ML / hybrid models for building or refrigeration thermal dynamics; out-of-distribution evidence

### Takeaway
Residual learning on top of an RC model is the best-evidenced hybrid. It improves accuracy (one study roughly halved MAE vs RC-only) and is the hybrid most likely to stay physically sensible out of distribution. Physically consistent NN architectures offer guaranteed physical monotonicity by design. Evidence is mostly from buildings, with limited real-world OOD tests.

### Cited Findings
- EPFL (2025): compared five hybrid approaches for probabilistic (quantile) indoor-temperature modelling in a real case study. Residual learning with a feedforward NN performed best on average. It was the only model producing physically intuitive predictions on out-of-distribution test data. Quantile conformal prediction calibrated the quantiles effectively. — [arXiv:2507.17526](https://arxiv.org/abs/2507.17526v1)
- CESI LINEACT: 4R3C RC model + MLP (MLP identifies parameters and predicts temperature/loads). Hybrid MAE 0.454 °C / RMSE 0.547 °C vs physics-only 0.851 °C / 0.974 °C (in-distribution only). — [CESI LINEACT](https://lineact.cesi.fr/en/?p=194063)
- Physically Consistent Neural Networks (Di Natale et al.): prior knowledge is embedded in the network structure so predictions respect physical laws by design, even on unseen data. — [arXiv:2112.03212](https://www.arxiv.org/pdf/2112.03212)
- Bayesian neural networks used to identify grey-box thermal models. — [arXiv:2009.05889](https://arxiv.org/pdf/2009.05889)
- Drgoňa et al. (2021), "Physics-constrained deep learning of multi-zone building thermal dynamics", Energy and Buildings: structured state-space neural models with physics constraints. — [arXiv:2011.05987](https://arxiv.org/abs/2011.05987) (from background knowledge)
- Refrigeration twin with online-updated semi-empirical compressor model: 7.42–23.62% accuracy improvement over a simplified model. — [XJTU](https://faculty.xjtu.edu.cn/chuangwang/zh_CN/article/510574/content/30011.htm)
- Physics-informed LSTM with RC thermal constraint (motor windings; GitHub README, not peer-reviewed). — [ThermoPINN](https://github.com/pascme05/ThermoPINN)
- In the freezer study, the nonlinear physics model (Carnot-COP) gave the best open-loop prediction but behaved poorly inside MPC. The linear 3R3C was the most robust choice for control. — [arXiv:1510.06855](https://ar5iv.labs.arxiv.org/html/1510.06855)

### Inferences
- The recommended ThermoTwin design is: RC twin (identified per unit), then a LightGBM or small MLP on the residual and on exceedance-event targets, then calibration. This should be the most robust approach to a hidden synthetic test set whose distribution may shift (different ambient, loading or fault severities). It also yields interpretable causes from parameter drift.
- A full PINN is probably unnecessary for a hackathon. A differentiable RC model with learned parameters, fitted by gradient descent in PyTorch, gives most of the benefit.

### Gaps
- No refrigeration-specific paper found that quantitatively compares hybrid vs pure-ML OOD generalisation (e.g. train at 25 °C ambient, test at 35 °C).

## 6. Time-series foundation models (Chronos, TimesFM, Moirai, Lag-Llama, TimeGPT) for zero-shot temperature forecasting on edge

### Takeaway
Chronos-Bolt is the most edge-friendly TSFM (lowest energy and latency, small variants available). TimesFM is accurate but heavier, and Moirai-MoE is energy-hungry. TimeGPT is API-only. None is trained for exogenous-driven thermostat dynamics (door, compressor state), so zero-shot use is a useful baseline, not a replacement for a fitted RC/GBM model.

### Cited Findings
- Zero-shot on the 25-dataset Chronos benchmark, aggregate relative MASE (lower is better): Chronos-Bolt-Base (205M params) 0.791; Moirai-Base (311M) 0.812; TimesFM (200M) 0.879; Chronos-T5-Small (46M) 0.830. — [arXiv:2605.07222 (table summarised via search)](https://arxiv.org/pdf/2605.07222)
- Chronos-Bolt comes in tiny/mini/small/base. Moirai 1.1 comes in small/base/large. TimesFM 1.0 is 200M and 2.0 is 500M. — [arXiv:2509.04208](https://arxiv.org/pdf/2509.04208)
- Energy/latency benchmark (context 512, horizon 64): efficiency is mainly architecture-driven. Chronos-Bolt had consistently low energy and latency; TimesFM had the best MeteoSwiss accuracy at low energy; Moirai-MoE used substantially more energy for similar error. — [PMLR v309, Guibert et al. 2026](https://proceedings.mlr.press/v309/guibert26a.html)
- GIFT-Eval flags TimesFM v1 for self-declared test-data leakage. TimesFM-2.5 carries no flag. — [arXiv:2605.07222](https://arxiv.org/pdf/2605.07222)
- In an open-world living benchmark, results were mixed across domains. TimesFM-2.5 and Chronos-2 were stronger on several series than Chronos-Bolt. — [LiveHouse-TS, arXiv:2608.17299](https://arxiv.org/pdf/2608.17299)
- Primary papers (from background knowledge):
  - Chronos — Ansari et al., TMLR 2024, [arXiv:2403.07815](https://arxiv.org/abs/2403.07815)
  - TimesFM — Das et al., ICML 2024, [arXiv:2310.10688](https://arxiv.org/abs/2310.10688)
  - Moirai — Woo et al., ICML 2024, [arXiv:2402.02592](https://arxiv.org/abs/2402.02592)
  - Lag-Llama — Rasul et al., [arXiv:2310.08278](https://arxiv.org/abs/2310.08278)
  - TimeGPT-1 — Garza & Mergenthaler-Canseco, [arXiv:2310.03589](https://arxiv.org/abs/2310.03589); served via Nixtla's hosted API rather than as open weights

### Inferences
- On an edge gateway (Raspberry Pi class), Chronos-Bolt tiny/mini is plausible for a zero-shot baseline. On a microcontroller (ESP32 class), TSFMs are not feasible. Harrabi et al. show 1.2 MB-class convolutional autoencoders are the realistic ceiling there.
- Thermostatic sawtooth signals with exogenous door/compressor events are poorly suited to univariate zero-shot forecasting. Expect TSFMs to track the cycle pattern but miss door-driven excursions unless covariates are supported (Chronos-2 and Moirai support covariates, per their releases; not verified this session).

### Gaps
- No on-device (CPU-only or ARM) memory or latency measurements for TSFMs were found.
- No study applying TSFMs to refrigerator or cold-chain temperature was found.
- Exact parameter counts for Chronos-Bolt tiny/mini were not verified this session.

## 7. Probability calibration, conformal prediction for time series, and event-based early-warning metrics

### Takeaway
Use Platt or isotonic calibration on held-out data for the excursion classifier. Use adaptive conformal inference (ACI/AgACI) or EnbPI for forecast intervals under drift. Score alerts at the event level (lead time, false alarms per day, alert precision) using NAB-style windows or Tatbul range-based precision/recall rather than point-wise F1.

### Cited Findings
- **Calibration (from background knowledge):**
  - Platt scaling: Platt, J. (1999), "Probabilistic outputs for support vector machines..." in Advances in Large Margin Classifiers.
  - Isotonic: Zadrozny & Elkan (2002), KDD — [DOI 10.1145/775047.775151](https://doi.org/10.1145/775047.775151)
  - Niculescu-Mizil & Caruana (2005), "Predicting good probabilities with supervised learning", ICML. Found boosted trees and SVMs produce distorted probabilities; Platt works better with little calibration data, isotonic with more. — [DOI 10.1145/1102351.1102430](https://doi.org/10.1145/1102351.1102430)
- **Conformal for time series:**
  - Gibbs & Candès, "Adaptive Conformal Inference Under Distribution Shift" (NeurIPS 2021). Wraps any point or quantile forecaster and keeps long-run coverage without exchangeability by adapting one parameter online. — [arXiv:2106.00170](https://arxiv.org/abs/2106.00170v3); [NeurIPS 2021](https://neurips.cc/virtual/2021/oral/28041)
  - Xu & Xie, "Conformal Prediction for Time Series" (EnbPI). Ensemble-based, no data splitting or retraining, with bounds on conditional and marginal coverage gaps. — [arXiv:2010.09107](https://ar5iv.labs.arxiv.org/html/2010.09107)
  - Zaffran et al. (ICML 2022), AgACI: a parameter-free aggregation of ACI learning rates. — [ICML 2022](https://icml.cc/virtual/2022/spotlight/17818)
  - Susmann, Chambaz & Josse: survey plus R package AdaptiveConformal. — [Computo 2024](https://computo.sfds.asso.fr/published-202407-susmann-adaptive-conformal/published-202407-susmann-adaptive-conformal.pdf)
  - Quantile conformal prediction calibrated indoor-temperature quantiles well in the EPFL hybrid study. — [arXiv:2507.17526](https://arxiv.org/abs/2507.17526v1)
- **NAB scoring (Lavin & Ahmad 2015):**
  - Anomaly windows centred on labelled anomalies, default total window size 10% of the file length.
  - Only the earliest detection in a window counts, weighted by a sigmoid that rewards earlier detection.
  - FPs outside windows are penalised, less if close to a window. Missed windows count as FN.
  - Unscored probationary period (first 15%).
  - Application profiles reweight TP, FP and FN (standard, reward-low-FP, reward-low-FN).
  - Sources: [Domino blog summary](https://blog.dominodatalab.com/numenta-anomaly-benchmark); [arXiv:2105.12818](https://arxiv.org/pdf/2105.12818); original paper [arXiv:1510.03336](https://arxiv.org/abs/1510.03336) (from background knowledge)
- **Tatbul et al. (NeurIPS 2018), "Precision and Recall for Time Series":** generalises precision and recall to ranges with tunable existence reward, overlap size, positional bias (e.g. front-end bias to reward early detection) and cardinality. Classical P/R is a special case. — [NeurIPS proceedings](https://proceedings.neurips.cc/paper/2018/hash/8f468c873a32bb0619eaeb2050ba45d1-Abstract.html); [arXiv:1803.03639](https://arxiv.org/abs/1803.03639)
- Taxonomy of TSAD evaluation metrics (2025). — [arXiv:2511.18739](https://arxiv.org/pdf/2511.18739)
- Point-adjust inflation of F1. — [Kim et al., arXiv:2109.05257](https://arxiv.org/abs/2109.05257) (from background knowledge)
- Dynamic survival alarm policy: thresholding a hazard/CDF estimate to trade off alarm rate against earliness, evaluated with event-level recall at fixed alarm precision. — [Yèche et al., arXiv:2403.12818](https://arxiv.org/abs/2403.12818)

### Inferences
- Suggested ThermoTwin scorecard:
  - **Event recall:** fraction of excursions with at least one alert 15–60 min before onset.
  - **Median and P10 lead time.**
  - **Alert precision:** fraction of alert episodes followed by an excursion within 60 min.
  - **False alerts per unit-day.**
  - **Brier score / reliability diagram** for the probabilities.
  - **Range-based P/R** with front-end bias.

  Merge consecutive alert points into one alert episode (with a refractory period) before counting false alarms. Otherwise the false-alarm rate is inflated by duplicated alerts.
- Choose the alert threshold to meet a target false-alarm budget (e.g. at most 1 false alert per unit per week) on a validation set, then use ACI-style online adjustment if the base rate drifts.

### Gaps
- No refrigeration-specific benchmark using NAB or Tatbul metrics was found.

## 8. Mean kinetic temperature (MKT), USP/ICH references, Arrhenius budgets, WHO VVM categories

### Takeaway
MKT uses the Arrhenius-weighted mean of absolute temperatures with default ΔH = 83.144 kJ/mol (so ΔH/R = 10,000 K). USP <1079.2> sets cold-chain (2–8 °C) limits: excursions 8–15 °C, at most 24 h, and MKT not more than 8 °C over 24 h. The WHO VVM categories are VVM30 (30 d at 37 °C / 193 d at 25 °C), VVM14 (14 / 90), VVM7 (7 / 45) and VVM2 (2 d at 37 °C, 225 d at 5 °C, no 25 °C point).

### Cited Findings
- **MKT formula (USP <1079.2>):**

  T_K = (ΔH/R) / ( −ln[ (e^(−ΔH/(R·T₁)) + e^(−ΔH/(R·T₂)) + … + e^(−ΔH/(R·Tₙ))) / n ] )

  T in kelvin; n = number of equally spaced readings; ΔH = 83.144 kJ/mol default "unless more accurate information is available from experimental studies"; R = 8.3144×10⁻³ kJ·mol⁻¹·K⁻¹. MKT is not an arithmetic mean. Seevers et al. found the choice of ΔH does not change MKT significantly. — [USP "MKT in the Evaluation of Temperature Excursions..." (USP 2025 text, mirror)](https://trungtamthuoc.com/usp-en/mean-kinetic-temperature-in-the-evaluation-of-temperature-excursions-during-storage-and-transportation-of-drug-products); [Vaisala blog on default ΔH](https://www.vaisala.com/en/blog/2020-02/common-questions-mkt-answered-trending-interpreting-reports-default-activation-energy)
  - Note: the mirror rendered the equation as an image. The formula above is the standard form, consistent with the variable definitions given there.
- ΔH/R = 83.144 / 0.0083144 = 10,000 K. The value was chosen historically for ease of manual calculation. Worked example: 44 h at 20 °C + 4 h at 30 °C gives MKT ≈ 21.5 °C vs arithmetic mean ≈ 20.7 °C. MKT is always at or above the arithmetic mean. — [Vaisala](https://www.vaisala.com/en/blog/2020-02/common-questions-mkt-answered-trending-interpreting-reports-default-activation-energy); [LogTag Analyzer help](https://help.logtagrecorders.com/LTA3/Topics/UserGuide/Chapter2-Using_Analyzer/Mean_Kinetic_Temperature.htm)
- **USP <1079.2> Table 1:**

  | | Storage | Acceptable excursion | Max temp | Max excursion time | MKT (NMT) | MKT period |
  |---|---|---|---|---|---|---|
  | Controlled room temperature (CRT) | 20–25 °C | 15–30 °C | 40 °C | 24 h | 25 °C | 30 days |
  | Controlled cold temperature (CCT) | 2–8 °C | 8–15 °C | 15 °C | 24 h | 8 °C | 24 h, counted from and including the high excursion |

  "MKT should not be used to justify a system out of control." Each excursion is a separate event, and degradation is irreversible. Example monitoring interval 15 min. — [USP mirror](https://trungtamthuoc.com/usp-en/mean-kinetic-temperature-in-the-evaluation-of-temperature-excursions-during-storage-and-transportation-of-drug-products)
  - The mirror's text did not explicitly display the chapter number "<1079.2>". It appears in USP 48–NF 43 and cross-references <659>, <1079> and <1079.3>.
- **WHO PQS vaccine-refrigerator day/night test:** the calculated MKT must remain within +2 °C to +8 °C with default activation energy 83.144 kJ/mol over the 5-day test. Short excursions up to +20 °C are tolerated, never reaching 0 °C. — [WHO PQS E003 docs (search summary)](https://extranet.who.int/prequal/sites/default/files/document_files/PQS_Performance_E003_RF03.2.pdf)
- **ICH Q1A(R2)** defines MKT in its glossary as a single derived temperature that gives the same thermal challenge as the actual fluctuating profile. — [ICH Q1A(R2) Guideline PDF](https://database.ich.org/sites/default/files/Q1A%28R2%29%20Guideline.pdf) (from background knowledge)
- **Origin of MKT:** Haynes, J.D. (1971), "Worldwide virtual temperatures for product stability testing", J. Pharm. Sci. 60(6):927–929. — [DOI 10.1002/jps.2600600622](https://doi.org/10.1002/jps.2600600622) (from background knowledge)
- **WHO VVM categories** (days to end point; the number in the name is the upper limit in days at 37 °C for ≥95% of VVMs):

  | Category | 37 °C | 25 °C | 5 °C |
  |---|---|---|---|
  | VVM30 (high stability) | 30 d | 193 d | >4 years |
  | VVM14 (medium) | 14 d | 90 d | >3 years |
  | VVM7 (moderate) | 7 d | 45 d | >2 years |
  | VVM2 (least stable; OPV) | 2 d | no 25 °C point | 225 d (critical temperatures 37 °C and 5 °C) |

  End point = active square matches the reference circle. — [DCVMN "Choice of VVM category"](https://dcvmn.org/wp-content/uploads/2018/12/choice-of-vvm-category.pdf); [Pitt VVM summary](https://sites.pitt.edu/~super1/Pirzado/Vaccine%20Vial%20Monitor.pdf); spec WHO/PQS/E06/IN05 and testing protocol [E006/IN05-VP.2](https://extranet.who.int/prequal/key-resources/documents/pqs-independent-type-testing-protocol-e006in05-vp2-vaccine-vial-monitor)

### Inferences
- **Arrhenius budget (my calculation, not from a source):** the 37 °C / 25 °C ratio is 193/30 = 90/14 = 45/7 ≈ 6.43 for VVM30, VVM14 and VVM7. That implies a common apparent activation energy Ea ≈ R·ln(6.43)/(1/298.15 − 1/310.15) ≈ 119 kJ/mol, higher than the USP 83.144 default.
  - A ThermoTwin "stability budget" can accumulate consumed life as Σ Δtᵢ / t_end(Tᵢ), with t_end(T) = t_end(37 °C)·exp[(Ea/R)(1/T − 1/310.15)].
  - Using Ea ≈ 119 kJ/mol reproduces the VVM 25 °C end points.
  - Using 83.144 kJ/mol would be conservative for long exposures at low temperature and optimistic at high temperature. Report both and flag the assumption.
- For real-time display, use rolling MKT over 24 h for 2–8 °C products (per the USP CCT row) and cumulative VVM-equivalent life consumed.

### Gaps
- I could not open the official USP <1079.2> or WHO E06/IN05.4 text directly (paywalled or only via mirrors). Verify the table values against the current official versions.
- The VVM2 25 °C value is not defined; VVM2 at 37 °C = 2 days is implied by the naming convention stated in the sources.

## 9. Public datasets usable for this project (with licence notes)

### Takeaway
There is no large, open, labelled refrigerator-excursion dataset. The most useful are:
- Sun et al. 2021 (ORNL display-case fault data, figshare)
- Benamirouche et al. 2026 (synthetic 27-fridge degradation data with generator)
- REFIT/UK-DALE fridge power traces for compressor-cycle realism
- a Bangkok household fridge temperature dataset (123 homes, 5-min)

Licences must be verified on each landing page.

### Cited Findings
- **Sun et al. 2021, ORNL display-case FDD (lab, real):** 6 faults × 3 severities, 1 s data. figshare [10.6084/m9.figshare.13232627](https://doi.org/10.6084/m9.figshare.13232627). The article is CC BY 4.0 and the metadata CC0; data-file licence not stated in the article. — [PMC8159987](https://pmc.ncbi.nlm.nih.gov/articles/PMC8159987/)
- **Benamirouche et al. 2026, synthetic fridge predictive maintenance:** 27 fridges, 7.07M rows at 1-min, 6 degradation types, generator code. The arXiv page shows CC BY 4.0 for the paper; no dataset repository link on the abstract page. — [arXiv:2609.22229](https://arxiv.org/abs/2609.22229)
- **Bangkok household refrigerators:** temperature and humidity inside fridges of 123 households, Freshliance TagPlus-TH loggers, 5-min interval. Hosted via B2FIND; licence not confirmed. — [B2FIND record](https://b2find.eudat.eu/dataset/43ac660a-fa48-5675-a56c-fb3252b86fa0)
- **IEEE DataPort:** energy consumption of 103 household refrigerators over two years on an IEC 62552-compliant test bench (energy-focused). DataPort access terms vary. — [IEEE DataPort keyword page](https://ieee-dataport.org/keywords/ec-62552-household-refrigerators-energy-consumption-energy-efficiency-classification)
- **REFIT Electrical Load Measurements:** 20 UK houses, 2 years, aggregate plus 9 appliance channels at 8 s, including fridges and freezers (Murray et al., Scientific Data 2017). The Strathclyde page shows a CC BY 4.0 logo, but I could not confirm the dataset-specific licence. Users are asked to cite the Scientific Data paper. Dataset DOI 10.15129/31da3ece-f902-4e95-a093-e0a9536983c4. — [PMC5315495](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5315495/); [Strathclyde REFIT cleaned](https://pureportal.strath.ac.uk/en/datasets/refit-electrical-load-measurements-cleaned/)
- **Annotated load anomalies from REFIT** (including refrigerator, freezer and fridge-freezer). — [Strathclyde](https://pureportal.strath.ac.uk/en/datasets/annotated-load-anomalies-from-the-refit-dataset/)
- **UK-DALE:** open-access UK appliance-level electricity data. Sources disagree on sampling (individual appliances at 1/6 Hz; whole-house at 16 kHz). Licence not confirmed this session; commonly reported as CC BY 4.0. — [GWU dataset listing](https://bigdata.seas.gwu.edu/data-set-38-uk-domestic-appliance-level-electricity-uk-dale-data-set/)
- **Strawberry cold-chain shipments** (6 US shipments, 5–10 min). — [arXiv:2103.12895](https://arxiv.org/abs/2103.12895)
- **ASHRAE RP-1043:** chiller, not fridge; purchase only. — [arXiv:2011.00187](https://arxiv.org/pdf/2011.00187)
- **Kaggle:** no cold-chain/refrigerator temperature dataset was confirmed. The closest is a generic DHT IoT temperature/humidity dataset. An Edge Impulse project author reported finding no open dataset of in-fridge temperature/humidity and built their own. — [Baselight mirror of Kaggle IoT sensors](https://baselight.app/u/kaggle/dataset/luisenrique054_iot_sensors_01); [Edge Impulse refrigerator predictive maintenance](https://docs.edgeimpulse.com/experts/refrigerator-predictive-maintenance)

### Inferences
- Best use for ThermoTwin:
  - REFIT/UK-DALE fridge power to calibrate realistic compressor duty cycles and cycle periods (typical fridge cycling) in the simulator.
  - The Bangkok fridge temperatures to sanity-check simulated air-temperature amplitude and door-event signatures.
  - Sun et al. for fault-signature realism (door-open %, icing, fan failure, condenser blockage).
  - The Benamirouche generator as a second, independent simulator to test robustness to simulator mismatch. Train on ThermoTwin's simulator and test on theirs, which approximates the hidden synthetic test set risk.

### Gaps
- Licences for REFIT, UK-DALE, the Bangkok dataset and the Sun et al. figshare files were not confirmed from the data landing pages this session.
- No open vaccine-refrigerator (PQS) temperature log dataset was found.
- No Kaggle cold-chain dataset with verifiable provenance was identified.
