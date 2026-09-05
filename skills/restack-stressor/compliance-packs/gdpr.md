---
name: GDPR Compliance Pack
framework: General Data Protection Regulation (EU) 2016/679
version: 1.0
---

# GDPR Compliance Pack

## Philosophy

Every GDPR article exists because real harm happened to real people — identity theft, surveillance, manipulation, loss of control over personal narratives. This pack expresses those harms as stressors. When you walk your paths under these stressors and identify residuals, you produce architecture that makes the harm structurally impossible — not just procedurally compliant.

**Compliance becomes a byproduct of antifragile design.**

---

## How to Use

```
/restack-stressor compliance gdpr     # inject this pack into your stressor list
/restack-stressor walk                # walk your paths under these stressors
/restack-stressor analyze             # build impact matrix — actors × stressors
/restack-stressor residues            # residuals address the underlying harm
/restack-adr create [document residuals as architectural decisions]
```

These stressors work alongside your system-specific stressors — run them in the same analysis, not a separate audit.

---

## Stressor Pack

### Data Breach & Unauthorised Access

**GDPR-01: A threat actor exfiltrates the entire personal data store**
- *Regulation:* Article 32 (security of processing), Article 33 (breach notification)
- *Real harm:* Individuals suffer identity theft, financial fraud, or reputational damage because data they trusted you with was stolen
- *Walk focus:* Which actors hold or transmit unencrypted personal data? Which actors can be reached without authentication? Where does bulk data access go undetected?

**GDPR-02: An internal employee queries the database and exports all user records without authorisation**
- *Regulation:* Article 32 (access controls), Article 5(1)(f) (integrity and confidentiality)
- *Real harm:* Insider threat — a disgruntled employee, a compromised account, or simple curiosity causes the same harm as an external breach
- *Walk focus:* Which actors expose bulk data access? Where is privilege separation enforced? Who can read data without a business justification being recorded?

**GDPR-03: A misconfigured API endpoint returns personal data to unauthenticated callers**
- *Regulation:* Article 25 (data protection by design and by default), Article 32
- *Real harm:* Personal data is publicly accessible because a default was wrong, not because of active attack
- *Walk focus:* Which actors serve personal data? What is the default access posture — open or closed? Where is authentication enforced vs. assumed?

---

### Right to Erasure & Data Subject Rights

**GDPR-04: A user requests deletion of their account and all associated personal data, but data persists in backups, logs, analytics pipelines, and third-party integrations**
- *Regulation:* Article 17 (right to erasure)
- *Real harm:* A person cannot leave — their data continues to be processed indefinitely despite a clear withdrawal of consent
- *Walk focus:* Walk the user data path end to end — every actor that writes, caches, replicates, or forwards personal data. Where does data land that the deletion flow doesn't reach?

**GDPR-05: A user requests a copy of all personal data held about them, but the system cannot produce a complete, portable export**
- *Regulation:* Article 15 (right of access), Article 20 (right to data portability)
- *Real harm:* Individuals cannot inspect or move what is theirs — undermining the fundamental principle of data sovereignty
- *Walk focus:* Which actors hold personal data in formats that aren't included in the export? Which third-party actors hold data the system doesn't control?

**GDPR-06: A user withdraws consent for data processing, but their data continues to flow through marketing, analytics, and recommendation systems**
- *Regulation:* Article 7 (conditions for consent), Article 21 (right to object)
- *Real harm:* Consent becomes meaningless — the architecture processes data regardless of expressed preference
- *Walk focus:* Where is consent state stored and checked? Which downstream actors receive data without verifying consent? Is consent checked at the source or just at the entry point?

**GDPR-07: A user requests correction of inaccurate personal data, but the correction doesn't propagate to all downstream actors and third parties**
- *Regulation:* Article 16 (right to rectification)
- *Real harm:* Inaccurate data continues to be used in decisions affecting the individual (credit, employment, insurance)
- *Walk focus:* Which actors replicate or cache personal data? Which third-party actors received the data and cannot be updated?

---

### Data Minimisation & Purpose Limitation

**GDPR-08: The system collects personal data at registration that is never used for the stated purpose, but is retained indefinitely**
- *Regulation:* Article 5(1)(b) (purpose limitation), Article 5(1)(c) (data minimisation)
- *Real harm:* People hand over personal information under a specific promise, and it is used — or exposed — for purposes they never agreed to
- *Walk focus:* Walk the data collection path — what is collected at each actor? What is the stated purpose? Which actors actually use each field? What is never read after initial write?

**GDPR-09: Personal data collected for one feature is passed to a new analytics or AI training pipeline without re-obtaining consent**
- *Regulation:* Article 5(1)(b) (purpose limitation), Article 6 (lawfulness of processing)
- *Real harm:* Data collected under one legal basis is repurposed without a new basis — processing becomes unlawful even though the data was legitimately collected
- *Walk focus:* Which actors receive copies of personal data beyond the original purpose? Where does data flow to that wasn't in the original consent disclosure?

---

### Data Retention & Storage

**GDPR-10: Personal data is retained long after the user relationship ends because no retention policy is enforced in the architecture**
- *Regulation:* Article 5(1)(e) (storage limitation)
- *Real harm:* Data that should have been deleted years ago is exposed in a breach — harm is compounded by the unnecessary retention
- *Walk focus:* Which actors store personal data? What triggers deletion? Is there any actor that enforces retention limits automatically, or is it a manual process?

**GDPR-11: Logs containing personal data (IP addresses, email addresses, user IDs in query strings) are retained indefinitely in log aggregation systems**
- *Regulation:* Article 5(1)(e) (storage limitation), Article 4(1) (definition of personal data)
- *Real harm:* Operational data that was never intended as a data store becomes one — personal data accumulates in systems with no access controls or retention policy
- *Walk focus:* Which actors write to logs? What personal data appears in log lines? What is the retention policy on log storage actors? Who has access?

---

### Third-Party & Cross-Border Data Transfers

**GDPR-12: A new third-party analytics or monitoring tool is integrated that transfers personal data outside the EU/EEA without an adequacy decision or transfer mechanism**
- *Regulation:* Article 44–49 (transfers to third countries)
- *Real harm:* Personal data is transferred to a jurisdiction with weaker protections — the rights the GDPR guarantees cannot be enforced
- *Walk focus:* Which actors transmit data to external services? Which of those services are outside the EU/EEA? What transfer mechanism is in place for each?

**GDPR-13: A sub-processor suffers a breach and personal data processed on your behalf is exposed**
- *Regulation:* Article 28 (processor obligations), Article 33 (breach notification chain)
- *Real harm:* You are legally responsible for data processed by your processors — a breach at a third party is a breach you must report and for which you bear accountability
- *Walk focus:* Which actors in your system are operated by third parties? Which of those handle personal data? What contractual and technical controls are in place?

---

### Breach Notification

**GDPR-14: A data breach occurs but goes undetected for more than 72 hours because no actor in the system detects or alerts on anomalous data access patterns**
- *Regulation:* Article 33 (72-hour notification to supervisory authority)
- *Real harm:* Regulators and affected individuals cannot take action to protect themselves — the delay compounds the harm
- *Walk focus:* Which actors could detect a breach? What constitutes anomalous access — and is any actor watching for it? How does a detected anomaly propagate to a notification?

---

### Special Categories of Data

**GDPR-15: The system inadvertently collects or infers special category data (health, religion, political opinion, biometric) through user behaviour, free-text fields, or enrichment APIs**
- *Regulation:* Article 9 (special categories of personal data)
- *Real harm:* Sensitive attributes attract the harshest consequences if exposed — discrimination, persecution, stigmatisation — yet they often enter systems unintentionally
- *Walk focus:* Which actors receive free-text input, behavioural signals, or third-party enrichment data? Could any of those inputs contain or allow inference of special category data? What is the processing basis?

---

## Common Residuals

These residuals frequently emerge from GDPR stressor analysis. They address the underlying harms structurally — and often protect against multiple stressors simultaneously:

| Residual | Stressors Addressed |
|----------|---------------------|
| **Encryption at rest and in transit actor** — dedicated encryption layer wrapping all personal data stores and transmission paths | GDPR-01, GDPR-02, GDPR-03, GDPR-12 |
| **Consent state actor** — a centralised service that other actors query before processing personal data, enforced at every consumption point not just at entry | GDPR-06, GDPR-09 |
| **Data erasure propagation path** — a dedicated path that walks all actors holding data for a given subject and triggers deletion, including backup and log actors | GDPR-04, GDPR-10, GDPR-11 |
| **Personal data inventory actor** — a service that knows what personal data is held, where, and for what purpose; powers subject access requests and deletion | GDPR-04, GDPR-05, GDPR-07, GDPR-08 |
| **Retention enforcement actor** — a scheduled actor that enforces deletion after the retention period expires, removing the dependency on manual process | GDPR-10, GDPR-11 |
| **Data minimisation review intention** — an intention that triggers periodic review of what data is being collected vs. what is being used | GDPR-08, GDPR-09 |
| **Anomaly detection actor** — monitors data access patterns and triggers a breach notification path when thresholds are exceeded | GDPR-14 |
| **Transfer gate actor** — validates that any outbound data transmission to a third-party actor has a valid transfer mechanism before allowing the intention to propagate | GDPR-12, GDPR-13 |
| **Audit log path** — a separate, append-only path that records who accessed what personal data and when, with its own access controls and retention policy | GDPR-02, GDPR-14 |

---

## Audit Traceability

When residuals from this analysis are documented as ADRs, they provide audit evidence that compliance controls were addressed architecturally, not procedurally. Each ADR should reference:
- The GDPR article being addressed
- The stressor that surfaced the need
- The residual introduced and why

This is stronger than a checklist audit — it shows regulators that the harm was understood and designed away.

---

## Scope Notes

This pack covers processing of personal data of individuals in the EU/EEA. Relevant regardless of where your organisation is located — if you process data about EU/EEA residents, GDPR applies.

**Not covered by this pack (separate analysis recommended):**
- Cookie consent and tracking (primarily a front-end / consent management concern)
- DPIA (Data Protection Impact Assessment) process — use `/restack-design-review` for structured assessment
- Legitimate interest balancing tests — legal analysis, not architectural

---

*Pack version: 1.0 | Regulation version: GDPR (EU) 2016/679 | Last reviewed: 2026-05*
