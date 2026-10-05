# Impact matrix, iteration 3 (Lockerline)

**Scoring baseline:** D5. EB (the event broker), SS (the snapshot store) and
RJ (the replay job) run on one managed event cluster. OC is on-call. Since D6
the matrix is `scored pre-D6`.

| Stressor | Lens | CA | RS | LC | PR | EB | SS | RJ | OC | Σ |
|---|---|---|---|---|---|---|---|---|---|---|
| S-1 | O | 1 | · | · | · | · | · | · | · | **1** |
| S-2 | C | · | · | 1 | · | · | · | · | · | **1** |
| S-3 | O | 1 | · | · | · | · | · | · | · | **1** |
| S-4 | C | · | · | 1 | 1 | · | · | · | · | **2** |
| S-5 | X | 1 | 1 | · | · | · | · | · | · | **2** |
| S-6 | C | · | 1 | · | 1 | 1 | · | · | · | **3** |
| S-7 | O | · | · | 1 | 1 | · | 1 | · | · | **3** |
| S-8 | P | · | · | · | · | 1 | 1 | 1 | · | **3** |
| S-9 | P | 1 | · | · | · | · | · | 1 | 1 | **3** |
| S-10 | C | · | · | · | · | 1 | · | 1 | 1 | **3** |
| S-11 | V | · | · | · | · | · | 1 | · | · | **1** |
| S-12 | C | · | · | · | · | · | · | · | · | **0** |
| **Total** | | **4** | **2** | **3** | **3** | **3** | **3** | **3** | **2** | **23** |
