### Scaling patterns by layer

| Layer | Primary approach | The constraint that actually bites |
|---|---|---|
| Stateless compute | horizontal, auto-scaled | warm-up time; connection pool exhaustion downstream |
| Stateful compute | vertical first, then partition | partitioning is a migration, not a setting |
| Relational database | read replicas, pooling, then shard | **the single writer** — replicas do nothing for write load |
| Key-value / document store | partition by key | hot keys; a bad partition key is a rewrite |
| Cache | scale out, tier | cold start after deploy; stampede on expiry |
| Object storage | effectively unbounded | request rate per prefix; cost, not capacity |
| Queue / stream | partition-based | ordering guarantees limit parallelism |
| Search index | replicas for read, shards for write | reindexing time grows with the corpus |
| Third-party API | you do not scale it | their rate limit is your ceiling |

Three of these are worth stating explicitly because they are the ones teams
discover late:

**Read replicas do nothing for write load.** A system whose write path is
saturating cannot be helped by adding replicas, and the effort spent adding
them delays the partitioning work that was actually needed.

**A partition key is close to a one-way door.** Choosing it badly is discovered
at scale and corrected by rewriting the data layer. It deserves an ADR.

**A third-party rate limit is your ceiling**, and it is somebody else's
decision. Treat it as a stressor and design a residual — queue, cache, batch —
rather than assuming an increase can be negotiated in time.

#### Scale-in is half the design

Teams design scale-out and forget the other direction, then discover their
elastic system never gives capacity back, or drops requests when it does.

- **Connection draining** before an instance goes away.
- **Session handling** — sticky sessions prevent scale-in and constrain
  scale-out; if they exist, that is a finding.
- **In-flight work.** What happens to a request or message being processed when
  the instance terminates? If the answer is "it is lost", that is a correctness
  defect surfaced by a capacity design.
- **Scale-in hysteresis.** Aggressive scale-in plus a spiky load produces
  thrashing, which costs more than the capacity saved.

#### Auto-scaling triggers

Trigger on the thing that saturates, which is rarely CPU. Queue depth, request
latency, connection pool utilisation and in-flight request count are usually
better signals — CPU is the default because it is easy to read, not because it
is informative.

Always state the **warm-up time**. It is the gap during which you are
under-provisioned, and headroom exists to cover it. An auto-scaling design
without a stated warm-up has not been finished.

---

### Finding the bottleneck

Every system has one. A team that cannot name theirs will optimise the wrong
thing, and the optimisation will show no improvement — which is expensive in
both effort and credibility.

#### Method

1. **Take the critical path from the path map.** Bottleneck analysis on a
   component list misses the interactions; on a path, the sequence is visible.
2. **For each actor, establish its ceiling and its current headroom.** Not its
   utilisation — its ceiling: requests per second, connections, IOPS, whatever
   saturates. Utilisation without a ceiling tells you nothing about how much
   room is left.
3. **The lowest ceiling on the path is the bottleneck**, regardless of how
   healthy everything else looks. Everything upstream can only run as fast as
   this.
4. **Name the second bottleneck too.** When the first is relieved, the second
   arrives immediately, and it is frequently the harder one. Teams that plan
   only the first fix are surprised twice.
5. **Check the non-obvious candidates**, which are where real bottlenecks
   usually hide: connection pool size, thread pool size, a lock, a single
   writer, a rate limit, a synchronous call to a third party, a lease or
   leader-election bottleneck, DNS.

#### Bottlenecks are matrix columns

An actor at its capacity ceiling is a vulnerable actor. It should already be a
column in the stressor matrix with a load-related stressor hitting it — and if
it is not, that is a gap in the analysis, not just a capacity finding.

Feed bottleneck findings back as stressors: "Inventory DB reaches its write
ceiling at 3x current load". Then the residual question applies normally — and
the answer is often architectural (a queue that absorbs the burst, a cache that
removes the reads) rather than more hardware.

---

### Right-sizing

Reducing over-provisioning without removing residuals.

1. **Measure actual utilisation** over a period covering the peak. Right-sizing
   from a quiet week produces an outage on a busy one.
2. **Separate over-provisioning from headroom.** A resource at 15% average may
   be correctly sized for a 10x peak. Only over-provisioning is waste; headroom
   was a decision.
3. **Check the matrix before removing anything.** A warm standby, an
   over-provisioned buffer or an idle replica may be a residual. Removing it
   raises impact on an actor the analysis already flagged — say which stressors
   the saving re-exposes you to, and let that be a decision rather than a
   side effect of a cost exercise.
4. **Right-size stateless first.** It is reversible in minutes. Stateful
   right-sizing is a migration and belongs in a different conversation.
5. **Re-measure afterwards.** Right-sizing changes behaviour — a smaller cache
   hits the origin more, a smaller instance changes GC characteristics.
