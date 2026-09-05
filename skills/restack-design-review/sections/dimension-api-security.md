### API dimension

An API is a contract, and most of its cost arrives later — at the point someone
needs to change it and cannot. Review it as a one-way door, because that is
usually what it is.

**Contract clarity.** Is the contract explicit and versioned, or implied by
whatever the implementation currently returns? An undeclared contract is still
a contract; it is just one nobody agreed and everybody depends on.

**Evolution.** Trace one concrete change: adding a field, deprecating one,
changing a type. Who breaks, and how would you know before they do? If the
answer requires coordinating a deploy with a consumer, the API is coupling two
release cycles together.

**Error semantics.** Can a caller distinguish "your request was wrong", "I
failed", "I am overloaded, retry later", and "I succeeded but with nothing to
return"? Conflating these is what produces the empty-response-with-200 class of
bug — the caller cannot tell absence from failure, so it guesses, and it
guesses wrong under load.

**Idempotency and retries.** Which operations are safe to retry, is that stated
in the contract, and is there an idempotency key for the ones that need it? A
caller will retry whether or not you designed for it.

**Pagination and unbounded responses.** Any collection endpoint without a limit
will eventually return everything. Ask what happens at 100x the current volume.

**Timeouts and backpressure.** What does this API do when it is overloaded —
queue, shed, or fall over slowly? Slow failure is worse than fast failure
because it exhausts the caller's resources too.

Cross-check against the path map: every API is a hop, and its failure mode is
what the upstream actor experiences.

---

### Security dimension

Review the threat model, not a control checklist. The compliance-as-stressors
argument applies here — a control list tells you what is conventionally
required; a threat model tells you what would actually hurt this system.

**Start with the threat model.** Ask directly: who would attack this, what
would they want, and what do they already have access to? If there is no answer,
that is the top finding — every control below is unmotivated without it.

**Authentication and authorisation, separately.** Who are you, and what may you
do, are different questions with different failure modes. Look specifically for
authorisation decided at the edge and trusted thereafter: any actor that
believes an upstream already checked is an actor that can be reached another way.

**Trust boundaries on the path map.** Mark where each path crosses one.
Crossings are where validation belongs, and undrawn crossings are where it is
missing.

**Secrets.** Where do they live, how are they rotated, and what is the blast
radius of one leaking? A secret that cannot be rotated without downtime will
not be rotated.

**Data protection.** What is sensitive, where does it rest, where does it
travel, and who can read it in logs? Sensitive data in logs is the most common
finding in this dimension and the easiest to fix early.

**Blast radius of compromise.** Assume one actor is fully compromised. What can
it reach? If the answer is everything, the finding is architectural — network
or identity segmentation — not a control gap.

**Audit.** Can you reconstruct who did what, after the fact? Note that this
usually has to be designed in; it is rarely retrofittable.

**Compliance.** Do not review against a control list here. If a regulatory
framework applies, run `/restack-stressor compliance <pack>` so the requirements
enter as stressors and the residuals address the underlying harm structurally.
A control satisfied by a document and not by the architecture will be satisfied
right up until it matters.
