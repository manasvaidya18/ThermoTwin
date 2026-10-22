# CODE APEX 3.0 — Problem-Statement Analysis & Solution Playbook

Prepared 10 Oct 2026 from the five PDFs in this folder. Goal: understand all 11 problem statements, design a *distinctive* system for each, and pick the one to pitch in tomorrow's PPT.

**Contents**
1. What is actually in the folder (and rules/deadlines that matter)
2. How to choose — scorecard and recommendation
3. Track 4 · Technology for Social Cause (UST) — 3 problems
4. DeltaV industrial-automation pack — 3 problems
5. iMocha track — 5 problems
6. Patterns that win across all of them
7. Round-1 PPT: slide-by-slide mapping and what to build tonight
8. Sources and things I could not verify

---

## 1. What is actually in the folder

Not "4 problem statements + 1 PPT" — it is **3 problem-statement packs (11 problems in total), 1 handbook, 1 PPT template**.

| File (first 8 chars) | What it is | Problems |
|---|---|---|
| `7a78ae4f` | **iMocha track** — "AI Hackathon Problem Statements" | IM-01 Vibe Coding assessment · IM-02 Autonomous AI QA engineer · IM-03 Skill Passport · IM-04 AI Job Simulator · IM-05 Codebase Mentor |
| `2d49d07b` | **Track 4 — Technology for Social Cause**, powered by UST | T4-1 Cold-storage excursion early-warning · T4-2 Indoor positioning with sparse anchors · T4-3 Sensor trust / drift / false-alarm detection |
| `50b1e524` | **Industrial-automation (DeltaV) pack** — sponsor name is not printed on the PDF; DeltaV is Emerson's control system | #01 Untangle (P&ID → simplified sketch) · #02 IO Signal Sudoku (constraint packing into DeltaV hardware) · #03 Eagle Eye (cabinet photo vs drawing QC) |
| `8d3fe06f` | **Participant handbook** (rules, dates, demo tips) | — |
| `eb07ff99` | **PPT template** — green "VCA" theme | 7 content slides + thank-you |

### Timeline (handbook)
| Stage | Date | What it means for us |
|---|---|---|
| Registration closes | 9 Oct | done |
| **Round 1** | **10–11 Oct** | **Idea + PPT (this is the deliverable due tomorrow)** |
| Round 1 results | 12 Oct | |
| **Round 2** | 15–18 Oct | Online prototype — 4 days |
| Round 2 results | 19 Oct | |
| **Grand Finale** | 24 Oct, 8:30 AM, VIT Bibwewadi | 24-hour offline build, live demo, hidden test |

Assumption: the PPT is the Round-1 submission. The handbook says detailed per-round submission rules "will be shared directly with registered teams", so check your email/portal for slide limits or upload format before you finalise.

### Rules that shape the decision
- **AI tools, APIs, open-source are allowed — but every team member must be able to explain every component** (viva risk). Declare all models/tools.
- **Pre-built work is allowed** (handbook §9). So tonight's prototype work counts and belongs on the "What's built today" slide.
- Judging weights are **not published**. The handbook's own "strong demo story" is the best proxy: *Problem → Approach → Proof → Engineering → Impact*. "Proof" means something the judges can see working.
- Plagiarism / fabricated data → disqualification. iMocha: public/sample/synthetic data only, own API keys, never commit keys.
- DeltaV pack: sample data is "hackathon use only, do not share"; the tool must produce outputs end-to-end ("no hand-editing"); a **hidden test** decides.
- Track 4: organisers may supply a dev dataset and keep a **hidden test set**. Scoring dimensions: hidden-test performance, robustness to noise/missing/unseen conditions, explainability, deployability (API / app / edge), visualisation + demo quality, clarity of assumptions/limitations/validation.

### Errors inside the PDFs (so nobody gets confused)
1. **Track 4, problem 1** — the "Problem Statement" box under the cold-storage title contains the *indoor-positioning* paragraph (copy-paste slip). The real task is the bullet list on the next page (predict excursion probability, separate recovery from failure, explain, dashboard/API).
2. **Track 4, problem 2** — its "Suggested Technology" line is a copy of problem 1's (forecasting/anomaly/classification). For positioning, think filtering + sensor fusion + robust estimation.
3. The DeltaV pack is numbered backwards in the PDF (#03, #02, #01). Cosmetic only.

### The PPT template
Cover (problem, team) → **Problem & Target Need** (who is affected / current gap / why now) → **Proposed Solution & Innovation** (what's different / core mechanism / why feasible in this timeframe) → **System Architecture & Tech Stack** → **Key Features & UI/UX** → **Implementation Roadmap** (built today / in progress / planned) → **Expected Impact & Scalability** → Thank you.

---

## 2. How to choose

Ratings are my judgement for a typical 3–4-person student team: ●●●●● = best.

| Problem | Doable by 18 Oct | No data wait | Stands out | Demo wow | Provable with numbers | One-line verdict |
|---|---|---|---|---|---|---|
| T4-1 Cold-chain early warning | ●●●●● | ●●●●● | ●●●●○ | ●●●○○ | ●●●●● | Safest ML bet, strongest social story |
| T4-2 Indoor positioning | ●●●●○ | ●●●●● | ●●●○○ | ●●●●● | ●●●●● | Best live demo, needs maths comfort |
| T4-3 Sensor trust | ●●●●○ | ●●●●● | ●●●○○ | ●●●○○ | ●●●●● | Elegant; best as a *layer* inside T4-1 |
| #02 IO Signal Sudoku | ●●●●○ | ●●●○○ | ●●●●● | ●●●●○ | ●●●●● | Least crowded, objectively checkable |
| #01 Untangle | ●●○○○ | ●●○○○ | ●●●●● | ●●●●● | ●●●○○ | Moonshot: needs sample P&IDs + vision skill |
| #03 Eagle Eye | ●●○○○ | ●○○○○ | ●●●●○ | ●●●●● | ●●●○○ | Hardest: scarce data, "no false alarms" rule |
| IM-01 Vibe Coding | ●●●○○ | ●●●●● | ●●●○○ | ●●●●○ | ●●●○○ | Sponsor's headline; crowded |
| IM-02 AI QA engineer | ●●●○○ | ●●●●● | ●●●○○ | ●●●●● | ●●●●○ | Great demo; agent reliability is the work |
| IM-03 Skill Passport | ●●●●○ | ●●●●● | ●●○○○ | ●●●○○ | ●●●○○ | Crowded; wins only on evidence rigour |
| IM-04 Job Simulator | ●●●●○ | ●●●●● | ●●○○○ | ●●●●○ | ●●○○○ | Fun; feedback quality is the whole game |
| IM-05 Codebase Mentor | ●●●●○ | ●●●●● | ●●○○○ | ●●●○○ | ●●●○○ | Most obvious idea; needs real citation checking |

### My recommendation (without knowing your team's strengths)
1. **IO Signal Sudoku (#02)** — least crowded, the problem is a clean constraint puzzle, the hidden test is *objective* (zero violations, 100% allocated, minimal moves), and you can show a working 10,000-signal result on synthetic data before tomorrow's deadline. The "AI" story is honest and strong: **AI proposes, the solver guarantees, an independent referee verifies.** Condition: someone on the team is comfortable with Python + constraint solving, and you can get the sample IO MDB + Excel template from the organisers (ask now).
2. **If the team is ML-leaning → T4-1 Cold-chain, with T4-3's sensor-trust layer built in.** All data is synthetic and under your control; the idea has the best social-impact narrative; and the physics-twin + spoilage-budget ideas are distinctive.
3. **If you want the most impressive live demo → T4-2 Indoor positioning.**
4. **If you want to align with iMocha's headline → IM-01**, but only with the replay/evidence/fairness depth in section 5 — a plain "chat + score" version will look like every other submission.
5. **Avoid #01 and #03 unless** you already have strong computer-vision people *and* access to the sample drawings/photos. They have the highest payoff and the highest risk.

Questions to settle with the team in 5 minutes: (a) who can own the backend/algorithm? (b) who can own the UI/visualisation? (c) is anyone strong in computer vision? (d) can we get the organisers' sample data before Round 2?

---

## 3. Track 4 — Technology for Social Cause (UST)

**Shared design principle (from the PDF):** pure software/data problems; no proprietary hardware; organisers may provide *synthetic* data plus a *hidden* test set with unseen fault combinations and noise levels. So the winning move is the same for all three: **build your own realistic simulator, train on one slice of it, and test on slices with conditions the model never saw.** Report numbers on that — it mirrors the hidden evaluation and gives you proof for slide 6.

### T4-1 · AI-Based Predictive Cold-Storage Excursion & Early-Warning System

**In plain words.** Vaccines, medicines and food must stay in a temperature band (vaccines are typically stored at 2–8 °C). Today's monitors alarm *after* the limit is crossed — too late to save the stock. We must predict, minutes ahead, that an excursion is coming, tell the user *why*, and avoid crying wolf.

**Who is hurt.** Immunisation programmes and rural health centres (unreliable power, ageing fridges), blood banks, pharmacies, food distributors. A single failed fridge can spoil a whole batch.

**The real crux.** Three look-alike situations that need different responses: (a) **door opened, will recover on its own** — harmless; (b) **cooling slowly degrading** — fix it this week; (c) **sudden cooling failure** — act in the next 20 minutes. A threshold or a plain anomaly detector confuses them, producing false alarms (alarm fatigue) or late alarms.

**Our system — "ThermoTwin".**
1. **Simulator (data engine).** A two-node thermal model — *air* temperature and *product* temperature (product is slower because of thermal mass) — with a thermostat-controlled compressor, defrost cycles, door events, ambient swings, load changes, gradual cooling loss, sudden failure, power cut, sensor spikes/noise/dropout. Emits labelled episodes with `timestamp, storage temp, ambient temp, door state, cooling state, rate-of-change, noise, event label` — matching the PDF's field list.
2. **Online digital twin.** For each unit, estimate its own physical parameters on the fly (recursive least squares / Kalman): *cooling capacity*, *leak/insulation*. Output a **Cooling Health Index**. The twin predicts what a *healthy* unit would do next; the **residual** (actual − expected) is the key signal. A door-open recovery follows the twin's decay curve; a failing compressor does not.
3. **Excursion forecaster.** Gradient-boosted trees (LightGBM/XGBoost) on window features: slope, curvature, compressor duty-cycle, cycle period, time since door close, twin residual, ambient delta, rolling MKT. Compare against a small TCN/GRU baseline. Outputs **probability of excursion within H minutes** (H = 15/30/60) plus **time-to-breach** (quantile regression), probabilities calibrated (isotonic) so "80%" means 80%.
4. **Cause classifier.** `door-open` / `ambient` / `cooling degradation` / `sudden failure` / `sensor artefact` — as the PDF asks for contributing factors.
5. **Explainer.** TreeSHAP values mapped to plain-language **reason codes** ("cooling effectiveness down 23% over 6 days", "door open 9 min, 3× usual"). An LLM may *phrase* the alert, but only from these structured codes — it never invents causes.
6. **Alert policy.** Persistence + hysteresis + a cost-sensitive threshold tuned to a stated **false-alarm budget** (e.g. ≤ 1 per unit per month) — the PDF's "keep false alarms under control".

**Memorable features.**
- **Spoilage Clock** — instead of a binary "excursion", show *how much stability budget has been used*. Warm periods count for more than their average (Arrhenius weighting — the same idea behind mean kinetic temperature and WHO's vaccine vial monitors). A 6-minute blip and a 3-hour excursion stop looking identical.
- **Product vs air temperature** — don't alarm on an air spike the product core never felt.
- **What-if slider** — "if the door stays open 5 more minutes → predicted peak 7.4 °C, product stays safe."
- **Recommended action** attached to each alert (move stock to backup unit, check gasket, call technician).
- **Alert-fatigue meter** — a live false-alarms-per-week counter versus a classic threshold alarm on the same data.
- **Fleet view** — grid of fridges, red/amber/green, sorted by time-to-breach.
- **SMS/WhatsApp-style alert** for low-connectivity settings; **edge-ready** model (small tree ensemble/ONNX that runs on a Raspberry Pi-class device).
- **Sensor-trust pre-filter** borrowed from T4-3: if the sensor looks faulty, say "possible sensor fault — verify" instead of raising a product-risk alarm.

**How we prove it.** Hold out *whole episodes and fault types* (leave-one-fault-type-out), never random rows. Report: event recall at ≥ 15 / 30 min lead time, false alarms per unit-week, mean lead time, PR-AUC, Brier score/calibration curve, and a robustness grid (noise × missing-data × unseen fault combos). Show the same data through a classic threshold alarm for contrast.

**Risks / questions.** Organiser dataset schema (ask early; make the pipeline schema-adapter driven). Simulator realism — document assumptions and limitations (the PDF explicitly scores this). Avoid leakage via overlapping windows.

**Build tonight.** Simulator + LightGBM + one chart of "lead time vs false alarms: ours vs threshold alarm".

---

### T4-2 · AI-Based Indoor Positioning with Sparse Infrastructure and Noisy Measurements

**In plain words.** Estimate where a moving target (patient, wheelchair, infusion pump, person with dementia) is on a 2-D floor from distance/signal-strength readings to a *few* fixed beacons — when readings are noisy, some beacons drop out, and walls bend the signal (non-line-of-sight, NLOS, which makes ranges read too long). Output position **plus uncertainty**.

**The real crux.** Classical trilateration needs ≥ 3 clean ranges. With 3 anchors, one of them NLOS-biased, one missing — it breaks. And a fixed-layout neural net can't handle a different number/placement of anchors in the hidden test.

**Our system — "LocusNet".**
1. **Simulator.** Virtual hospital floor with walls; anchors at known (x, y); trajectories (corridor-following, waypoint walks, turns, stops); ideal range/RSSI + Gaussian noise + **NLOS bias when the line crosses a wall** + bursty packet loss + missing anchors. Mirrors the PDF's recipe exactly, and hidden-test conditions (different paths, noise, obstruction) are generated as separate splits.
2. **Per-anchor trust estimator.** Classifier giving *P(NLOS)* from range residual vs the consensus fix, RSSI-vs-range inconsistency, temporal jumps, variance.
3. **Robust estimator.** Measurement weights from step 2 feed an EKF / particle filter with robust (Huber/Student-t) loss; RANSAC over anchor subsets when ≥ 4 are available; motion prior + **map constraint** (walkable area) to resolve the two-anchor ambiguity.
4. **Learned model — anchor-agnostic.** A set-transformer over *anchor tokens* `(x, y, range, RSSI, valid-flag)` → position correction + covariance (heteroscedastic Gaussian likelihood), then a small GRU/smoother over time. Trained with **random anchor dropout and randomised noise/wall layouts** so one model works for 3, 4 or 6 anchors and unseen layouts.
5. **Uncertainty.** Output `(x, y, Σ)` and a **calibrated 90% ellipse** (conformal calibration). Honest behaviour: with 1 anchor the ellipse balloons instead of faking precision.

**Memorable features.**
- **Anchor Placement Advisor** — "you can afford 4 beacons; place them *here*; predicted P90 error = 1.3 m." Uses geometric dilution of precision / Cramér–Rao bound. This directly serves the PDF's "reduce installation complexity".
- **Degradation heat-map** — error vs (number of anchors × NLOS rate × noise): the comparison the PDF explicitly requests.
- **Kill-an-anchor live demo** — click an anchor off, watch the estimate and ellipse adapt, next to classical trilateration failing.
- **Distance to the theoretical limit** — plot our error against the CRLB to show how close we are.
- **Last-known-zone fallback** — when confidence is too low, report "probably in Ward B" rather than a bad point.

**How we prove it.** RMSE, P90 error, error CDF, per-condition tables, calibration (does the 90% ellipse contain truth ~90% of the time?), plus ablations (no NLOS filter, no motion model, fixed-layout net). Baselines: least squares, EKF, particle filter.

**Risks.** Sim-to-real gap (state it; add one public UWB/BLE dataset for a baseline check — verify its licence). Hidden-set schema unknown.

**Build tonight.** Simulator + LS/EKF baseline + the animated floor-plan demo with one anchor failing.

---

### T4-3 · AI-Based Sensor Trust, Drift and False-Alarm Detection

**In plain words.** An alarm is only as good as the sensor behind it. Decide for each abnormal reading: **real event** (several sensors agree it happened) or **sensor problem** (spike, stuck value, noise burst, offset/gain drift, dropout) — and give each sensor a **trust/health score**.

**The real crux.** A real event and a fault both look like "a deviation". The discriminator is *context*: a real event moves related sensors together and with physically plausible lag; a fault is local.

**Our system — "SensorCourt" (four witnesses and a judge).**
1. **Forensic witness (single sensor).** Spikes (Hampel/MAD), flatline/stuck runs, noise-variance ratio, drift via CUSUM/Page-Hinkley and robust slope, gaps.
2. **Peer witness (across sensors).** Predict each sensor from its neighbours (ridge/GP/GBM with lags) and score the residual. Add a **PCA monitor**: *T²* flags variation **inside** the normal correlation pattern (= genuine event), *Q/SPE* flags variation that **breaks** the pattern (= sensor fault). Contribution plots point at the guilty channel. Neat rule of thumb for the pitch: *"events live in the subspace, faults live in the residual."*
3. **Physics witness.** Rate-of-change limits, range limits, propagation-lag consistency.
4. **History witness.** The sensor's calibration age and prior faults as a Bayesian prior.
5. **Judge.** A per-sensor state machine/HMM over {healthy, drifting, stuck, noisy, spiky, dropout, failed}; the posterior is the **trust score**. Each alarm gets a verdict: *Trusted event / Suspected sensor fault (type, confidence) / Verify*.
6. **Maintenance planner.** Drift rate → "out of tolerance in ~9 days → recalibrate"; replace-vs-recalibrate guidance.

**Memorable features.**
- **Verdict cards** with the evidence ("S3 residual +6σ; 3 of 4 peers flat → gain error on S3, 87%").
- **Virtual-sensor failover** — a quarantined sensor is replaced by an estimate from its neighbours so monitoring continues.
- **Fault Fuzzer** — inject faults live and see the detector respond; doubles as the robustness test.
- **Sensor leaderboard** (health scores) and **maintenance calendar**.
- **False-alarm reduction at fixed sensitivity** shown as one headline number.

**How we prove it.** Event-vs-fault AUC; fault-type macro-F1; alarms removed at ≥ 95% genuine-event recall; time-to-detect drift; trust-score calibration. **Train on single faults, test on combinations** (the PDF's hidden-test condition).

**Honest limits (say them on the slide).** Faults that hit *all* sensors identically (common-mode) are invisible to peer comparison — mitigate with physical bounds and a reference; slow genuine change vs slow drift is ambiguous; single-sensor mode is weaker than multi-sensor.

**Best use.** As a *module* inside T4-1 rather than a stand-alone entry — but it also stands alone well if the team prefers the statistics-heavy problem.

---

## 4. DeltaV industrial-automation pack

**Background you need (60 seconds).** A process plant has thousands of field instruments. Each sends one electrical signal on a **pair** of wires, bundled into multi-pair **cables** (24/12/6/2 pairs) to a **marshalling cabinet** in the control room. Inside, signals land on **CHARM** modules (1 CHARM = 1 signal), 12 per **baseplate**; 8 baseplates per **CIOC** controller card; up to 4 CIOCs per cabinet (**32 baseplates = 384 slots**). The pack's three problems cover the P&ID diagrams, the IO allocation, and the final quality check. The PDF says "no DCS background needed" — treat them as vision/logic/constraint puzzles.

### #02 · IO SIGNAL SUDOKU — rule-driven allocation of 10,000+ signals

**In plain words.** Input: an Excel list where each row is a signal (`tag, IO type, cable, pair, IO group, segregation A/B`). Output: an Excel in the customer's template giving every signal an exact home — *cabinet → CIOC → baseplate → CHARM slot*, with the right CHARM type, terminal block and names — obeying user-defined rules, raising a **TQ** (technical query to the customer) for anything it cannot place, and handling **revisions** with the fewest moves.

**Rules in the PDF.** Keep logical groups together; never put A and B signals on the same CIOC; capacity (12/8/4); keep each cable's pairs side-by-side in pair order (a 24-pair cable fills exactly two baseplates: 22 signals + 2 wired spare pairs); leave ~10% spare per cabinet; right CHARM + terminal block per signal type (AI → AI CHARM; AO; DI; high-current DO → isolated DO CHARM with fused injected power; normal DO; relay output); user-defined naming patterns; **and the user can add/edit/remove any rule — nothing hard-coded.**

**The real crux.** It is a **bin-packing problem with side constraints** (contiguous blocks, group cohesion, anti-affinity, spare reserve, naming), and then a **minimal-change re-solve** when the customer sends Rev B. Greedy heuristics (and LLM "just allocate it" approaches) will leak violations at scale; a solver won't.

**Size check.** 10,000 signals ≈ 27 cabinets at 100% fill, ≈ 30 with a 10% reserve (before cable padding). That arithmetic becomes our **lower bound** — and a headline claim: "our result is within N cabinet(s) of the theoretical minimum."

**Our system — "Sudoku Engine".**
1. **Ingest + auto-map.** Read one or many Excel files; map headers to canonical fields (fuzzy match + LLM fallback, always shown for confirmation). Validate: duplicate tags, missing IO type, cable pair out of range, pair used twice, inconsistent segregation → each becomes a TQ *before* solving.
2. **Rule engine (declarative).** Rules live in YAML/JSON, not code: `capacity`, `anti_affinity(field, scope)`, `cohesion(field, scope, ordered)`, `contiguity(cable)`, `reserve(%, scope)`, `mapping(io_type → CHARM, terminal block)`, `naming(pattern)`, plus custom rules. Each rule has an on/off switch and a weight if soft. Rule sets are saved per project. A **static rule-conflict checker** warns before solving ("spare 40% + keep-group-together cannot both hold for G1").
3. **Solver (hierarchical).**
   - *Blocks:* each cable becomes a block of N slots (small cables may share a baseplate).
   - *Level 1:* assign blocks to CIOCs/cabinets with OR-Tools **CP-SAT** — hard constraints: capacity, A/B anti-affinity, spare reserve; objective: fewest cabinets, then fewest group splits, then least fragmentation.
   - *Level 2:* order blocks within each CIOC, place contiguously on baseplates/slots in pair order.
   - *Level 3:* generate names from the patterns; assign CHARM + terminal block from the mapping table.
   - Decompose by group so 10k signals stay tractable.
4. **Independent referee.** A *separate* validator re-reads the output Excel and checks every enabled rule from scratch. "Zero violations" is a **certificate**, not a hope. (This is the strongest answer to "how do we know it's right?")
5. **TQ engine.** Infeasibility explanations from solver assumptions/pre-checks → each TQ has an ID, severity, affected tags, the rule that conflicted, a plain-English reason and a suggested question to the customer. Missing-data TQs are listed separately from rule-conflict and capacity TQs.
6. **Revision (Rev A → Rev B).** Diff by tag → unchanged / added / deleted / changed. **Pin** unchanged signals, re-solve only the affected region, and widen the "release radius" step by step (slot → baseplate → CIOC → cabinet) only if infeasible. Objective puts *moves* far above *cabinet count*. Output: impact report (added, deleted, moved, cabinets touched) and the **ripple radius**.

**The AI layer (kept honest).** LLM for: column mapping, **natural-language → rule** ("reserve 15% spare and isolate all SOVs" → JSON rule shown as a diff for approval), TQ wording, and **rule mining** from a previous project's allocation ("this past Excel obeyed these 6 rules — adopt them?"). The solver never depends on an LLM for correctness.

**Memorable features.**
- **The Sudoku board** — a visual grid cabinet → CIOC → baseplate → 12 slots, coloured by group, striped for A/B, hatched for spare; hover for tag/cable/pair/CHARM/terminal block; violations pulse red. The solver "fills the board" on screen.
- **Rule playground** — drag spare % from 10 → 15 and watch cabinets 29 → 31 live.
- **"Why is this signal here?"** — click a slot, get the constraints that decided it.
- **Rev A ↔ Rev B slider** — moved signals animate; the impact map highlights touched cabinets.
- **Optimality gap** versus the capacity lower bound.
- **Extensible hardware profile** — Phase 1 is DeltaV, but capacity/CHARM tables are data, so another DCS is a new profile, not a rewrite.
- **Fuzz-tested** — random IO lists with planted defects prove TQ recall and zero violations at scale.

**How we prove it.** Synthetic generator at 100 → 10,000+ signals; metrics: % allocated, violations (must be 0), cabinets vs lower bound, fill %, solve time, TQ precision/recall on planted defects, moves per revision.

**Risks / questions for organisers.** Exact Excel template layout; can one baseplate mix CHARM types/terminal blocks; whether group cohesion is hard or soft; is the ~10% spare per cabinet or per project; ordering semantics of "in sequence"; how spare pairs count toward slots; which signals are "no group".

**Build tonight.** Generator + rule YAML + CP-SAT for one cabinet + referee + the Sudoku board screenshot, then a 10k-signal timing run.

---

### #01 · UNTANGLE — customer P&ID + IO list → simplified sketch

**In plain words.** A P&ID is a plant's piping-and-instrumentation drawing: lots of bends, crossovers and detail. Control-room operators need a clean view: only the **major equipment** (tanks, vessels, pumps, exchangers) and the **instruments in the IO list**, connected in correct flow order, drawn left-to-right with straight lines. Engineers redraw this by hand today.

**The real crux.** Turning a drawing into a **graph** (what connects to what, which way the fluid flows), then *simplifying* the graph without losing connectivity, then *laying it out* readably. The two worst traps are (a) crossing lines that are *not* connected, and (b) duty/standby pumps that cross each other on the drawing but are logically parallel.

**Our system — "Untangle Graph".**
1. **Dual-path ingestion.** *Vector PDFs* (CAD exports — most customer P&IDs): read paths and text with coordinates directly (PyMuPDF) — far more reliable than image processing. *Scanned/raster PDFs:* render at 300 dpi → OCR + symbol detection. Detect which path to take automatically.
2. **Symbol layer.** Instrument bubbles with tags; equipment (vessel, tank, pump, exchanger); valves. Rules on primitives for vector input; a vision-language model or detector for classification (declare it).
3. **Line layer.** Separate process lines (thick/solid) from signal lines (thin/dashed); snap endpoints, split T-junctions, and treat *unmarked crossings as not connected*.
4. **Tag handling.** Parse tags with ISA-style grammar (first letters = variable, e.g. PT/FT/LT/TT; number = loop) and **fuzzy-match IO-list tags to OCR'd text** (`PT-101A` vs `PT101A`, `O`↔`0`) — then produce the required **tag-check report** (found / not found / near-miss suggestion).
5. **Flow direction.** From arrowheads, then equipment semantics (pump suction→discharge, nozzle positions, check valves), propagated through the graph.
6. **Simplify.** Contract away elbows, minor valves, reducers and non-IO instruments; keep IO-list instruments as ordered "taps" on the edge they measure.
7. **Recognise structure.** **Series-parallel decomposition**: series → left-to-right; parallel branches with matching component types → duty/standby drawn as two parallel rows. This resolves the "pumps cross over each other" case *by construction*.
8. **Layout.** Layered (Sugiyama-style) layout with orthogonal routing (e.g. ELK); constraints: left→right, minimise bends and crossings, parallel groups aligned. Export SVG → PDF/PPTX/PNG.

**Memorable features.**
- **Trace-back** — click any line in the sketch and the original P&ID path lights up (builds trust, which the judges will care about).
- **Confidence overlay** — low-confidence edges/tags flagged amber.
- **Two-extractor cross-check** — rule-based and vision-model graphs compared; disagreements are queued for review.
- **Synthetic P&ID generator** — we create vector P&IDs with *known* ground-truth graphs, random bends, crossovers and duty/standby pairs, giving unlimited test data and real accuracy numbers on unseen drawings.

**How we prove it.** Tag recall (IO list vs found), equipment recall, **edge precision/recall** against ground-truth graph, flow-direction accuracy, crossings and bends per sketch.

**Risks.** Highest data dependency (needs the sample P&IDs and IO lists), messy real drawings, raster quality. Fallback: vector-first, human-confirmation UI for low-confidence items.

**Build tonight.** Only if sample files are in hand: parse one vector P&ID, extract tags, print the tag-check report. Otherwise the synthetic generator + graph simplification demo.

---

### #03 · EAGLE EYE — cabinet photo + drawing → QC check sheet

**In plain words.** Technicians build a control cabinet from a drawing. QC inspectors then check *by eye* that every part is present, in the right place and order, correctly labelled, and that every wire has the right ferrule and colour. We must take a **photo + GA drawing (PDF) + wire/label Excel lists + QC checklist** and produce a filled checklist: PASS/FAIL per item, FAILs boxed on the photo with a zoomed snippet, "expected vs found", and a **re-check** after the fix.

**The real crux.** (1) *No false alarms* — a correct item must never be marked FAIL. (2) *Generalise to a cabinet never seen*. With little labelled data, you cannot train a detector from scratch — so use the **drawing as the query**: it tells the system exactly what to look for and where.

**Our system — "Eagle Eye".**
1. **Drawing → expected model.** Parse the GA PDF's text/shapes into an expected layout (component, label, rail/row, order). Parse Excel lists into an expected wire/ferrule table (`CB11-2/PS11-L` = from CB11 pin 2 to PS11 pin L).
2. **Photo prep.** Rectify perspective to the backplate; tile and upscale for small text.
3. **Find and read.** Open-vocabulary detection/segmentation or a VLM proposes boxes; OCR on label and ferrule crops is **decoded against the known vocabulary** from the drawing (closed-set matching fixes `O/0`, `I/1`), which raises accuracy dramatically.
4. **Align and compare.** Use confidently read labels as anchors to map photo ↔ drawing; check **presence** (expected region empty = missing; part found but unlabelled = missing label), **order** (edit-distance/permutation analysis catches "CB43 ↔ CB44 swapped"), **label match**, **ferrule match** against the wire list, **wire colour** (brown phase, blue neutral, green/yellow earth, red +24 V, black 0 V — colour-normalised classification).
5. **Three-lane verdict.** PASS (evidence), FAIL (evidence above threshold), and **VERIFY** (low confidence — glare, blur). Everything still appears in the PASS/FAIL sheet as required, but VERIFY items are flagged "needs a human glance" instead of being asserted as FAIL. This is how the "no false alarms" rule is honoured.
6. **Evidence pack.** For each FAIL: box on the photo, zoomed snippet, expected vs found.
7. **Re-check loop.** Register the new photo to the old (feature matching + homography), re-run only the failed items, close those that pass, keep an **issue ledger** (history, timestamps, before/after).
8. **Plug-in checks.** `Check` interface (`needs`, `run() → Finding`) + a registry + a YAML that maps checklist rows to checks, so adding "earthing" or "shrouds" is one new file and one YAML line — not a rewrite.

**Memorable features.** Before/after slider for re-checks; "unreadable — retake photo from this angle" guidance; planted-fault self-test (copy-paste/inpainting to create synthetic faults on sample photos and measure detection).

**How we prove it.** Per-check precision/recall on planted faults; false-FAIL count (target 0); % of items auto-verified vs sent to VERIFY.

**Risks.** Hardest of the eleven: little data, small text, lighting; heavy reliance on vision models. Choose only with real CV capability and sample data in hand.

---

## 5. iMocha track

**What iMocha already ships (verified from their help centre, see sources).** iMocha has a "Coding Assessment with AI Assistant": three-panel screen (problem · editor · AI assistant); the assistant is **hint-only** (never writes passing code); the assistant **cannot see the candidate's code** unless it is attached with `@`; coding and **"AI fluency"** are scored separately; AI fluency has three parameters — Context Quality, Critical Thinking, Collaboration — graded A/B/C, giving a High/Medium/Low badge; recruiters see the **chat transcript** (not a replay). Their own docs list **no practice/preview mode** and **no on-request re-evaluation** in the current release, and candidates who never use the assistant get "Low" overall.

This tells us exactly where IM-01 can add value, and that the other four problems are fresh ideas rather than extensions of an existing product.

### IM-01 · Vibe Coding: the AI-era coding assessment — "VibeLens"

**In plain words.** Candidates build a small real-world task in a browser workspace with an AI assistant; recruiters get a skill report. The open questions: a better candidate experience, and a report that is useful, fair and easy to trust.

**Where we beat the current product (every point maps to the PDF's "expected solution").**
1. **Practice mode + onboarding** — a 5-minute sandbox task showing the workspace, the assistant and what is (and isn't) measured. Removes anxiety and a source of unfairness; today's product lacks it.
2. **Capture the whole journey, not just chat.** Event stream: prompts, AI responses, edits, runs, test results, accept/reject/paste of AI code, idle gaps, file switches. A phase classifier segments the session into **Understand → Plan → Build → Verify → Fix → Reflect**.
3. **AI Reliance Map (provenance).** Line-level authorship of the final code: human / AI-accepted-as-is / AI-then-edited. Computed by code, not by an LLM.
4. **Verification behaviour.** Time from "AI code inserted" to "first run or test"; tests written; did they catch a flaw in AI output (task designs include natural edge-case traps in the spec — *not* a sabotaged assistant, which would be unfair).
5. **Comprehension micro-checks.** Two quick "predict/explain" questions about code the AI wrote ("what happens if the list is empty in `parse()`?") — separates *understanding* from *accepting*.
6. **One-page skill report.** Radar over: problem decomposition · context/prompt clarity · verification · debugging · code quality · AI judgement · comprehension. Each score = rubric level + **confidence band** + two **evidence moments** (click → the session replays at that timestamp) + a plain-language sentence. A working-style archetype (e.g. Verifier / Delegator / Explorer / Driver).
7. **Fairness by design (the "why you can trust this" panel).** Rubric-anchored scoring; *facts computed by code, judgement by LLM, evidence by pointer*; scores re-run with two judge prompts/models and the **agreement shown**; prompts scored on **intent clarity, not grammar** (Hinglish and non-native English are not penalised); not using the AI is not auto-"Low" — "AI judgement" includes knowing when not to use it; **parity test** — same behaviour phrased in different language styles must score the same; candidates can **see their report and request human re-evaluation**; hidden checks are never revealed (feedback speaks in skill categories, not test content).
8. **Candidate feedback** — "What went well / practise next" with 2–3 targeted mini-exercises.
9. **Recruiter view** — side-by-side candidate comparison with *explanations*, not just ranks.

**Architecture.** Monaco editor + in-browser sandbox (Sandpack/Pyodide) or containerised runner; event logger; metrics service (deterministic); LLM judge with JSON-schema rubric output; report renderer (HTML→PDF).

**Stage 2 target.** Recorded/mock session → event log → first report. **Stage 3.** Live session, replay, parity test, polished one-pager.

### IM-02 · Autonomous AI QA Engineer — "ScoutQA"

**In plain words.** Give an agent a web-app URL and a short description; it explores like a user, invents tests, runs them in a real browser, files **evidence-backed bug reports**, and turns good journeys into reusable automated tests.

**The real crux.** The **oracle problem** — how does the agent know something is a bug? And **trust** — a bug report must be reproducible by a human, or it is noise.

**Our system.**
- **Agents:** *Explorer* (builds a state graph of the app; DOM-state hashing; novelty- and risk-driven exploration) · *Planner* (prioritises journeys: sign-up, login, checkout, search) · *Tester* (Playwright, using the accessibility tree + screenshots) · *Judge* (the oracles) · *Reporter* (dedupe, severity, step minimisation) · *Codifier* (emits Playwright tests with role-based locators).
- **Oracle zoo:** console errors, HTTP 4xx/5xx, broken links, accessibility violations (axe-core), layout overflow/visual anomalies, **spec-derived expectations** (LLM turns your description into checkable assertions), and **metamorphic checks** (add then remove an item → cart total returns; search results consistent with filters).
- **Repro Verifier (the differentiator).** Before any bug is reported, a clean browser **replays the steps 3 times**; only reproducible bugs are filed → precision and the PDF's "every report can be reproduced by a person" are enforced automatically. A **delta-debugging minimiser** shrinks the steps.

**Memorable features.** *BugBench* — our own sample shop app with 20–30 **planted bugs** across categories (functional, validation, state, UI, security such as XSS/IDOR) → we report **recall, precision, reproduction rate, duplicates, cost per bug**. App-map coverage view (states visited vs unseen). Dashboard with severity and trend. One-click **GitHub Actions export** of the generated tests. Flakiness detection.

**Risks.** Agent reliability and cost; start with a tightly scoped sample app, then show it on a second app to demonstrate generality.

### IM-03 · Skill Passport: verified skills from real work — "ProofPass"

**In plain words.** Turn a student's real work (GitHub repos, project reports, portfolio, certificates, resume) into a skill profile where **every skill is tied to evidence**, compared with a target role, with a learning plan and a recruiter view readable in under a minute.

**The real crux.** *Never show an unsupported claim as verified.* LLMs happily infer skills from a README; recruiters need proof.

**Our system.**
1. **Evidence extraction (deterministic first).** Dependency manifests → tech inventory; AST/static analysis → practices (tests, CI config, Docker, typing, error handling, modularity); git history → cadence, **authorship share by commit email**, collaboration; duplicate/template detection → reduces credit for boilerplate/forks; resume parsed into **claims**; certificates marked *verified* only if a public verification link/ID exists, otherwise *self-declared*.
2. **Evidence graph.** Each evidence node: type, source (file:line / commit / URL), strength, recency (decay). Skills link to nodes; scores aggregate evidence (noisy-OR/Bayesian) into levels L0–L4 from an explicit rubric ("L2 needs ≥ 2 independent artefacts with non-trivial usage").
3. **Three honest states.** **Verified** · **Evidenced (weak)** · **Claimed only** (grey, never counted).
4. **Citation verifier.** The LLM may only reference evidence IDs; a post-check confirms each cited file/line exists and supports the statement; failures are dropped (**fail-closed**).
5. **Role match.** Target role from a JD or an open taxonomy (e.g. ESCO / O*NET / SFIA — pick one and state it on slide 3) → coverage score with a "why" breakdown and gaps.
6. **Learning plan as new evidence.** Prerequisite graph + time budget; each plan item is a **proof task** whose output is re-analysed, so a "gap" can turn into "Verified" — the loop closes.
7. **Shareable passport.** One-page recruiter view with a trust bar; signed JSON/hash + QR so the recruiter can verify it hasn't been edited. Placement-cell cohort view: skills supply vs role demand.

**Memorable features.** *Claim-vs-Proof ledger* ("12 claimed · 7 verified · 3 weak · 2 unproven"); **planted-lie test** — a resume with fake skills (Kubernetes, Rust) that the system must refuse to verify (measurable hallucination rate = 0); skill-decay by recency; counter-evidence flags.

### IM-04 · AI Job Simulator: practise real work scenarios — "DayOne"

**In plain words.** Students role-play realistic work moments (production incident, code review, vague client, tough teammate) with AI characters, then get an evidence-backed, rubric-graded debrief.

**The real crux.** Free-form LLM chat wanders, leaks hidden facts, and gives vague feedback. We need scenarios that **react** but stay **fair and gradeable**.

**Our system — Director · Actors · Assessor.**
- **Scenario spec (YAML):** world facts, **hidden facts**, characters (goal, personality, what they know), **beats** with triggers (e.g. asking about the deadline unlocks the client's real budget), work **artefacts** (logs, a diff, a ticket), rubric, strong/weak example moves.
- **Director** holds scenario state and fires beats and timed events (a pager alert at turn 4). **Actors** speak only from what their character knows (prevents leaks). **Assessor** silently tags behaviours to the rubric with turn IDs while you play.
- **Debrief:** per rubric dimension — score, **verbatim quotes** (a programmatic check confirms each quote exists in the transcript; unsupported lines are dropped), "a stronger move would have been…", and **missed opportunities** ("you never asked about the deadline; the client would have revealed X").
- **JD → scenario generation:** extract competencies from a job description, fill a scenario template, and validate that every rubric dimension has ≥ 2 observable moments.

**Memorable features.** Visible **pressure meters** (manager patience, client trust); **rewind-and-retry from any turn** (branching what-ifs); incident "war room" with several characters; voice mode (browser speech or Whisper + TTS); progress radar across attempts; difficulty that adapts; three launch scenarios — *2 a.m. outage*, *PR with a security flaw and a defensive teammate*, *vague client requirement*.

**Fairness.** Anchored rubric with example transcripts; two assessor passes with agreement reported; accent/grammar never scored unless the dimension is communication; Hinglish accepted.

### IM-05 · Codebase Mentor: AI onboarding for developers — "CodeSherpa"

**In plain words.** An AI mentor that reads a repo and helps a newcomer understand it quickly, with every answer grounded in real code.

**The real crux.** *Grounding.* "Chat with repo" bots hallucinate file names and confidently explain code that isn't there.

**Our system.**
1. **Index.** tree-sitter → symbols, imports, call graph (static approximation), entry points (main, routes, CLI, handlers), test-to-code mapping. Symbol-level chunks with context headers.
2. **Retrieve.** Hybrid (keyword + embeddings) → **graph expansion** (callers/callees) → **git history** (blame, commit messages) for "why" questions. Mining history is the key: this is where "knowledge in senior engineers' heads" actually lives.
3. **Answer with proof.** Every claim carries `[path:Lstart–Lend@commit]`. A **citation verifier** reopens the lines and checks support; unsupported claims are removed; when it can't ground an answer it says so and points to where to look (**abstain**).
4. **Architecture overview.** Module clustering over the import graph (community detection) → LLM-named components → interactive diagram with click-through to code.
5. **Guided tours.** For "what happens when a user signs up?", locate the entry point by retrieval, follow the call graph, and present ordered steps with highlighted code and **predict-then-reveal** mini-questions.
6. **Starter tasks.** Mine `good first issue`, TODO/FIXME, skipped tests, low-coverage modules; rank by small blast radius; output a task card (goal, files to read, steps, how to test, **who to ask** from CODEOWNERS/blame).
7. **Living docs.** Doc sections carry **code anchors** (symbol + content hash). On push, changed anchors mark sections stale and regenerate *only* those sections (as a PR).

**Memorable features.** "Why was this written this way?" answered from history; **tribal-knowledge capture** (unanswerable questions go to a maintainer; the reply is saved as a verified note anchored to code); docs freshness badge.

**How we prove it.** Citation precision (% of cited ranges that truly support the claim), answer accuracy on a 30-question golden set from the repo's own issues, and the required **peer test** (e.g. 6 newcomers, with vs without mentor, time-to-first-correct-answer).

---

## 6. Patterns that win across all eleven

1. **Evidence on every output.** The three packs all demand proof — cited code, linked evidence, expected-vs-found, a TQ with reason, a reason code. Build "show your work" in as a core feature, not an extra.
2. **Abstain rather than bluff.** VERIFY lanes, "I couldn't ground this", low-confidence flags. Judges punish confident wrong answers more than honest gaps.
3. **Declarative over hard-coded.** Rules in YAML, checks as plug-ins, hardware as profiles. Both the DeltaV pack and Track 4's "unseen conditions" reward this.
4. **Build your own benchmark and report numbers.** Planted bugs, planted lies, planted faults, synthetic hidden test. One chart of real results beats three slides of claims.
5. **Facts by code, judgement by LLM, evidence by pointer.** Keep the LLM out of anything that can be computed or verified deterministically.
6. **Fairness and limitations as visible features** — especially for assessment problems (IM-01, IM-04) and Track 4's explicit "assumptions and limitations" criterion.
7. **Demo discipline** (handbook): rehearsed flow, recorded backup video, local sample inputs, a 30-second explanation before the deep dive.

---

## 7. Round-1 PPT — slide mapping and what to build tonight

| Slide | Put here |
|---|---|
| 1 Cover | Problem statement, team name, leader |
| 2 Problem & Target Need | **Who** (specific persona) · **Gap** (what today's process misses — one concrete number or scenario) · **Why now** |
| 3 Solution & Innovation | **What's different** (the 2–3 signature ideas above) · **Core mechanism** (a 4–5-step diagram) · **Why feasible** ("we already ran it on synthetic data: result X") |
| 4 Architecture & Stack | Pipeline diagram + stack boxes: frontend / backend / database / AI-APIs / hosting. Name every model and tool (handbook: be ready to explain) |
| 5 Features & UI/UX | 3–4 real screenshots or mock-ups — the Sudoku board, the verdict card, the replay report |
| 6 Roadmap | **Built today** (the tonight prototype — be concrete) · **In progress** · **Beyond hackathon** |
| 7 Impact & Scalability | Beneficiaries, scale story, how it grows past the demo |
| 8 Thank you | Contact |

**Tonight's "built today" proof, per problem** (aim for ~3–4 hours of work):
- **#02 Sudoku:** synthetic IO MDB generator → CP-SAT on one cabinet → referee → board screenshot → 10k-signal timing.
- **T4-1 Cold-chain:** simulator → LightGBM → "lead time vs false alarms" chart vs threshold alarm.
- **T4-2 Positioning:** simulator → trilateration vs robust filter → error-vs-anchors heat-map.
- **T4-3 Sensor trust:** simulator with injected faults → PCA T²/Q split → confusion matrix.
- **IM-01:** clickable report mock-up built from a *recorded sample session* (the PDF explicitly accepts this).
- **IM-02:** tiny sample app with planted bugs + one Playwright run + one reproduced bug report.
- **IM-03:** run on one public repo + a resume containing fake skills; show them flagged "unproven".
- **IM-04:** one scenario spec + text chat + rubric debrief with verbatim quotes.
- **IM-05:** index one open-source repo and answer 5 questions with verified citations.
- **#01 / #03:** only with the sample files in hand.

---

## 8. Sources and things I could not verify

**Verified (public sources):**
- iMocha AI-assisted coding test — candidate view: <https://help.imocha.io/kb/article/360/how-can-a-candidate-take-ai-assisted-coding-assessment>
- iMocha AI-assisted coding test — admin view, report tabs, AI-fluency parameters, limitations: <https://help.imocha.io/kb/article/361/how-to-configure-ai-assisted-coding---admin-view>
- WHO PQS vaccine vial monitor specification (defines mean kinetic temperature and the Arrhenius basis of VVMs): <https://extranet.who.int/prequal/sites/default/files/document_files/who_pqs_e006_in05_vp.4.pdf>

**Not verified — do not put on a slide without a primary source:**
- The widely repeated claim that "up to 50% of vaccines are wasted" — I found it only repeated in secondary sources, not traced to a WHO primary document. Also, in the one detailed public wastage report I found (Ontario), expired stock rather than cold-chain failure was the largest cause. Use the *mechanism* (heat exposure degrades vaccines; alarms come too late) rather than a headline percentage unless you find the primary figure.
- Anything about the sample data in the DeltaV pack (template layout, real P&ID quality) — I have not seen it; section 4 lists the questions to ask organisers.
- The judging weights — the handbook says they will be decided at the judges' discretion.
