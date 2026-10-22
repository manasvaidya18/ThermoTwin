# Alarm management, alarm fatigue and false alarms in cold-storage temperature monitoring (for ThermoTwin's alert policy)

Research date: 11 October 2026. "(secondary)" marks a vendor, trade-press, review or aggregator source rather than the original standard or study. Several standards (ISA-18.2, IEC 62682, EEMUA 191) are paywalled. Their figures here come from published summaries, so check them against the standard text before quoting them as normative.

## 1. What industrial alarm-management standards recommend (ISA-18.2 / IEC 62682 / EEMUA 191)

### Takeaway
The process-industry standards treat an alarm as something that needs an operator response. They set numeric performance targets:
- About 1 alarm per 10 minutes per operator (about 6 per hour, about 150 per day) is "very likely acceptable". About 2 per 10 minutes (about 12 per hour, about 300 per day) is the maximum manageable.
- A flood is 10 or more alarms in 10 minutes.
- Chattering alarms: zero. Stale or standing alarms: fewer than 5 to 10.
- The top 10 alarms should make up 1 to 5% of the load.
- Annunciated priorities should be split about 80% low, 15% medium, 5% high.
- Chattering is fixed with deadbands (temperature about 1% of range) and on-delay or off-delay timers.
- Shelving is time-limited and operator-initiated. "Suppression by design" is driven by the state of the process.

### Cited Findings
**Alarm rate per operator**
- ISA-18.2 recommended frequencies (secondary, Yokogawa / Control Engineering article): about 150 alarms per day per operator is "very likely acceptable" and about 300 per day is "maximum manageable". The hourly equivalents are about 6 and about 12. — [Yokogawa: Implementing Alarm Management per the ANSI/ISA-18.2 Standard](https://www.yokogawa.com/ch/library/resources/media-publications/implementing-alarm-management-per-the-ansi-isa-182-standard-control-engineering/)
- EEMUA 191 steady-state target: fewer than 1 alarm per 10 minutes per operator (about 6 per hour) (secondary). — [Chemical Engineering: Alarm management by the numbers](https://www.chemengonline.com/alarm-management-numbers/)
- Emerson/DeltaV KPI table, which says it is "largely copied from EEMUA 191" (secondary, vendor). It sets targets and action limits:

  | KPI | Target | Action limit |
  |---|---|---|
  | Average alarm rate per operator | 1–2 per 10 min | >3 per 10 min |
  | Alarms per operator per day | <288 | >432 |
  | Alarms per operator per hour | <12 | — |
  | % of 10-minute periods with >10 alarms | <1% | >5% |
  | Stale alarms (active >24 h) | <5 on any day | >5 |
  | Chattering and fleeting alarms | 0 | >5 |
  | Contribution of the top 10 most frequent alarms | <1% to ~5% | >20% |

  — [Emerson: Alarm management by the numbers (PDF)](https://d1-live.emerson.com/documents/automation/article-alarm-management-by-numbers-deltav-en-38292.pdf); [Chemical Engineering reprint](https://www.chemengonline.com/alarm-management-numbers/)
- Sources conflict on the daily rate. ISA-18.2 (as summarised by Yokogawa) gives 150 "very likely acceptable" and 300 "maximum manageable". The Emerson/EEMUA-derived table uses <288 as the target and >432 as the action limit. One vendor page (Zbotic) cites "<1 per minute" as the EEMUA target, which is inconsistent with the other sources and should not be used. — [Yokogawa](https://www.yokogawa.com/ch/library/resources/media-publications/implementing-alarm-management-per-the-ansi-isa-182-standard-control-engineering/); [Emerson](https://d1-live.emerson.com/documents/automation/article-alarm-management-by-numbers-deltav-en-38292.pdf); [Zbotic (unreliable)](https://zbotic.in/scada-alarm-management-best-practices-for-plant-operators/)

**Floods, peaks and standing alarms**
- Flood definition (secondary): ANSI/ISA-18.2 defines a flood as 10 or more annunciated alarms in any 10-minute period per operator. EEMUA 191 defines the start of a flood as a 10-minute period with more than 10 new alarms. — [Chemical Engineering](https://www.chemengonline.com/alarm-management-numbers/); [IChemE Alarm Management Practical Guide (2021)](https://www.icheme.org/media/16019/icheme-alarm-management-practical-guide-06_05_2021.pdf)
- IChemE practical guide (2021), comparing IEC 62682 with EEMUA 191 (secondary):
  - Peak alarm rate in abnormal operation: fewer than 10 alarms in the first 10 minutes.
  - 10-minute periods containing more than 10 alarms: under 1%.
  - Standing (stale) alarms: fewer than 5 under IEC 62682 and fewer than 10 under EEMUA 191.
  - Top 10 alarms: 1–5% of total under IEC. EEMUA has "discussed but no target".

  — [IChemE Alarm Management Practical Guide, 6 May 2021](https://www.icheme.org/media/16019/icheme-alarm-management-practical-guide-06_05_2021.pdf)
- Emerson says ISA-18.2 considers fewer than 10 standing alarms, and fewer than 10 alarms in a 10-minute flood, acceptable (secondary, vendor). — [Emerson Automation Experts: Suppressing plant alarms (2019)](https://www.emersonautomationexperts.com/2019/alarm-management/suppressing-plant-alarms/)
- exida's KPI table gives the top-10 contribution target as "~<1% to 5% max with action plans". One plant's as-found value was 69.8%. — [exida Alarm Management Assessment](https://exida.com/alarm-management/assessment)

**Priority tiers**
- ISA-18.2 recommends an annunciated priority split of about 5% high, 15% medium and 80% low. An exida case study reports a Solvay plant brought into line with "ISA-18.2 recommendations (~5% high, ~15% medium, ~80% low)". — [exida Solvay case study](https://www.exida.com/Case-Study/solvay-plant-reduces-downtime-and-improves-safety-through-alarm-management)
- exida notes the target applies to annunciated (presented) alarms, not configured ones. It also says there is "no direct correlation" between the rationalized and the annunciated priority distribution. — [exida blog: Get your priorities (distribution) straight](https://exida.com/Blog/which-measure-rationalized-or-annunciated-is-more-important)
- ABB lists the same split (high 5%, medium 15%, low 80%) as an EEMUA 191 benchmark (secondary). — [ABB SCADA Alarm Management White Paper](https://library.e.abb.com/public/72f20c70c7b44d889d463db81df5c38d/SCADA%20Alarm%20Management%20White%20Paper.pdf)

**Shelving and suppression**
- ISA-18.2 definitions (secondary):
  - Shelving is a mechanism, usually started by the operator, that temporarily suppresses an alarm. Shelved alarms return after a preset time, and the system must show a list of all shelved alarms.
  - Suppression by design prevents an alarm from reaching the operator, based on plant state or other conditions.

  — [ProcessOnline: Improving alarm management with ISA-18.2, Part 2](https://www.processonline.com.au/content/software-it/article/improving-alarm-management-with-isa-18-2-part-2-1141142642); [WinCC OA alarm shelving docs](https://www.winccoa.com/documentation/WinCCOA/latest/en_US/alarmshelving/topics/alarm_shelving_overview.html)

**Deadbands and delays**
- Recommended alarm deadbands, attributed to EEMUA 191 (secondary): flow 5%, temperature 1%, level 2%, pressure 2%, composition 1%. — [exida: Why should I use an alarm deadband](https://www.exida.com/Blog/why-should-i-use-an-alarm-deadband)
- An academic paper attributes similar values to EEMUA and ISA: flow 5%, temperature 1%, level 5%, pressure 2%. So the two sources conflict on level (2% vs 5%). — [Chattering-alarm paper, ACC 2011 proceedings (PDF)](https://skoge.folk.ntnu.no/prost/proceedings/acc11/data/papers/1100.pdf)
- Chattering alarms are resolved with hysteresis (deadbands) or on-delay and off-delay timers (secondary). — [Chemical Engineering](https://www.chemengonline.com/alarm-management-numbers/)
- Emerson warns that adjusting the deadband works for nuisance alarms, but the deadband should not be set "into the long-term average value". — [Emerson Automation Experts](https://www.emersonautomationexperts.com/2019/alarm-management/suppressing-plant-alarms/)

### Inferences
- If you treat a pharmacy or clinic fridge fleet as an "operator console", the same targets make sense. A clinic nurse or vaccine coordinator, who has other duties, should see far fewer than about 6 actionable alerts per hour across all devices. In practice the target is closer to a handful per week. Any alarm that chatters (repeated set/clear around the threshold) is a design defect.
- The 80/15/5 split suggests ThermoTwin should present most notifications as low-priority advisories (for example, a predicted risk or a trend) and reserve the high tier for confirmed, sustained excursions that threaten product.
- A 1% deadband on a fridge sensor is about 0.1–0.2 °C on a typical span. That is well below the ±0.5 °C accuracy CDC requires (see section 3), so in practice ThermoTwin's hysteresis should be at least the sensor uncertainty.
- Shelving should expire automatically and be listed somewhere, so that a muted fridge is never forgotten. Suppression by design (for example, during a scheduled defrost or a stock-loading window) should be logged, not silent.

### Gaps
- I could not access the text of ANSI/ISA-18.2 (current edition), IEC 62682 or EEMUA 191 (latest edition), so all figures are from secondary summaries. Edition years were not verified.
- I found no authoritative ISA-18.2 table of on-delay and off-delay times by signal type. A forum post says the ISA technical report suggests default delays by process-variable type, but I could not confirm the values (for example, the commonly quoted 60 s for temperature).
- I found no published application of ISA-18.2 KPIs specifically to cold-chain or fridge-monitoring fleets.

## 2. Evidence of alarm fatigue in clinical settings

### Takeaway
The Joint Commission's Sentinel Event Alert 50 (8 April 2013) is the anchor source. It estimates that 85–99% of alarm signals do not require clinical intervention, partly because thresholds are set too tight or left at defaults. It names alarm fatigue as the most common contributing factor in 98 alarm-related sentinel events (80 deaths). The often-quoted "72–99% false" range comes from Sendelbach & Funk (2013). Drew et al. (2014) logged 2.56 million alarms in 31 days in five ICUs and found 88.8% of annotated arrhythmia alarms were false positives.

### Cited Findings
**The Joint Commission, Sentinel Event Alert Issue 50, 8 April 2013 ("Medical device alarm safety in hospitals"; primary)**
- "The number of alarm signals per patient per day can reach several hundred", which means "tens of thousands of alarm signals throughout the hospital every day".
- "between 85 and 99 percent of alarm signals do not require clinical intervention". Listed causes include "alarm conditions are set too tight; default settings are not adjusted for the individual patient… or sensors are mispositioned".
- The Sentinel Event database recorded 98 alarm-related events between January 2009 and June 2012. Of these, 80 resulted in death, 13 in permanent loss of function and 5 in unexpected additional care. 94 occurred in hospitals.
- Contributing factors (counts):
  - absent or inadequate alarm system: 30
  - improper alarm settings: 21
  - alarm signals not audible in all areas: 25
  - alarm signals inappropriately turned off: 36
- "Alarm fatigue – the most common contributing factor" among other factors identified.
- The FDA MAUDE database recorded 566 alarm-related patient deaths between January 2005 and June 2010.
- Since 2007, ECRI Institute has listed clinical alarm conditions as the first or second hazard on its Top 10 Health Technology Hazards list.
- Recommendations:
  - Leadership-owned alarm management.
  - An inventory of alarm-equipped devices and their default settings.
  - Guidelines for alarm settings, including "identification of situations when alarm signals are not clinically necessary".
  - Guidelines for tailoring limits.
  - Inspection and maintenance.
  - Training.
  - A cross-disciplinary team with "continual improvement and constant optimizing of alarm system policies and configurations".

— [The Joint Commission, Sentinel Event Alert 50 (PDF)](https://digitalassets.jointcommission.org/api/public/content/f65e5c9df2b94000a99445e0a7877007)

**72–99% range (secondary)**
- Sendelbach S, Funk M. "Alarm fatigue: a patient safety concern." *AACN Advanced Critical Care* 2013;24(4):378–386. A later systematic review quotes it as finding "72% to 99.4% of clinical alarms were false alarms". I did not access the original, and some papers cite it as 2014. — [Systematic review of nurses' attitudes to alarm fatigue, citing Sendelbach & Funk (academia.edu)](https://www.academia.edu/98739208/Nurses_Attitudes_Related_To_Alarm_Fatigue_in_Critical_Care_Units_A_Systematic_Review)

**Drew BJ et al., "Insights into the Problem of Alarm Fatigue with Physiologic Monitor Devices", *PLOS ONE*, 22 October 2014 (doi 10.1371/journal.pone.0110274)**
- Setting: 461 adults in 5 UCSF ICUs over 31 days.
- 2,558,760 unique alarms in total: 1,154,201 arrhythmia, 612,927 parameter and 791,632 technical.
- 381,560 audible alarms, an audible burden of 187 per bed per day.
- 88.8% of 12,671 annotated arrhythmia alarms were false positives. This applies to the annotated sample, not to all arrhythmia alarms.
- Causes: "inappropriate user settings, patient conditions, and algorithm deficiencies".

— [PMC4206416](https://pmc.ncbi.nlm.nih.gov/articles/PMC4206416); [UCSF news release, Oct 2014](https://www.ucsf.edu/news/2014/10/119601/hospital-logs-staggering-25-million-alarms-just-month)

**Other clinical studies**
- Görges, Markewitz & Westenskow, *Anesthesia & Analgesia* 2009 (ICU time-motion study): clinicians ignored 41% of alarms (secondary). — [AHRQ PSNet summary](https://psnet.ahrq.gov/issue/improving-alarm-performance-medical-intensive-care-unit-using-delays-and-clinical-context)
- Review by Arora et al. (arXiv 2302.03885, 2023; secondary):
  - Only 5–13% of ICU alarms were actionable.
  - One quarter of monitored patients generated two thirds of alarms.
  - In another study, 2% of patients produced 77% of false arrhythmia alarms.
  - Fewer than 26% of alarms were clinically significant (citing Paine et al., *J Hosp Med* 2016;11(2):136–144).

  — [Arora et al., Classification of Methods to Reduce Clinical Alarm Signals (arXiv)](https://arxiv.org/pdf/2302.03885)

**ECRI hazard lists**
- ECRI's 2015 Top 10 list included "Alarm hazards: inadequate alarm configuration policies and practices" (secondary). — [California Healthline](https://californiahealthline.org/morning-breakout/alarm-fatigue-is-leading-health-care-technology-hazard-facing-hospitals-report-finds)
- ECRI 2025 list, item 6: "Dangerously low default alarm limits on anesthesia units". — [ECRI Top 10 Health Technology Hazards for 2025](https://home.ecri.org/blogs/ecri-events/top-10-health-technology-hazards-for-2025); [MedTech Dive](https://www.medtechdive.com/news/ecri-top-health-tech-hazards-2025-ai/734694/)
- ECRI 2026 list (published January 2026): no alarm-specific item. The closest is #9, "technology designs or configurations that prompt unsafe clinical workflows". — [ECRI 2026 page](https://home.ecri.org/blogs/ecri-events/top-10-health-technology-hazards-for-2026); [MLO summary](https://mlo-online.com/information-technology/news/55352952/ecri-releases-list-of-top-10-healthcare-technology-hazards-for-2026)

**Regulation: Joint Commission NPSG.06.01.01, "Alarm system safety" (secondary)**
- Phase 1 (2014): leaders make alarm safety a priority (EP1, by 1 July 2014) and identify the most important alarm signals (EP2).
- Phase 2 (from 1 January 2016): policies on appropriate settings, when alarms can be disabled, who can change parameters, monitoring and response, and checking alarms (EP3); plus staff education (EP4).

— [Relias Media: New NPSG addresses clinical alarm safety](https://reliasmedia.com/articles/64545-new-npsg-addresses-clinical-alarm-safety); [AHRMM alarm safety management](https://www.ahrmm.org/resource-repository-ahrmm/alarm-safety-management-110314-1)

### Inferences
- ThermoTwin can defensibly say that fixed-threshold alarms with poor configuration cause alarm fatigue in clinical monitoring. Sentinel Event Alert 50 explicitly blames thresholds "set too tight" and defaults "not adjusted", and lists "alarm signals inappropriately turned off" in 36 of 98 sentinel events. The disabling behaviour matters directly for fridges: CDC tells staff not to disconnect a repeatedly sounding alarm (section 3).
- The pitch should not present the 72–99% figure as a cold-chain statistic. It comes from bedside physiologic monitoring. Use it as an analogy and pair it with the cold-chain mechanisms in section 3 (door openings, defrost, unbuffered probes).
- The Joint Commission recommendations map well onto a product feature list:
  - inventory of devices and settings
  - per-unit tailored limits
  - documented rules for when alerts are unnecessary
  - periodic review of alarm trends ("continual improvement… of configurations")

### Gaps
- I could not access the full text of Sendelbach & Funk (2013) to confirm the exact 72% / 99.4% bounds or the studies they pool.
- I found no peer-reviewed study that measures alarm fatigue (desensitisation, delayed response or disabling) for pharmacy or vaccine refrigerator alarms. The cold-chain fatigue argument is by analogy plus mechanism, not a direct measurement.
- I could not confirm the current (2026) wording of NPSG.06.01.01.

## 3. Evidence specific to vaccine and medicine refrigerators (false alarms, CDC/WHO guidance, LMIC RTMD experience)

### Takeaway
Both CDC and WHO build false-alarm control into the measurement itself:
- **CDC (Toolkit, July 2026):** a DDL with an out-of-range alarm and a buffered probe in the centre of the unit, with the display outside so the door stays shut.
- **WHO PQS (30-day temperature recorders, Type 1 configuration):** an alarm only after sustained exposure. The heat alarm needs ≥+8 °C for 10 hours; the freeze alarm needs ≤−0.5 °C for 60 minutes.

Buffering dampens air swings dramatically: one study recorded 1.7–6.2 °C in air against 3.6–4.3 °C in glycol. LMIC remote monitoring evidence (Nexleaf RCT in Mozambique, Belize, India eVIN) shows SMS alerts improve uptime and cut freezing, but it rarely reports how many alarms were false or acted on.

### Cited Findings
**CDC Vaccine Storage and Handling Toolkit, July 2026 edition (primary PDF; page updated 14 July 2026)**
- Digital data logger (DDL) features listed:
  - "Alarm for out-of-range temperature"
  - "Detachable probe that best reflects vaccine temperatures (e.g., a probe buffered with glycol, glass beads, sand, or Teflon®)"
  - low battery indicator
  - current, minimum and maximum temperature display
  - "Recommended uncertainty of ±0.5°C (±1°F)"
  - logging interval programmable to record temperatures "at least every 30 minutes"
- "Many DDLs use a buffered temperature probe… In contrast, standard thermometers typically measure air temperature."
- Placement: "Place the buffered probe of the DDL in the center of the unit with the vaccines surrounding it. A device placed near the unit's walls, floor, vent, ceiling, or door may indicate temperatures that are colder or warmer than the actual vaccine temperature." Also: "Place the DDL's active digital display outside the unit so temperatures can be read without opening the door".
- Routine checks: "At the start of each workday, check and record minimum and maximum temperatures". If the device has no min/max, read the current temperature at least twice per workday.
- Excursion response:
  1. Any staff member who hears an alarm notifies the primary or backup vaccine coordinator or a supervisor.
  2. Label the vaccines "DO NOT USE—TEMPERATURE EXCURSION". Do not discard them.
  3. Document the date and time, unit and room temperatures (including min/max), the length of time vaccine may have been affected (if using a DDL), inventory with lot numbers, other relevant information (for example a cracked door seal), and "how long it took to act".
  4. Contact the immunization program or the manufacturer.
- "Repeated Alarm Alerts: If the temperature alarm sounds repeatedly, do not disconnect it until the cause is identified and addressed. Do basic checks of the unit door, power supply, and thermostat settings."
- Every unit needs a DDL, plus at least one backup DDL.
- Vaccines should not go on door shelves or in drawers, and should sit 2–3 inches from the walls, ceiling, floor and door.

— [CDC Vaccine Storage and Handling Toolkit (PDF, July 2026)](https://www.cdc.gov/vaccines/hcp/downloads/storage-handling-toolkit.pdf); [CDC Storage & Handling landing page](https://www.cdc.gov/vaccines/hcp/storage-handling/index.html)
- Since 1 January 2018, VFC providers have had to use a DDL with continuous monitoring and a current calibration certificate in each unit (secondary, New Jersey state programme). — [NJIIS: Getting to Know Your Data Loggers](https://njiis.nj.gov/docs/vfc/Getting_to_Know_Your_Data_Loggers.pdf)

**Buffered probe vs air probe: quantified**
- Rusnack MR, "Improving Vaccine Safety by Using an Algorithmic Model as a Replacement for a Physical Thermal Buffer", *Innovations in Pharmacy* 2018;9(1):Article 10. The author works for AmericanPharma Technologies, a vendor, so there is a potential conflict of interest.
  - The set-up was a two-door pharmacy fridge with compressor cycling every 60 minutes.
  - Over 24 hours, unbuffered air ranged 1.7–6.2 °C while a 20-ml glycol bottle ranged only 3.6–4.3 °C.
  - An algorithmic "virtual buffer" tracked the glycol with a mean difference of −0.078 °C (95% CI −0.085 to −0.070).
  - To simulate the buffer accurately, the algorithm needed at least one sample per 10.8 minutes; the author chose 5 minutes.
  - Problems with physical glycol listed: evaporation, spills, mispositioning and touching the walls, and a thermal response that differs from vaccine fluid.
  - The buffer "is intended to reduce false alarms so that the drug manager will know with higher confidence that a temperature alert is an event requiring action."

  — [Rusnack 2018, Innovations in Pharmacy (PDF)](https://pubs.lib.umn.edu/index.php/innovations/article/download/962/1050/2207)
- Vendor claims (secondary, unverified data): Dataloggers Inc. says buffers such as glycol bottles or nylon blocks "reduce nuisance alarms caused by door openings and compressor cycling". Phase IV says a buffered probe will still alarm if the door is left open for several minutes. — [DataloggerInc: Comparison of Thermal Buffer Effectiveness](https://dataloggerinc.com/wp-content/uploads/2023/07/23-Comparison_of_Thermal_Buffer_Effectiveness.pdf); [Phase IV LEAP refrigerator manual](https://phaseivengr.com/wp-content/uploads/2025/01/53-100187-15-MANUAL_USER_LEAP_Refrigerator.pdf); [Lascar vaccine white paper](https://backup.lascarelectronics.com/wp-content/uploads/vaccine-white-paper-12_2019-1.pdf)

**WHO PQS alarm delays (30-day temperature recorders, E006)**
- The WHO PQS standard for 30DTRs (E006/TR06.4) defines a Type 1 refrigerator configuration (+2 to +8 °C):
  - low alarm at −0.5 °C or below for 60 minutes
  - high alarm at +8 °C or above for 10 hours

  TechNet-21 describes these as consecutive minutes and hours (secondary). — [TechNet-21: New PQS configurations ready on all Fridge-tags (7 June 2022)](https://www.technet-21.org/en/community/discussions/new-pqs-configurations-ready-on-all-fridge-tags); [UNICEF Supply Catalogue: Fridge-tag 2E](https://supply.unicef.org/s0002135.html)
- One TechNet-21 forum reply says the high alarm is >+10 °C for 10 hours. This conflicts with the +8 °C figure and is likely an error.
- Nexleaf summarises the rationale: "the WHO says up to 10 hours of moderate heat exposure is okay, but just 60 minutes of freezing exposure is considered potentially destructive". — [Nexleaf IoT for Development Series: ColdTrace (2017, PDF)](https://www.nexleaf.org/wp-content/uploads/reports/IoT-Series_ColdTrace-PDF-Report_2017.pdf)
- WHO PQS data sheet for the Berlinger Fridge-tag 2 (E006-020):
  - measures every minute, ±0.5 °C, visual alarm, factory-programmed
  - default Type 1 and Type 2 configurations "as per TR06.4"
  - spec E006/TR06.3
  - prequalified 31 January 2013, valid until 31 May 2027
  - USD 48 per unit (2022 base price)

  — [WHO PQS E006-020 data sheet](https://extranet.who.int/prequal/sites/default/files/immunization_devices/pdf/e006/E006-020.pdf)

**Nexleaf ColdTrace RCT, Mozambique, 15 August 2014 to 1 June 2015**
- Partners: Nexleaf with the Mozambique Ministry of Health, VillageReach, PATH and UNICEF (Nexleaf report, primary).
- Groups:
  - Group 1: 29 facilities with RTM plus SMS alerts, training and posted SOPs.
  - Group 2: 28 facilities with 30DTRs.
  - Group 3: 26 facilities with stem thermometers read twice daily.
- ColdTrace alert thresholds were deliberately more conservative than the WHO alarm states:
  - cold alert: below +2 °C for ≥30 minutes
  - warm alert: above +8 °C for ≥60 minutes
  - WHO freezing alarm state: below −0.5 °C for 60 minutes
  - WHO heat alarm state: +8 °C for ≥600 minutes
- Uptime (+2 to +8 °C): 90% (RTM), 86% (30DTR), 74% (stem thermometer).
- Time per month in each state:

  | Group | Cold alert | WHO freeze alarm | Warm alert | WHO heat alarm |
  |---|---|---|---|---|
  | 1: RTM | 9 h | 2 h | 45 h | 18 h |
  | 2: 30DTR | 25 h | 4 h | 36 h | 15 h |
  | 3: Stem thermometer | 31 h | 6 h | 96 h | 56 h |

- Share of time in WHO freeze alarm: 0.55% (RTM), 1.9% (30DTR) and 2.3% (stem).

— [Nexleaf: RTM Increases Uptime and Decreases Freezing Duration in Vaccine Refrigerators (PDF)](https://www.nexleaf.org/wp-content/uploads/2021/05/Nexleaf-RTM-RCT-Report.pdf)

**Other Nexleaf results**
- The TechNet 2015 poster version (secondary summary): Group 1 had 50% fewer cold excursions than the 30DTR group and 62% fewer than the stem-thermometer group (p<0.02). It attributes lower freezing duration to staff and supervisors being alerted via SMS and escalated alerts. — [Nexleaf TechNet 2015 poster](https://www.technet-21.org/images/TC2015/Posters/NexLeaf_Poster.pdf)
- Nexleaf's own report says "Text alerts alone reduced vaccine freezing in health clinics by 74%", and that nurses "take action to protect vaccines" when alerted. It also notes that "many chronically broken fridges kept on failing" despite alerts, which shifted the focus to remote diagnosis and maintenance. — [Nexleaf IoT Series: ColdTrace (2017)](https://www.nexleaf.org/wp-content/uploads/reports/IoT-Series_ColdTrace-PDF-Report_2017.pdf)
- Nexleaf's RCT report cites a WHO study in India (Murhekar et al., *Bull WHO* 2013) in which 75% of freeze-sensitive vaccines showed signs of freeze damage at the point of administration (secondary via Nexleaf). — [Nexleaf RCT report](https://www.nexleaf.org/wp-content/uploads/2021/05/Nexleaf-RTM-RCT-Report.pdf)

**Belize RTM evaluation**
- Oladeji O et al., *Int J Community Med Public Health* 2025;12(3):1503–1511, published 28 February 2025. This is a retrospective review of alarm records from November 2023 to October 2024.
  - 8 RTM devices were installed, and alarms came from 4 of them.
  - "Eighteen alarms were reported in 8 months", ranging from 1 to 6 per month with an average of 2.6 per month. That average is internally inconsistent: 18 ÷ 8 = 2.25.
  - Alarm duration ranged from 0.6 to 31.3 hours, with an average of 9.6 hours.
  - "75% of the alerts resolved within 24 hours."
  - The paper does not classify alarms as false or true and does not describe the notification channel.

  — [Oladeji et al. 2025, IJCMPH](https://www.ijcmph.com/index.php/ijcmph/article/view/13600)

**India eVIN (UNDP-run)**
- SIM-enabled loggers record every 10 minutes and upload every 60 minutes over GPRS. On high or low temperature the logger alarms and alerts technicians and cold chain handlers by SMS or email.
- A health worker quote: "If there's a power failure, the alarm rings and we get an SMS. Even if we are at home, we can call the staff."
- UNDP cites live monitoring at more than 29,000 cold chain points.

— [Vikaspedia: eVIN project](https://en.vikaspedia.in/viewcontent/health/health-care-innovations/health-system-strengthening-1/evin-project-of-health-ministry-health-system-strengthening-1-1?lgn=en); [Governance Now: The shot just got smarter](https://www.governancenow.com/gov-next/egov/the-shot-just-got-smarter-evin-vaccine-immunisation); [UNDP: eVIN to Co-WIN](https://www.undp.org/india/blog/evin-co-win-digitizing-indias-immunization-programme)

**Nuisance-alarm mechanisms in practice**
- A Nexleaf coordinator on TechNet-21 (secondary): "Normal events can lead to short-term excursions that are of no importance, so it would be important to not trigger an 'alarm' to the health worker too." — [TechNet-21 30DTR discussions](https://www.technet-21.org/en/community/discussions/30-dtr)
- Food and commercial cold rooms (secondary, manufacturer manual): door openings raise probe readings and scheduled defrost can push temperatures above limits, so delays should be set "to avoid nuisance alarms under these normal circumstances". The manufacturer does not recommend specific values. — [Winland EA200/EA400 manual](https://www.manualsdir.com/manuals/465960/winland-electronics-ea200-ea400.html)
- Vendor caution: a failed or stuck defrost can cause genuine high temperatures, so delays must not hide defrost faults (secondary, vendor). — [Envigilance: Walk-in freezer monitoring](https://envigilance.com/temperature-monitoring/walk-in-freezer-monitoring/)

### Inferences
- The two authoritative bodies (CDC and WHO) already embody the two main anti-false-alarm levers: physical or thermal filtering (buffered probe) and persistence (10 h heat / 60 min freeze). ThermoTwin's policy can be presented as an extension of WHO/CDC practice rather than a departure from it.
- The asymmetry is deliberate and should be copied: freezing gets a short delay (60 min) because it is quickly destructive, while heat gets a long one (10 h). Nexleaf used tighter "early warning" levels (30 min below +2 °C; 60 min above +8 °C) underneath the WHO alarm levels. This is a natural two-tier design: early warning first, then a WHO-grade alarm.
- Nexleaf's results support the claim that alerting changes behaviour for freezing:
  - Time in WHO freeze alarm was 2 h/month with RTM vs 4 h with 30DTR and 6 h with stem thermometers.
  - Not for heat: the RTM group spent more time in warm alert (45 h) and heat alarm (18 h) than the 30DTR group (36 h / 15 h).

  ThermoTwin's "explain causes" and predictive features are the right answer to the "chronically broken fridges kept on failing" problem, because alerts alone cannot fix equipment.
- Belize gives a rough real-world volume of 18 alarms across 8 devices in 8 months. That is about 0.28 alarms per device per month, or about 0.56 if you count only the 4 devices that alarmed. Average durations of about 10 hours and 25% unresolved at 24 hours suggest response latency, not alarm count, was the problem there.
- Rusnack's numbers give ThermoTwin a concrete basis for a "virtual buffer". A first-order filter on air temperature, with a time constant matched to a 20-ml glycol bottle, removes most compressor-cycle swing (4.5 °C peak-to-peak in air vs 0.7 °C in glycol). It needs sampling every 5–10 minutes.

### Gaps
- I found no independent, controlled study that quantifies the percentage reduction in false alarms from buffered vs air probes in vaccine fridges. The figures are either damping ranges (Rusnack) or vendor claims.
- I could not obtain the primary WHO PQS E006/TR06.4 specification text. Thresholds come from TechNet-21 and UNICEF summaries.
- I found no LMIC remote monitoring evaluation (Nexleaf, UNICEF, PATH, Gavi CCEOP) that reports the share of alarms that were false or non-actionable, or SMS acknowledgement rates and median response times. Nexleaf reports outcomes (uptime, time in alarm), not alert-level response.
- I found no PATH or UNICEF remote monitoring landscape report with alarm-volume data in this search. The Gavi CCEOP remote monitoring requirements were not retrieved.
- Food cold rooms: I found no authoritative (FDA Food Code, HACCP or EN 12830) guidance on alarm delay values. Only vendor manuals were found.

## 4. Human factors of alert design (actionability, escalation, content, channel, acknowledgement)

### Takeaway
Every alert should map to a defined action and a named responder. It should escalate when it is not handled, carry the information the responder needs to act and document (as in CDC's excursion record), and never be disabled silently. In low-resource settings the proven channel is SMS to facility staff, escalating to supervisors. I found no comparative evidence of SMS against app notifications.

### Cited Findings
- Who acts, and what goes in the message (CDC, July 2026):
  - Who acts: "Any staff member who hears an alarm… should immediately notify the primary or backup vaccine coordinator, or report the problem to their supervisor."
  - Information to capture: date and time, unit and room temperature (including min/max), duration, affected inventory and lots, and contributing factors such as a cracked door seal.
  - Documentation must include "how long it took to act".

  — [CDC Toolkit, July 2026](https://www.cdc.gov/vaccines/hcp/downloads/storage-handling-toolkit.pdf)
- No silent disabling: CDC says "do not disconnect [the alarm] until the cause is identified and addressed". The Joint Commission found alarm signals "inappropriately turned off" in 36 of 98 sentinel events. — [CDC Toolkit](https://www.cdc.gov/vaccines/hcp/downloads/storage-handling-toolkit.pdf); [TJC SEA 50](https://digitalassets.jointcommission.org/api/public/content/f65e5c9df2b94000a99445e0a7877007)
- Governance of settings: NPSG.06.01.01 EP3 requires policies on clinically appropriate settings, when alarms can be disabled, who has authority to change parameters, and how alarms are monitored and responded to (secondary). — [Relias Media](https://reliasmedia.com/articles/64545-new-npsg-addresses-clinical-alarm-safety)
- Escalation in LMIC remote monitoring:
  - Nexleaf's Mozambique intervention combined SMS alerts with training "on responding to RTM alerts" and SOPs posted in clinics. It attributes lower freezing to staff and supervisors being alerted "through SMS and escalated alerts".
  - The first-generation ColdTrace devices were built on "inexpensive smartphones" using SMS.

  — [Nexleaf RCT report](https://www.nexleaf.org/wp-content/uploads/2021/05/Nexleaf-RTM-RCT-Report.pdf); [Nexleaf TechNet 2015 poster](https://www.technet-21.org/images/TC2015/Posters/NexLeaf_Poster.pdf)
- India eVIN: alerts go by SMS or email to cold chain handlers and technicians. A health worker described getting an SMS at home and calling staff, with weekly visits from vaccine cold chain managers (VCCMs) as the backup support layer. — [Governance Now](https://www.governancenow.com/gov-next/egov/the-shot-just-got-smarter-evin-vaccine-immunisation)
- Priority discipline: "if too many alarms are high priority, then effectively none of the alarms are high priority" (secondary, exida). — [exida blog](https://exida.com/Blog/which-measure-rationalized-or-annunciated-is-more-important)
- Shelving and acknowledgement: ISA-18.2-style shelving is temporary and auto-returns, with a visible list of shelved alarms (secondary). — [ProcessOnline](https://www.processonline.com.au/content/software-it/article/improving-alarm-management-with-isa-18-2-part-2-1141142642)
- Response metrics seen in practice:
  - Belize: 75% of alerts resolved within 24 hours, mean alarm duration 9.6 hours.
  - Görges et al. (2009): 41% of ICU alarms ignored (secondary).

  — [Oladeji et al. 2025](https://www.ijcmph.com/index.php/ijcmph/article/view/13600); [AHRQ PSNet](https://psnet.ahrq.gov/issue/improving-alarm-performance-medical-intensive-care-unit-using-delays-and-clinical-context)
- Safety of reducing alarms: a 2015 Johns Hopkins randomized study of altered alarm settings (Cvach et al., *Biomed Instrum Technol* 2015) found lower alarm frequency with no difference in adverse events, including cardiac arrests and mortality (secondary). — [Johns Hopkins Nursing magazine](https://nursing.jhu.edu/magazine/articles/2011/12/turning-down-the-volume-2/); [FierceHealthcare](https://www.fiercehealthcare.com/healthcare/three-lessons-learned-to-reduce-alarm-fatigue-and-improve-alarm-management-and-patient)

### Inferences
Suggested ThermoTwin alert message template, derived from CDC's documentation list:
- unit or site name
- current and buffered (product) temperature
- the threshold crossed and for how long
- predicted time to the WHO-grade alarm (lead time)
- likely cause, for example door open, defrost, power loss or compressor failure
- the recommended action, for example "check door seal; do not move vaccines yet" or "move vaccines to backup unit"
- an acknowledgement link or reply code
- the escalation time if not acknowledged

Suggested escalation chain:
1. Facility staff by SMS, plus an in-app or local buzzer.
2. If not acknowledged within N minutes, the primary or backup vaccine coordinator.
3. Then the district supervisor or cold chain technician.

This mirrors CDC's coordinator roles and Nexleaf's supervisor escalation.

Other design points:
- SMS should be the default channel in LMIC settings. Smartphone push should be a progressive enhancement, since every documented deployment found (ColdTrace, eVIN) relied on SMS.
- Acknowledgement and resolution timestamps should be first-class data, because CDC already asks providers to document "how long it took to act".

### Gaps
- I found no study comparing SMS, app push, IVR voice calls and on-device buzzers for cold-chain alert response.
- I found no published acknowledgement rates or median time-to-acknowledge for vaccine fridge SMS alerts.
- I found no human-factors guidance (for example from AAMI or IEC 60601-1-8) applied specifically to fridge alarm message content. I did not research IEC 60601-1-8 in this session.

## 5. Methods to reduce false alarms and their quantified effects

### Takeaway
The levers with numbers behind them are persistence or delay, tailored thresholds, sensor and electrode hygiene, and multi-signal fusion. Most quantified evidence comes from clinical monitoring:
- **Delays:** 15 s SpO2 delay, −60% false alarms; 14 s, −50%; 19 s, −67%; 2 s, −25%; 5 s, −49%.
- **Adaptive delays:** −73.5% false positives.
- **Tailored default limits:** −43% critical alarms.
- **Team bundle:** median alarms 180 → 40.
- **Fusion and machine learning:** 47% to 90% suppression of false alarms, with about 0.5–1% of true alarms lost.

For fridges, the evidence is the WHO 10 h / 60 min delays and buffer damping. I found no published percentage reduction for fridge alarms specifically.

### Cited Findings
**Delays and persistence (clinical)**
- A 15-second delay between crossing an SpO2 threshold and alarming would cut false-positive alarms by 60% (Paine et al., *J Hosp Med* 2016, via review; secondary). — [Arora et al., arXiv 2302.03885](https://arxiv.org/pdf/2302.03885)
- A 14-second delay in an ICU reduced false-positive alarms by 50%, and a 19-second delay reduced alarms by 67%. The review cites Cvach, "Monitor alarm fatigue: an integrative review", *Biomed Instrum Technol* 2012;46(4), which draws on Görges et al. (2009). Secondary. — [Arora et al.](https://arxiv.org/pdf/2302.03885); [AHRQ PSNet on Görges 2009](https://psnet.ahrq.gov/issue/improving-alarm-performance-medical-intensive-care-unit-using-delays-and-clinical-context)
- In a trauma resuscitation unit (316,688 alarms for 6,701 patients over 12 months), a 2-second delay would cut alarms by 25% and a 5-second delay by 49% (Colton et al., *J Trauma Nurs* 2013;20(4):184–8; secondary). — [Arora et al.](https://arxiv.org/pdf/2302.03885)
- Adaptive time delays gave a 73.51% overall reduction in false-positive alarms. This was retrospective; the authors note the effect "has not been demonstrated in a prospective study". — [UKE Hamburg publication record](https://fis.uke.de/portal/en/publications/reduction-of-clinically-irrelevant-alarms-in-patient-monitoring-by-adaptive-time-delays(99275c89-3a53-490d-b14d-65976f65969b).html)
- A 2024 simulation of ICU alarm delays found a 10-second delay eliminated more than half of alarms, and concluded that delays should be tailored to each vital sign and context. — [DRS 2024 paper](https://dl.designresearchsociety.org/drs-conference-papers/drs2024/researchpapers/140)

**Tailored thresholds and defaults**
- Graham & Cvach, *Am J Crit Care* 2010;19(1):28–34: revising unit default alarm settings cut critical monitor alarms by 43% from baseline (secondary). — [FierceHealthcare](https://www.fiercehealthcare.com/healthcare/three-lessons-learned-to-reduce-alarm-fatigue-and-improve-alarm-management-and-patient); [Arora et al.](https://arxiv.org/pdf/2302.03885)
- Further results reported in the review (secondary):
  - Self-resetting heart-rate alarms with limits of 45 and 130 bpm gave an 89% reduction in mean weekly alarms.
  - Procedure-specific vital-sign settings reduced false-positive alarms by about 80% (Schmid et al.).

  — [Arora et al.](https://arxiv.org/pdf/2302.03885)

**Team bundles and hygiene**
- Dandoy et al., *Pediatrics* (team-based approach): compliance rose from 38% to 95%, and median alarms fell from 180 to 40, a 77.78% decrease (secondary). — [Arora et al.](https://arxiv.org/pdf/2302.03885)
- Daily ECG electrode change cut average alarms per bed by 46% (Cvach et al.). Another unit saw 20.6% and 71.0% reductions in two intervention periods (Smith). Secondary. — [Arora et al.](https://arxiv.org/pdf/2302.03885)

**Multi-sensor fusion and machine learning (secondary)**
- Using arterial blood pressure (ABP) features cut ECG arrhythmia alarms by an average of 47% (447 MIMIC-II records).
- A random-forest classifier suppressed 90.3% of false tachycardia alarms while incorrectly suppressing only 0.54% of true alarms.
- One method reached 30.5% false-alarm suppression with true-alarm suppression below 1%.
- Bayesian fusion had a 23% error rate, against 35% (ECG only), 40% (ABP only), 41% (PPG only) and 31% (majority voter).

— [Arora et al.](https://arxiv.org/pdf/2302.03885)

**Cold-chain specific**
- Buffering: air 1.7–6.2 °C vs glycol 3.6–4.3 °C over 24 hours. The algorithmic buffer was within −0.078 °C of measured glycol. — [Rusnack 2018](https://pubs.lib.umn.edu/index.php/innovations/article/download/962/1050/2207)
- Persistence: WHO 30DTR Type 1 alarms at ≥+8 °C for 10 h and ≤−0.5 °C for 60 min. Nexleaf's early-warning alerts used 30 min below +2 °C and 60 min above +8 °C. — [TechNet-21](https://www.technet-21.org/en/community/discussions/new-pqs-configurations-ready-on-all-fridge-tags); [Nexleaf RCT](https://www.nexleaf.org/wp-content/uploads/2021/05/Nexleaf-RTM-RCT-Report.pdf)
- Hysteresis: EEMUA-attributed deadband for temperature is 1% (secondary). — [exida](https://www.exida.com/Blog/why-should-i-use-an-alarm-deadband)
- Context (door and defrost): manufacturer guidance is to set delays so that door openings and scheduled defrost do not trigger alarms. — [Winland manual](https://www.manualsdir.com/manuals/465960/winland-electronics-ea200-ea400.html)

### Inferences
Candidate rules for ThermoTwin's alert policy, drawn from the evidence above:
1. Alarm on a buffered or "virtual-buffer" product temperature, not on raw air temperature.
2. Use asymmetric persistence windows: an early warning (≥30 min below +2 °C, ≥60 min above +8 °C) and a critical tier at WHO-grade (≤−0.5 °C for 60 min, ≥+8 °C for 10 h).
3. Apply hysteresis of at least about 0.5 °C so an alert does not chatter at the threshold.
4. Suppress by design, with logging, when a door-open or defrost context explains a transient. Re-arm if the transient lasts longer than that unit's learned recovery time.
5. Use multi-sensor confirmation (two probes, or probe plus door and power state) before escalating to the critical tier.
6. Use predictive alerting to raise lead time rather than volume. A forecast "will breach in X minutes" should start as an advisory and be promoted to the higher tiers only by the persistence rules above, or by a high-confidence forecast with a short horizon.

The clinical fusion literature shows the key safety metric for any suppression is the true-alarm suppression rate, which those studies hold under about 1%. ThermoTwin should report this alongside any claimed reduction in false alarms.

The quantified clinical reductions (25–90%) can be cited as precedent for delay and fusion approaches. A cold-chain-specific reduction figure would have to come from ThermoTwin's own replay of logged data, for example by comparing a naive instantaneous threshold on air temperature with ThermoTwin's policy on the same traces.

### Gaps
- I found no peer-reviewed quantification of false-alarm reduction from delays, buffers or door-state context in pharmacy, vaccine or food fridges.
- I found no published evaluation of predictive (forecast-based) alerting for cold-chain excursions with precision or lead-time figures.
- The 14 s / 19 s delay figures are cited third-hand (arXiv review → Cvach 2012 → Görges 2009). Verify them against Görges et al., *Anesth Analg* 2009 (doi 10.1213/ane.0b013e31819bdfbb).

## 6. How alert performance should be evaluated

### Takeaway
Use three families of metrics:
- **Load metrics (ISA/EEMUA):** alerts per responder per period, flood share, top-10 or "bad actor" share, chattering count, stale or shelved count, priority mix.
- **Accuracy metrics (clinical literature):** false-positive or non-actionable share, PPV or precision, and true-alarm suppression rate.
- **Outcome and response metrics (cold chain):** uptime, hours in WHO alarm state per month, alarms per device per month, alarm duration, time to acknowledge and time to resolve, and the share resolved within 24 hours.

ThermoTwin should add lead time for predictive alerts.

### Cited Findings
- **ISA/EEMUA load KPIs:**
  - average alarm rate per operator (per 10 min, hour and day)
  - % of 10-minute periods with more than 10 alarms
  - peak rate
  - top-10 contribution
  - chattering and fleeting count
  - stale alarms (active more than 24 h)
  - annunciated priority distribution

  — [Emerson](https://d1-live.emerson.com/documents/automation/article-alarm-management-by-numbers-deltav-en-38292.pdf); [IChemE guide](https://www.icheme.org/media/16019/icheme-alarm-management-practical-guide-06_05_2021.pdf); [exida](https://exida.com/alarm-management/assessment)
- **Clinical accuracy metrics:**
  - false-positive share of annotated alarms (88.8%)
  - audible alarms per bed per day (187)
  - actionable share (5–13% of ICU alarms)
  - true-alarm suppression rate for alarm-reduction algorithms (0.54%, <1%)

  — [Drew et al. 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4206416); [Arora et al.](https://arxiv.org/pdf/2302.03885)
- **Cold-chain outcome metrics:**
  - uptime % within +2 to +8 °C (90/86/74%)
  - average hours per month in early-warning alert and in WHO freeze or heat alarm state
  - % of time in WHO freeze alarm (0.55% / 1.9% / 2.3%)

  — [Nexleaf RCT](https://www.nexleaf.org/wp-content/uploads/2021/05/Nexleaf-RTM-RCT-Report.pdf)
- **Response metrics:**
  - alarms per month (average 2.6, range 1–6)
  - alarm duration (0.6–31.3 h, mean 9.6 h)
  - % resolved within 24 hours (75%)

  — [Oladeji et al. 2025](https://www.ijcmph.com/index.php/ijcmph/article/view/13600)
- **Documentation metric:** CDC asks providers to record "how long it took to act". — [CDC Toolkit, July 2026](https://www.cdc.gov/vaccines/hcp/downloads/storage-handling-toolkit.pdf)
- **Joint Commission:** organisations should "review trends and patterns in alarm-related events" and continually optimise configurations. — [TJC SEA 50](https://digitalassets.jointcommission.org/api/public/content/f65e5c9df2b94000a99445e0a7877007)

### Inferences
Suggested ThermoTwin evaluation scorecard, assembled from the above (not from a single published standard):
1. **False or non-actionable alerts per device per month**, with a nuisance alert defined as one that did not reach WHO-grade or product-relevant buffered excursion criteria, or that resolved without intervention within the persistence window.
2. **Alert precision (PPV):** the share of critical alerts that correspond to a true product-threatening excursion.
3. **Recall or sensitivity on WHO-grade events:** the share of ≥10 h above +8 °C and ≥60 min at or below −0.5 °C events that were alerted. The target should be about 100%, with a true-alarm suppression rate under 1%, as in the clinical fusion studies.
4. **Lead time:** median minutes between the first predictive alert and the WHO-grade breach, or the first naive threshold crossing.
5. **Time to acknowledge and time to resolve:** medians and the 24-hour resolution rate, benchmarked against Belize's 75%.
6. **Load:** alerts per responder per day or week, % of days with an alert "flood", and the top-10 "bad actor" devices' share of alerts (ISA target 1–5%).
7. **Outcome:** uptime % and hours per month in WHO alarm state, as in the Nexleaf RCT.

For a hackathon demo, the most credible evidence is a replay benchmark. Run a naive instantaneous air-temperature threshold and the ThermoTwin policy over the same logged traces (with labelled door-open and defrost events), then report the reduction in nuisance alerts, recall on true excursions, and lead time.

### Gaps
- I found no published standard benchmark for "acceptable false alarms per fridge per month" in pharmacy or vaccine cold chain.
- I found no public labelled dataset of fridge traces with ground-truth door-open and defrost events and excursion labels in this search, so the replay benchmark would need ThermoTwin's own or synthetic data.
