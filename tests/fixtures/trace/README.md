# trace fixture: a synthetic engagement

A fictional parcel-locker reservation service, "Lockerline", with the documents
a ReStack journey produces and a planted defect for every check in
`skills/restack-trace/scripts/trace.py`. Nothing here comes from a real
engagement, and nothing may: fixtures are committed to a public repository
([ADR-021](../../../docs/adr/ADR-021-trace-checks-as-a-worklist.md)).

`tests/test_trace.py` copies `docs/` into a scratch directory and sets every
file's modification time from its own table before scanning, because a
checkout's mtimes are whatever the clone happened to write.

| Check | Planted defect | Deliberately clean neighbour |
|---|---|---|
| REF | ADR-0009, D9 and A-7 cited, never defined | D365 in prose (a product name, far past the log) |
| REG | A-1's row says Open, its last status line says Resolved; A-2 uses "Maybe" | A-3, whose row and status line agree |
| KO | ADR-0003: HLD "updated" but older than the ADR; runbook "bannered" with no banner; LLD-04 does not exist; test strategy "pending". ADR-0004's field is empty. ADR-0005 has none | DEPLOYMENT.md updated after the ADR; ADR-0006 "None" after a grep; ADR-0007 ticketed |
| AM | ADR-0002: amendment after the body, no banner. LLD-02: an amendment newer than its banner | LLD-02's banner-covered amendment; HLD's inline-marked section |
| SUP | HLD cites superseded ADR-0001 with no marker | the same citation marked; the archived HLD; the review |
| BASE | iteration 2 matrix scored at D2, D3 changed the actor set; HLD quotes it unqualified | iteration 3 matrix, scored at D3 |
| MX | a row total, a column total and a cell scored 2 | iteration 3, which adds up |
| ALERT | LOCKER-GHOST in the runbook only | LOCKER-STUCK, defined in ADR-0004 |
| PH | TBD in ADR-0002 | TBD inside a fenced block |
| PDF | written by the test: an export older than DEPLOYMENT.md | — |
