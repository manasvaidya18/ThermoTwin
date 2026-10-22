# AI Agents and Edge AI for IoT Monitoring, Predictive Maintenance and Cold Chain (with low-resource deployment constraints for rural India)

Research date: 11 October 2026. Scope: which "agent" components are useful and safe for ThermoTwin (predicts cold-storage temperature excursions, explains causes, recommends actions), and how to deploy on cheap hardware with poor connectivity. Hype vs evidence is flagged throughout: "vendor claim" = company marketing or press material with no independent evaluation.

## 1. Agentic AI in industrial IoT, predictive maintenance and cold chain (2024 to 2026): products, what works, failure modes, guardrails

### Takeaway
Every major industrial vendor now ships an LLM "copilot" or "agent" for maintenance, but they are mostly natural-language front ends over existing analytics (alarm summaries, work-order coding, document lookup), and the evidence for them is vendor-reported. The only rigorous public benchmark for industrial maintenance agents (IBM's AssetOpsBench) and root-cause benchmarks (OpenRCA) show low accuracy, high hallucination in some setups, and agents that over-claim success. That supports using an LLM to explain and draft, not to detect or decide. I found no cold-chain monitoring vendor with a confirmed generative-AI copilot.

### Cited Findings
**Vendor products (mostly vendor claims)**
- Siemens extended its Industrial Copilot in March 2025 with a generative-AI maintenance offering built on Senseye Predictive Maintenance (runs on Microsoft Azure). It covers reactive through predictive maintenance, and an entry package pairs "AI-powered repair guidance" with basic predictive capability. The coverage is a reprinted press release with no independent evaluation. — [Automation.com](https://www.automation.com/en-us/products/march-2025/siemens-industrial-copilot-generative-ai); [CIMdata](https://www.cimdata.com/en/industry-summary-articles/item/27216-siemens-expands-industrial-copilot-with-new-generative-ai-powered-maintenance-offering)
- IBM Maximo Condition Insight is described as an "agentic AI" capability in Maximo APM. It reads work orders, metrics, time-series data, meter readings, FMEA and alerts, then gives plain-language recommendations. IBM says the Maximo AI Service will automate condition-based maintenance "using a group of AI agents" (a forward-looking vendor claim). — [IBM announcement](https://www.ibm.com/new/announcements/maximo-condition-insight)
- The Maximo AI assistant (MAS 9.1+) answers work-order, service-request and asset questions. An administrator must configure it and can restrict which request types it answers. IBM notes that abbreviations like "WO" may need prompt tuning. — [IBM Docs](https://www.ibm.com/docs/SSLPL8_cd/com.ibm.mam.doc/aiconfiguration/c_max_assist.html)
- Maximo AI features in production are narrow, well-bounded tasks: suggesting failure/problem codes from work-order text, detecting duplicate work orders, and validating work-order details. — [IBM Expert Labs](https://www.ibm.com/new/announcements/introducing-ai-offerings-for-maximo-application-suite-from-ibm-expert-labs); [Verdantix on MAS 9.0](https://www.verdantix.com/insights/blog/ibm-maximo-application-suite-9.0-provides-users-new-genai-fsm-and-emissions-functionality)
- AWS IoT SiteWise Assistant (GA November 2024) is a generative-AI assistant that summarizes alarms in SiteWise Monitor and answers questions such as "which assets have active alarms". It uses asset hierarchy and history, and pulls SOPs and manuals through Amazon Kendra. It analyses only the customer's own account data. — [AWS What's New](https://aws.amazon.com/about-aws/whats-new/2024/11/aws-iot-sitewise-generative-ai-powered-industrial-assistant)
- Microsoft Factory Operations Agent (Azure AI Foundry, still labelled preview) does natural-language querying over a manufacturing semantic graph in Microsoft Fabric for root-cause analysis. Microsoft says it checks results against the manufacturing data via post-processing, with "Responsible AI guardrails". It reached Copilot Studio and Teams at Hannover Messe 2025. — [Microsoft Learn](https://learn.microsoft.com/pt-br/industry/manufacturing/manufacturing-data-solutions/overview-copilot-factory-operations); [AI Business](https://aibusiness.com/generative-ai/microsoft-launches-new-ai-agents-for-factory-automation-hannover-messe-2025)
- AWS published a multi-agent alarm-flood architecture for power utilities on Bedrock AgentCore. In its example, the agents separate a lightning-induced fault with sympathetic alarms from an unrelated transformer hot-spot. AWS reports "a few minutes" of processing versus a typical 40 to 60 minutes of manual investigation (vendor claim). — [AWS for Industries blog](https://aws.amazon.com/blogs/industries/intelligent-alarm-management-for-power-and-utilities-using-amazon-bedrock-agentcore/)
- Emerson's Ovation AI Alarm Insight Agent collapses alarm floods into prioritized summaries with root causes highlighted (product sheet). — [Emerson PDF](https://www.emerson.com/is/content/emerson/en/systems-and-software/ovation-distributed-control-systems/documents/PWS_011280-Ovation-AI-Alarm-Insight-Agent.pdf)
- Cold-chain vendors: Carrier's Lynx/Lynx Logix is described as AI/ML predictive analytics, not a generative copilot. The Sensitech–Qualcomm (Oct 2024) collaboration covers real-time monitoring and connectivity. I found no generative-AI copilot from Controlant, Sensitech, Tive or Carrier. — [Carrier monitoring page](https://carrier.com/refrigeration/en/worldwide/monitoring); [Pharmaceutical Commerce](https://www.pharmaceuticalcommerce.com/view/sensitech-qualcomm-cold-chain-collaboration)
- Augury reportedly added generative-AI natural-language querying of machine health in 2024. This is low confidence: the source is a third-party business-strategy blog, not Augury. — [businessmodelcanvastemplate.com](https://businessmodelcanvastemplate.com/blogs/growth-strategy/augury-growth-strategy)

**Evidence on agent performance and failure modes**
- AssetOpsBench (IBM Research, arXiv 2506.03828; AAAI) has 141 scenarios (99 single-agent, 42 multi-agent), 2.3M sensor points across 6 assets, 53 FMEA records and 4.2K work orders. It defines four agents: IoT (telemetry retrieval), FMSR (failure-mode to sensor mapping), TSFM (forecasting and anomaly detection with a time-series foundation model) and WO (work orders). An LLM judge scores six dimensions, including hallucination. — [arXiv HTML](https://arxiv.org/html/2506.03828v1); [IBM Research blog](https://researchweb.draco.res.ibm.com/blog/asset-ops-benchmark)
  - Plan-and-Execute paradigm: the best model (mistral-large) reached only 46.5% task completion. granite-3-8b and llama-3-70b exceeded 63% hallucination, and llama-4-maverick hit 47% hallucination. In the Tools-as-Agent (ReAct-style) setup, llama-4-maverick's hallucination was 11%. The authors say plan-and-execute "struggles with long-horizon sequencing, even for frontier models." — [arXiv HTML](https://arxiv.org/html/2506.03828v1)
  - Removing in-context examples dropped gpt-4.1 from 80% to 34% and granite-3-8b from 60% to 3% on 65 single-agent tasks, so performance depends heavily on worked examples. — [arXiv HTML](https://arxiv.org/html/2506.03828v1)
  - Failure analysis of 881 trajectories found "overstatement of task completion" (claiming success that did not happen) in 122 cases (23.8%), extraneous or ambiguous output formatting in 110 (21.4%), and ineffective error recovery in 160 cases. — [arXiv HTML](https://arxiv.org/html/2506.03828v1)
  - The LLM judge itself was only 69 to 75% accurate against four human experts (κ 0.44 to 0.55). — [arXiv HTML](https://arxiv.org/html/2506.03828v1)
  - Secondary blogs claim no model met an "85-point deployment readiness threshold" and that accuracy fell from 68% single-agent to 47% multi-agent. I could not verify this against the paper, so treat it as unverified. — [SoftwareSeni blog](https://www.softwareseni.com/beyond-leaderboards-domain-specific-ai-benchmarks-that-reflect-real-world-deployment-risk)
- OpenRCA (ICLR 2025, Microsoft/CUHK-SZ/Tsinghua) has 335 real failures and 68 GB of logs, metrics and traces. Even with a purpose-built RCA agent that uses Python for data retrieval, the best model (Claude 3.5) solved only 11.34% of cases. — [ICLR 2025 paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/d29b8d53678015079e1d245c023e49d2-Paper-Conference.pdf); [mlanthology](https://mlanthology.org/iclr/2025/xu2025iclr-openrca)
- OpenRCA 2.0 (2026 preprint, 500 instances, 11 frontier LLMs) found the exact root-cause set in only 20.7% of cases on average. Agents named at least one correct root-cause service in 76.0% of cases, but grounded it in a verified causal path in only 61.5%. Partially right answers are common; fully right, causally justified answers are rare. — [Emergent Mind summary of arXiv 2606.27154](https://www.emergentmind.com/papers/2606.27154)
- A vendor critique argues OpenRCA labels can be ambiguous: for example, a metric sits near 98% before, during and after the fault, and anomalies surface across 13 components. Benchmark scores are an imperfect proxy (vendor analysis, not peer-reviewed). — [Traversal blog](https://www.traversal.com/blog/openrca-isnt-root-cause-analysis-why-that-matters)

**Guardrails documented by vendors or benchmarks**
- These measures recur across vendor products and benchmark findings:
  - Ground answers only in the customer's own data and documents (AWS).
  - Post-process and verify outputs against source data (Microsoft).
  - Have an administrator restrict which request types the assistant answers (IBM).
  - Let operators accept, reject or annotate each AI recommendation. This is human-in-the-loop, seen in Cassidy's SCADA triage agent.
  - [AWS](https://aws.amazon.com/about-aws/whats-new/2024/11/aws-iot-sitewise-generative-ai-powered-industrial-assistant); [Microsoft Learn](https://learn.microsoft.com/pt-br/industry/manufacturing/manufacturing-data-solutions/overview-copilot-factory-operations); [IBM Docs](https://www.ibm.com/docs/SSLPL8_cd/com.ibm.mam.doc/aiconfiguration/c_max_assist.html); [Cassidy](https://www.cassidyai.com/solutions/ai-scada-alert-triage-agent)

### Inferences
- The tasks agents demonstrably do in shipped products are bounded language tasks: alarm summarization, NL query over a curated data model, failure-code suggestion, SOP/manual retrieval, and work-order drafting. Autonomous diagnosis is where the benchmarks show the poorest results. For ThermoTwin, the useful LLM jobs are:
  - turning model outputs into a plain-language explanation in Hindi or the local language;
  - drafting a maintenance ticket or incident report;
  - answering "what should I do?" from a fixed SOP library (for example, India's UIP cold-chain handbook).
- AssetOpsBench's 23.8% "overstated completion" maps directly to a cold-chain risk: an agent reporting "vaccines moved to backup fridge" or "technician notified" when the tool call failed. Every action claim must be checked against a tool return value.
- Recommended guardrails for ThermoTwin, synthesized from the above:
  - **Deterministic detection.** Thresholds and the ML model raise alarms. The LLM can never suppress, downgrade or delay an alarm.
  - **Constrained output.** The LLM picks a cause from a fixed taxonomy (door left open, power cut, compressor fault, overloading, wrong thermostat setting, high ambient, sensor fault) and must cite the feature values that support it.
  - **Code does the numbers.** All numbers (excursion duration, minutes above 8 °C, forecast time-to-breach) are computed by code and inserted into templates, never generated by the LLM.
  - **Human confirmation before acting.** Any action with consequences (discarding vaccines, marking stock unusable, escalating to the district officer) requires a human to confirm.
  - **Few-shot examples.** Keep curated worked examples in the prompt, given the 80% to 34% drop when they were removed.

### Gaps
- I found no independent (non-vendor) field evaluation of Siemens, IBM, Microsoft or AWS maintenance copilots measuring diagnostic accuracy or downtime impact.
- I found no published generative-AI copilot from a vaccine or pharma cold-chain monitoring vendor (Controlant, Sensitech, Tive, Berlinger, Nexleaf, etc.). There may be unannounced or regional products.
- The AssetOpsBench per-model Tools-as-Agent numbers (beyond the ones above) and the single- vs multi-agent accuracy comparison sit in charts I could not read. The "68% → 47%" figure is unverified.

## 2. LLMs for time-series reasoning and anomaly explanation: what works, what does not

### Takeaway
The research is consistent: off-the-shelf LLMs are poor at reading raw numeric time series. They perform near chance on time-series reasoning questions, trail specialised anomaly detectors by about 30%, and the LLM part of "LLM forecasters" can often be removed without loss. They help when they work on top of specialised models or computed features: generating rules or code, using domain context, and describing trends that a tool has already extracted. For ThermoTwin, detection and forecasting should stay with conventional ML or rules, and the LLM should get pre-computed, labelled features.

### Cited Findings
- "Are Language Models Actually Useful for Time Series Forecasting?" (Tan et al., NeurIPS 2024) ablated three popular LLM-based forecasters. Removing the LLM, or replacing it with a basic attention layer, did not hurt accuracy. Pretrained LLMs were no better than models trained from scratch, did not capture sequential dependencies, and did not help in few-shot settings. — [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ed5bf446f59e2c6646d23058c86424b-Abstract.html); [arXiv 2406.16964](https://arxiv.org/html/2406.16964v1)
- "Language Models Still Struggle to Zero-shot Reason about Time Series" (Merrill et al., Findings of EMNLP 2024) tested three task types: identifying the scenario that produced a series, answering factual questions about it, and using text context to improve forecasts. Strong LLMs were only slightly better than chance on identification and QA, far below humans, and gained only modestly from context. — [arXiv 2404.11757](https://arxiv.org/abs/2404.11757v1)
- SigLLM, "Large language models can be zero-shot anomaly detectors for time series?" (MIT, arXiv 2405.14755), ran 11 datasets and about 492 univariate series with GPT-3.5-turbo and Mistral. Using the LLM as a forecaster and flagging residuals beat directly prompting it to spot anomalies on all 11 datasets. State-of-the-art deep-learning detectors were still about 30% better than the LLM methods. — [arXiv 2405.14755](https://arxiv.org/html/2405.14755v1); [NVIDIA blog summary](https://developer.nvidia.com/blog/?p=87952)
- "Large Language Models Are Zero-Shot Time Series Forecasters" (Gruver et al., NeurIPS 2023) reported that GPT-3 and LLaMA-2 could zero-shot extrapolate series about as well as purpose-built models. It is the optimistic counterpoint that later ablations (Tan et al.) challenged. — [Liner review of Gruver et al.](https://liner.com/review/large-language-models-are-zeroshot-time-series-forecasters)
- "Towards Time-Series Reasoning with LLMs" (Chow et al., NeurIPS 2024 workshop) put a lightweight time-series encoder in front of a 7B LLM and fine-tuned it on chain-of-thought tasks. It beat GPT-4o on several zero-shot reasoning tasks, which suggests specialised encoders help more than raw text-serialised numbers. — [arXiv 2409.11376](https://arxiv.org/pdf/2409.11376)
- SensorLLM (EMNLP 2025) needed a two-stage alignment to make an LLM useful on motion-sensor data. The stages were sensor–language alignment, using special tokens per channel and auto-generated trend descriptions, then task-aware tuning. The paper names three obstacles: time series lack semantic context, processing them is computationally costly, and LLMs handle raw numbers poorly. — [arXiv 2410.10624](https://arxiv.org/html/2410.10624v4); [ACL Anthology](https://aclanthology.org/2025.emnlp-main.19)
- ATSADBench (aerospace telemetry anomaly detection, 9 tasks, 108K points, arXiv 2601.12448): LLMs did reasonably on univariate signals but struggled on multivariate telemetry, and RAG gave no significant gain over few-shot prompting. The paper also warns that the common "point-adjustment" metric inflates anomaly-detection scores. — [arXiv 2601.12448](https://arxiv.org/html/2601.12448v1)
- Argos (arXiv 2501.14170) is an agentic anomaly-detection design in which the LLM writes detection rules (code) that then run deterministically, rather than judging each point. It uses event-level F1 because plain F1 can look "unreasonably high". — [arXiv 2501.14170](https://arxiv.org/pdf/2501.14170)
- VisualTimeAnomaly / TSAD-Agent (arXiv 2502.17812) tests multimodal LLMs on plotted time series. The authors name reducing hallucinations as an open problem. — [arXiv 2502.17812](https://arxiv.org/pdf/2502.17812)
- TraceBench (ETH Zürich, August 2026) is a controlled benchmark of LLM agents attributing root causes in simulated mechanical systems. Agents "benefit substantially from domain context", mostly explore data through numerical console output rather than plots, and perform worse when they must write a labelling script than when they predict directly. — [arXiv 2608.27182](https://arxiv.org/abs/2608.27182)
- TimeReasoner (arXiv 2505.24511) reports that "slow-thinking" reasoning LLMs have non-trivial zero-shot forecasting ability, mainly for high-level trends and context shifts, not precise values. — [arXiv 2505.24511](https://arxiv.org/html/2505.24511v2)

### Inferences
- For ThermoTwin, do not ask an LLM to read a raw temperature CSV and decide whether an excursion is coming. Use a gradient-boosted model or rules for time-to-breach prediction. Then pass the LLM a compact, labelled evidence packet, for example:
  - "door_open_minutes_last_hour=23"
  - "compressor_current=0A for 47 min"
  - "mains_power=off since 14:05"
  - "ambient=41°C"
  - "slope=+0.9°C/h"
  - "predicted_breach_in=38 min (p=0.82)"
- Ask the LLM only to choose and explain a cause from that packet. This is the configuration the literature supports: tool-extracted features plus domain context.
- Causes in a vaccine fridge are mostly separable by simple signals: power, compressor current, door state and ambient. A rule or decision-tree attribution with SHAP-style feature contributions will be more reliable than LLM "reasoning". The LLM's value-add is language, localisation and SOP retrieval.
- Evaluate with event-level metrics (did we warn before the excursion, and how early; false alarms per fridge per week) rather than point-wise F1, given the metric-inflation warnings.

### Gaps
- I found no paper evaluating LLMs specifically on refrigerator or vaccine cold-chain temperature traces. The closest is a Research Square preprint on door-episode extraction from 500 vaccine fridges in 32 countries, which is not LLM-based. — [Research Square rs-9341655](https://www.researchsquare.com/article/rs-9341655)
- I did not find quantitative hallucination rates for LLM explanations of sensor anomalies (as opposed to agent task benchmarks).

## 3. Multi-agent patterns (monitoring, diagnosis, action/escalation, maintenance planning, report) and published architectures with evaluation

### Takeaway
The best-documented, evaluated architecture is IBM's AssetOpsBench. Its four specialist agents (IoT/telemetry, failure-mode mapping, time-series forecasting/anomaly, work orders) plus an orchestrator map almost one-to-one onto ThermoTwin's proposed monitoring, diagnosis, forecasting and maintenance agents. Its results argue for a single orchestrator calling deterministic tools (ReAct/"tools-as-agent") over an elaborate plan-then-delegate multi-agent system. Other "multi-agent alarm triage" architectures are vendor blog posts without rigorous evaluation.

### Cited Findings
- AssetOpsBench architecture: a global AssetOps orchestrator coordinates the IoT agent (7 tools for asset metadata and telemetry), the FMSR agent (maps sensors to failure modes from FMEA), the TSFM agent (forecasting and anomaly detection with IBM's TTM foundation model) and the WO agent (work orders, alerts, recommendations). — [arXiv HTML](https://arxiv.org/html/2506.03828v1)
- AssetOpsBench compared "Tools-as-Agent" (interleaved ReAct) with "Plan-and-Execute" (decompose first, then delegate). Plan-and-execute struggled with long-horizon sequencing even for frontier models and showed much higher hallucination for several models (above 63% for granite-3-8b and llama-3-70b). — [arXiv HTML](https://arxiv.org/html/2506.03828v1)
- Counter-intuitively, adding 10 out-of-domain "distractor" agents improved performance on the 99 single-agent scenarios. Agent-routing behaviour is not well understood. — [arXiv HTML](https://arxiv.org/html/2506.03828v1)
- The AWS Bedrock AgentCore alarm-management design uses multiple agents to correlate an alarm flood and separate independent root causes. Its time savings are vendor-reported, with no accuracy evaluation published. — [AWS for Industries](https://aws.amazon.com/blogs/industries/intelligent-alarm-management-for-power-and-utilities-using-amazon-bedrock-agentcore/)
- A pulp-and-paper study (Oct 2025) used a locally deployed LLM plus RAG to turn operator questions into structured filters over historical alarm logs and generate structured alarm reports (the "report agent" pattern). It is a system description; no operator evaluation was visible. — [JUTIF paper](https://jutif.if.unsoed.ac.id/index.php/jurnal/article/view/5225)
- IBM positions Maximo Condition Insight and a future "group of AI agents" for end-to-end condition-based maintenance (vendor roadmap). — [IBM](https://www.ibm.com/new/announcements/maximo-condition-insight)

### Inferences
- A defensible ThermoTwin decomposition, ranked by evidence of usefulness and safety:
  1. **Monitoring "agent".** This should not be an LLM: it is a deterministic edge loop (sensor read, features, GBT model, threshold, local alarm). Evidence: LLMs are weak at raw time-series detection (section 2), and alarms must work offline (section 4).
  2. **Diagnosis/explanation agent.** An LLM with tools such as get_recent_features, get_power_status, get_door_events and get_sop(cause). It outputs a JSON object of cause code, confidence, cited evidence values and recommended SOP steps, validated against a schema. This is useful and safe if it is constrained.
  3. **Action/escalation agent.** Keep the escalation ladder as deterministic rules (who to call, after how many minutes, by which channel). The LLM may phrase the message but must not decide whether to escalate. AssetOpsBench's "overstated completion" failure mode is the main hazard here.
  4. **Maintenance-planning agent.** A good fit for an LLM: drafting a repair ticket (symptoms, likely fault such as compressor or thermostat, parts, history) for the cold-chain technician to review. This mirrors IBM's failure-code suggestion and work-order drafting features.
  5. **Report agent.** A good fit: weekly or monthly fridge-health summaries in the local language for the medical officer or district cold-chain officer, generated from computed statistics.
- For a hackathon, one orchestrator LLM with 5 to 8 typed tools will likely be more reliable and easier to demo than five separate LLM agents, given AssetOpsBench's planning and multi-agent findings. The "multi-agent" framing can still be shown as logical roles.

### Gaps
- I found no peer-reviewed evaluation of a multi-agent LLM system for refrigeration, HVAC or cold-chain incident response with field data.
- I found no operator or user study measuring whether LLM explanations change technician response time or correctness in industrial alarm handling.

## 4. Edge deployment: tree models and small NNs on Raspberry Pi / ESP32 / MCUs; offline-first; store-and-forward; connectivity in India

### Takeaway
Small gradient-boosted or random-forest models fit easily on an ESP32: they convert to dependency-free C and run in tens to hundreds of microseconds. TFLite Micro's runtime needs about 16 KB on a Cortex-M3. Compute is not the constraint; power, connectivity and maintenance are. India's government eVIN loggers already show the proven low-resource pattern: a SIM-based logger with local alarm, a 10-minute measurement cycle, hourly GPRS upload, SMS fallback, battery backup and dual SIM. LoRaWAN (865 to 867 MHz, licence-free) suits private village-scale networks, but NB-IoT and LTE-M rural coverage in India is thin.

### Cited Findings
**On-device inference**
- "Boosted Trees on a Diet" (arXiv 2510.26557) measured LightGBM on a XIAO ESP32-S3 at 17.63 µs per prediction for a 4-tree, depth-4 model. The authors' own compact method took 137 µs (about 0.14 ms). Both are negligible compared with a sensor sampling period of minutes. — [arXiv 2510.26557](https://arxiv.org/pdf/2510.26557)
- emlearn converts scikit-learn decision trees, random forests and extra-trees (classifier and regressor) into portable C99. The code needs no libc and no dynamic allocation, ships as a single header, and is tested on AVR ATmega, ESP8266, ESP32, ARM Cortex-M (STM32), Linux, macOS and Windows. Model cost scales with the number of trees and their depth. — [emlearn docs](https://emlearn.readthedocs.io/en/latest/tree_based_models.html); [PyPI](https://pypi.org/project/emlearn)
- Treelite generates C source from XGBoost models and compiles them, with branch-prediction annotation and quantization. Its published benchmarks are server-class (AWS c5.18xlarge), not MCU. — [Treelite benchmark docs](https://treelite.readthedocs.io/en/0.91/benchmark.html)
- Tree ensembles are "far more energy efficient and require much less memory and compute than deep learning methods", which makes them better suited to embedded systems. — [PACSET, arXiv 2011.05383](https://arxiv.org/pdf/2011.05383)
- The TensorFlow Lite Micro core runtime fits in 16 KB on an Arm Cortex-M3 and needs no OS, standard library or dynamic allocation. ESP32-DevKitC and ESP-EYE are supported boards. — [TensorFlow Lite Micro docs](https://www.tensorflow.org/lite/microcontrollers?hl=pt)
- In the TFLM paper, the interpreter is under 2 KB, total framework memory is at most 13 KB for small conv/hotword models and 26.5 KB for a visual wake-words model, and interpreter overhead is under 0.1% to 4% of inference cycles. — [arXiv 2010.08678](https://arxiv.org/pdf/2010.08678)

**Offline-first / store-and-forward**
- AWS IoT Greengrass v2 Stream Manager is designed for "intermittent or limited connectivity". It has per-stream local-disk storage, retention policies and export priorities, so critical streams upload first after reconnecting. — [AWS Greengrass v2 docs](https://docs.aws.amazon.com/greengrass/v2/developerguide/manage-data-streams.html)
- The Greengrass MQTT spooler is by default an in-memory 2.5 MB cache that drops the oldest messages when full, and it drops QoS 0 messages while offline unless configured otherwise. It is not durable store-and-forward on its own. — [AWS re:Post thread](https://repost.aws/it/questions/QUaMSDu7d6T6iHFKa5zOZcAA/guaranteed-delivery-of-events-with-intermittently-offline-device); [Greengrass resilience docs](https://docs.amazonaws.cn/en_us/greengrass/v1/developerguide/disaster-recovery-resiliency.html)
- AWS IoT Greengrass v1 support ended on 7 October 2026, so new designs should not target v1. — [AWS Greengrass v1 docs](https://docs.aws.amazon.com/greengrass/v1/developerguide/stream-manager.md)

**India field pattern: eVIN loggers**
- eVIN SIM-enabled temperature loggers take a reading every 10 minutes and update the server every 60 minutes over GPRS. On a breach, the logger sounds an alarm and sends SMS and email to cold-chain technicians and managers. — [Vikaspedia eVIN](https://en.vikaspedia.in/viewcontent/health/health-care-innovations/health-system-strengthening-1/evin-project-of-health-ministry-health-system-strengthening-1-1?lgn=en)
- eVIN logger design features for poor infrastructure: 24-hour battery backup for frequent power failures, and dual-SIM loggers for patchy network. Alert thresholds: ILR above +8 °C or below +2 °C, and deep freezer above −15 °C. — [Ahmedabad Smart City eVIN document](https://smartnet.niua.org/sites/default/files/e-vin_health_by_ahmedabad_smartcity_.pdf)
- A field quote: "if there's a power failure, the alarm rings and we get an SMS". Workers also report thin maintenance budgets (cited as Rs 1,500 per district per year for deep-freezer maintenance) and too few cold-chain handler posts. — [Governance Now](https://www.governancenow.com/gov-next/egov/the-shot-just-got-smarter-evin-vaccine-immunisation)

**Connectivity options in India**
- The 865 to 867 MHz band is licence-free in India for LPWAN such as LoRaWAN. The IN865 plan reportedly has three default channels (865.0625, 865.4025 and 865.985 MHz), with 30 dBm ERP max and a 1%/hour duty cycle. Generic "868 MHz" modules may default to channels outside India's allowed range. These are vendor-blog figures not checked against WPC/DoT text. — [Zbotic LPWAN comparison](https://zbotic.in/nb-iot-vs-lte-m-vs-lora-low-power-wan-comparison-for-india-2025/); [ThinkRobotics LoRaWAN India guide](https://thinkrobotics.com/blogs/learn/lorawan-gateway-setup-india-complete-deployment-guide-for-2025)
- A private LoRaWAN gateway reportedly costs Rs 10,000 to 20,000 and can cover a village (vendor claim). — [ThinkRobotics](https://thinkrobotics.com/blogs/learn/lorawan-gateway-setup-india-complete-deployment-guide-for-2025)
- NB-IoT (Jio "JioThings", Airtel) is reportedly concentrated in metros and smart-city projects, sparse in Tier-2/3 and rural areas. LTE-M is "not widely available" on Indian networks. Both claims come from vendor blogs, with no operator confirmation found. — [Zbotic](https://zbotic.in/nb-iot-vs-lte-m-vs-lora-low-power-wan-comparison-for-india-2025/); [Electromaker nRF9160 + Airtel NB-IoT test](https://www.electromaker.io/project/view/testing-nb-iot-connectivity-in-india-with-nrf9160-and-airtel)

### Inferences
- Recommended ThermoTwin edge architecture (low cost, offline-first):
  - **Node.** ESP32 (about USD 3 to 5 class) with a temperature probe, door reed switch and SCT-013 CT. Computes features every 1 to 10 minutes.
  - **On-device model.** Runs a small GBT/RF classifier (emlearn or m2cgen C code) for "excursion likely within N minutes".
  - **Local alarm without the network.** A buzzer or LED fires immediately, with no dependence on network or cloud.
  - **Durable local buffer.** Logs to flash or SD as a ring buffer.
  - **Uplink.** Either a GSM/2G-4G modem (SIM800/A7670-class; SMS works where data does not) or LoRa to a Raspberry Pi or ESP32 gateway at the PHC.
  - **Gateway.** Runs a durable queue (store-and-forward) and syncs to the cloud when connected.
  - **Cloud-only components.** The LLM explanation and report agents run in the cloud. Their output is a "nice to have" layered on top of the alarm and must never be on the critical path.
- The eVIN design (10-minute measurement, hourly upload, SMS on breach, battery backup, dual SIM) is a validated template ThermoTwin can cite. ThermoTwin's differentiator is prediction (warning before the threshold is crossed) and cause attribution, not basic logging.
- Note for the pitch: PHCs already have government eVIN loggers. Position ThermoTwin as an add-on (predictive layer, cause explanation, fridges not covered by eVIN) rather than a replacement.

### Gaps
- I found no published latency or memory benchmark specifically for m2cgen- or Treelite-generated code on ESP32, or for LightGBM/XGBoost on a Raspberry Pi. They are expected to be trivial but should be measured.
- I did not verify Edge Impulse's current support for tree models or anomaly blocks on MCUs.
- I found no operator-published NB-IoT/LTE-M coverage maps for rural India, nor eVIN uptime or data-loss statistics.
- I found no data on power-outage frequency at Indian PHCs within this research scope.

## 5. Low-cost sensor hardware and accuracy vs WHO PQS requirements

### Takeaway
The WHO PQS 30-day fridge logger specification requires ±0.5 °C (−20 to +20 °C), 0.2 °C resolution, measurement every ≤10 min, and specific alarm rules (high: ≥ +8 °C for 10 h; low: ≤ −0.5 °C for 60 min). A DS18B20 nominally meets ±0.5 °C but with no margin. An SHT31 (±0.2 °C typical, 0 to 90 °C) is better for the 2 to 8 °C range, but neither is a certified device. ThermoTwin should present itself as a predictive add-on, not a PQS-compliant logger, and should calibrate against a reference.

### Cited Findings
- WHO PQS E006/TR06.3 (30-day electronic refrigerator logger, 2010):
  - Accuracy: ±0.5 °C or better within −20 to +20 °C for 12 months after calibration, and ±1.0 °C after 12 months without recalibration.
  - Resolution: 0.2 °C or better.
  - Operating range: −20 to +50 °C.
  - Measurement and logging: measure at ≤10-minute intervals, log at ≤1-hour intervals, over 30 days.
  - Factory-set alarms: low at a single event of −0.5 °C or below for 60 minutes; high at a single event of +8 °C or above for 10 hours.
  - Calibration must be traceable to an ISO/IEC 17025 lab or NIST.
  - Physical: IP64 and a non-replaceable battery with at least two years' life.
  - [WHO PQS E006/TR06.3 PDF](https://extranet.who.int/prequal/sites/default/files/document_files/PQS_E006_TR06.3.pdf)
- A newer revision, E006/TR06.4 (January 2022), exists. I did not read it, so values may have changed. — [WHO PQS TR06.4 page](https://extranet.who.int/prequal/key-resources/documents/pqs-performance-specification-e006tr064-30-day-electronic-refrigerator)
- WHO-prequalified remote temperature monitoring devices (RTMDs) declare ±0.5 °C accuracy: My Fridge Online VM1000 (E006-061), Berlinger SmartMonitor SITE L (E006-087), and Haier U-COOL / U-COOL Pro (E006-060/078, under spec E006/TR03.2). Several listings showed validity to 31 May 2026, so their current status should be rechecked. — [E006-061](https://extranet.who.int/prequal/sites/default/files/immunization_devices/pdf/e006/E006-061.pdf); [E006-087](https://extranet.who.int/prequal/sites/default/files/immunization_devices/pdf/e006/E006-087.pdf); [E006-078](https://extranet.who.int/prequal/sites/default/files/immunization_devices/pdf/e006/E006-078.pdf)
- A commercial example: the LogTag VaxTag is certified to E006/TR06.3 with accuracy better than ±0.5 °C from −20 to +40 °C. — [LogTag VaxTag datasheet](https://www.cik-solutions.com/content/files/en_datasheet_logtag_vaxtag_1.pdf)
- DS18B20 (1-Wire digital): ±0.5 °C only over −10 to +85 °C; the operating range is −55 to +125 °C. Analog Devices says the ±0.5 °C figure includes ADC error and drift. Resolution (9 to 12 bits) changes reported bits, not accuracy. — [Analog Devices KB](https://support.analog.com/en-US//knowledgebase/article/000095991); [DigiKey listing](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/DS18B20-T-R/1197286)
- One hobbyist forum anecdote reports individual DS18B20 units deviating far more than spec (likely counterfeit or clone parts). This is not systematic evidence. — [Arduino forum](https://forum.arduino.cc/t/calibratore-ntc-con-ds18b20/1173808)
- Sensirion SHT31 (I²C, temperature and humidity): temperature ±0.2 °C typical over 0 to 90 °C (±0.3 °C in some distributor listings), humidity ±2 %RH, operating range −40 to 125 °C. — [DFRobot SHT31 wiki](https://wiki.dfrobot.com/SHT31%20Digital%20Temperature%20and%20Humidity%20Sensor%20SKU%3A%20SEN0331); [RS Components](https://ie.rs-online.com/web/p/temperature-humidity-sensor-ics/8765061P)
- SCT-013 split-core current transformer (non-invasive clamp for detecting compressor running): the SCT-013-060 lists ±1% accuracy and ≤0.2% linearity, and the SCT-013-015 lists ±1%. Indian retailers sell 5 A to 100 A variants. Low-current linearity favours choosing a low-range variant (5 to 20 A) for a small fridge compressor. — [Zbotic SCT-013-060](https://zbotic.in/product/sct-013-060-non-invasive-ac-current-sensor-clamp-sensor-60a/); [Robu.in](https://robu.in/?p=618494)

### Inferences
- **Probe choice.** For 2 to 8 °C ILR/fridge monitoring, an SHT31 or a calibrated DS18B20 is adequate for prediction research. For −15 to −25 °C freezers, the DS18B20 falls outside its ±0.5 °C band (−10 °C lower limit). The SHT31's ±0.2 °C typical band also starts at 0 °C. Both would need calibration or a different probe (for example, a PT100/PT1000 RTD) for freezer compliance.
- **Measure the vaccine, not the air.** Use a probe in a glycol or buffer vial to mimic vaccine load temperature rather than air temperature. Air spikes during door openings cause false alarms. WHO TR06.3 requires positioning that "accurately measures the load temperature."
- **Cause signals.** Combine temperature with:
  - a door reed switch (binary door-open events);
  - an SCT-013 clamp on the fridge supply (compressor duty cycle; a stuck compressor shows 0 A or continuous running);
  - mains-power detection (an optocoupler or the CT itself).
  These signals make cause attribution almost rule-based (door, power, compressor or thermostat), which is safer than LLM inference.
- **Alarm rules.** Mirror WHO alarm logic (+8 °C for 10 h cumulative-style high alarm; −0.5 °C for 60 min freeze alarm) as ThermoTwin's "ground truth" rules, then add earlier predictive warnings. Freeze exposure is particularly damaging for freeze-sensitive vaccines, which the low-alarm rule reflects.

### Gaps
- Thermocouple specs: K-type standard tolerance is commonly cited as about ±2.2 °C, and MAX31855-type amplifiers as about ±2 °C. I did not verify a source this session. Thermocouples are in any case too inaccurate for 2 to 8 °C compliance.
- I did not find a WHO PQS requirement text for RTMDs (E006/TR03) in readable form, only product declarations.
- I found no accuracy data for counterfeit or clone DS18B20s common in Indian hobby markets beyond anecdotes.

## 6. Alert delivery in India: SMS, WhatsApp Business API, IVR voice in local languages; evidence on which channels get responses

### Takeaway
The cold-chain system India already uses (eVIN) relies on local audible alarms plus SMS and email to technicians and managers, and field reports suggest health workers notice them. There is good Indian evidence on voice/IVR reach from Kilkari, the national maternal mHealth programme: about half of calls are answered on the first attempt and nearly all by the ninth, so retries matter. ASHAs use WhatsApp heavily and informally. I found no head-to-head study comparing SMS, WhatsApp and IVR response for cold-chain alerts. A layered strategy (local buzzer, then SMS, then voice call with retries, then WhatsApp for rich detail) is best supported. Commercial SMS requires TRAI DLT template registration.

### Cited Findings
- eVIN breach alerts go by SMS and email to cold-chain technicians and managers, with a local alarm. A health worker said "if there's a power failure, the alarm rings and we get an SMS". — [Vikaspedia](https://en.vikaspedia.in/viewcontent/health/health-care-innovations/health-system-strengthening-1/evin-project-of-health-ministry-health-system-strengthening-1-1?lgn=en); [Governance Now](https://www.governancenow.com/gov-next/egov/the-shot-just-got-smarter-evin-vaccine-immunisation)
- In a peer-reviewed pre/post study, eVIN raised the share of facilities updating vaccine stock daily from 38.6% to 53.5% and substantially improved completeness of temperature logbooks and other records. It reported no alert-response-time data. — [PMC7643996](https://pmc.ncbi.nlm.nih.gov/articles/PMC7643996)
- Kilkari IVR (national, multi-state, Hindi and other languages), 2018 cohort across 13 states: 50% of calls were picked up on the first attempt, 76% by the third and 99.5% by the ninth. Of answered calls, about 48% were listened to for at least 50% of the content and 43% for at least 75%. A picked-up call may be answered by another family member. — [arXiv 2311.07139](https://arxiv.org/pdf/2311.07139)
- A Kilkari RCT in Madhya Pradesh (5,095 women) found 65% of the intervention arm listened to at least 50% of the content of answered calls. — [PMC9288869](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9288869/)
- A field trial with about 6,500 Kilkari participants found that a collaborative bandit algorithm for call timing significantly improved pickup over random call times. Call timing matters. — [PMLR v298 (Dasgupta et al. 2025)](https://proceedings.mlr.press/v298/dasgupta25a.html)
- ASHAs use WhatsApp extensively for work: groups, clinic announcements and countering misinformation. A Varanasi qualitative study (22 CHWs, PLOS Global Public Health 2025) asks whether WhatsApp adds to an already heavy ASHA workload ("More work for ASHAs?"). — [CHW Central PDF](https://chwcentral.org/wp-content/uploads/More-work-for-ASHAs-Exploring-the-role-of-whatsapp-messaging-and-community-health-work-in-urban-slum-areas-of-Varanasi-India.pdf); [MIT Technology Review](https://www.technologyreview.com/2023/02/03/1067726/indian-healthcare-workers-ashas-whatsapp-misinformation-pregnancy/)
- Microsoft Research's ASHABot is a Hindi-capable WhatsApp LLM chatbot answering health questions for ASHAs in rural Rajasthan. It is a precedent for LLM assistants reaching frontline workers via WhatsApp. — [Microsoft Research](https://www.microsoft.com/en-us/research/?p=1141120)
- Health-worker digitisation brings data-entry burden: ASHAs report spending more time entering data on phones than serving communities, yet value WhatsApp. — [HIFA mHealth-Innovate](https://hifa.org/node/96855482); [Ideas for India](https://ideasforindia.in/topics/productivity-innovation/is-digitalisation-a-double-edged-sword-for-workers-in-indias-public-healthcare-system.html)
- TRAI DLT rules: all commercial SMS in India require registration of the entity, the sender header and the exact content template. Messages that do not match an approved template are blocked by network-level scrubbing. Only Indian entities can register, and one registration covers all operators. — [Telerivet guide](https://www.telerivet.com/blog/india-sms-compliance-trai-dlt-registration-and-tcccpr-guide); [Plivo support](https://old-support.plivo.com/hc/en-us/articles/360046769131-DLT-Registration-Process-for-Sending-SMS-to-India)
- WhatsApp Business Platform moved to per-message pricing on 1 July 2025. Reported India utility-template prices conflict: about ₹0.11 to ₹0.115 per message (Exchange4media) versus ₹0.13 (MyOperator). Utility templates sent inside the 24-hour customer-service window are free. Meta's current rate cards are effective 1 April 2026, so 2025 figures may be stale. — [Exchange4media](https://www.exchange4media.com/marketing-news/whatsapp-introduces-permessage-billing-for-business-messaging-144935.html); [MyOperator](https://support.myoperator.com/portal/en/kb/articles/whatsapp-has-shifted-to-per-message-pricing-effective-july-1-2025-based-on-message-categories-and-your-recipient-s-country-in-india-there-are-three-paid-categories); [Meta pricing docs](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing); [Chakra HQ](https://chakrahq.com/article/pricing-updates-for-whatsapp-business-platform-effective-july-2025-onwards/)

### Inferences
- Suggested escalation ladder for ThermoTwin:
  1. **Local buzzer or LED.** Works offline and without power for the network.
  2. **SMS to the cold-chain handler.** Uses a DLT-registered template with fridge ID, temperature, predicted time-to-breach and cause code. SMS works on feature phones and 2G.
  3. **Automated voice call in Hindi or the regional language** if there is no acknowledgement (a reply SMS or missed-call acknowledgement) within N minutes. Retry up to 3 to 5 times, given Kilkari's 50% first-attempt and 76% third-attempt pickup.
  4. **Escalation to the Medical Officer, then the district cold-chain officer.**
  5. **WhatsApp message** with an LLM-written explanation and SOP steps (and a chart image) as an enrichment channel, not the primary alarm. It depends on smartphone and data and costs per template outside the 24-hour window.
- LLM-written text cannot go into SMS freely because DLT requires exact template matches. The LLM's explanation fits WhatsApp or app channels. SMS must use pre-registered templates with variable slots (a fixed cause-code vocabulary helps here too).
- Keep alerts for ASHAs minimal. ASHAs are not usually the cold-chain handlers (ANMs, pharmacists or designated handlers are), and the literature flags digital overload.

### Gaps
- I found no study comparing SMS, WhatsApp and IVR response rates or response times for cold-chain or equipment alerts among Indian health staff, and no eVIN alert-acknowledgement or response-time data.
- I did not verify current India IVR or voice-call API costs or DLT rules for voice (TRAI rules mainly target SMS and promotional calls).

## 7. Privacy, safety and regulatory considerations for AI decision support in medicine storage (brief)

### Takeaway
Temperature telemetry is not personal data, but health-worker phone numbers and names in an alert system are, so India's DPDP Act and Rules apply (core obligations from about May 2027). WHO's 2024 LMM guidance calls for oversight, independent auditing and stakeholder involvement. The main safety principle is that AI must not replace the certified logger or the human decision to discard or use vaccines.

### Cited Findings
- WHO's *Ethics and Governance of AI for Health: Guidance on Large Multi-Modal Models* (January 2024) has 40+ recommendations. They include assigning a regulator to assess LMMs for health use, mandatory post-release auditing and impact assessment by independent third parties for large-scale deployments, and involving health professionals and affected people from early development. — [WHO news release](https://www.who.int/news/item/18-01-2024-who-releases-ai-ethics-and-governance-guidance-for-large-multi-modal-models)
- India's Digital Personal Data Protection Rules 2025 were notified on 13 to 14 November 2025 and phase in over 12 to 18 months. Data Protection Board provisions apply immediately, consent-manager provisions after one year, and most consent, notice and processing obligations after 18 months (about 13 to 14 May 2027). — [PIB document](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf); [The Week/PTI](https://www.theweek.in/wire-updates/business/2025/11/14/del148-biz-dpdp-rules-ld-govt.html)
- WHO PQS sets device-level performance requirements (accuracy, alarms, calibration traceability) for cold-chain temperature monitoring equipment used in immunization programmes. — [WHO PQS E006/TR06.3](https://extranet.who.int/prequal/sites/default/files/document_files/PQS_E006_TR06.3.pdf)

### Inferences
- **Keep the certified record separate.** The PQS/eVIN logger remains the official record. ThermoTwin's predictions and explanations are advisory decision support.
- **No discard recommendations.** ThermoTwin should never recommend discarding or using vaccines on its own. Those decisions follow national guidelines (VVM status, shake test, excursion duration), and the system should only point to the relevant SOP with a human sign-off.
- **Data minimisation.** Store only role, phone number and facility for alert recipients; get consent and allow opt-out (DPDP).
- **Self-hosting the LLM.** If explanation text is generated by a cloud LLM, send only telemetry features and fridge IDs, never personal data. Alternatively, self-host a small model.
- **Audit trail.** Log every AI explanation alongside the raw evidence and the human action taken. This supports the auditability WHO's guidance emphasises, and lets the team measure explanation correctness later.

### Gaps
- I did not research CDSCO's position on whether cold-chain monitoring software counts as a medical device (likely not, since it does not diagnose patients). This needs confirmation if commercialising.
- I did not review the full WHO LMM guidance text on human-oversight wording, or India-specific AI health guidance (for example ICMR's 2023 ethical guidelines for AI in health).
