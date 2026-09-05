### Generating infrastructure as code

Supported: `terraform`, `cloudformation`, `bicep`, `cdk`. Generate code the
team can read and review, not the shortest thing that applies cleanly.

#### Safety rules — these are not style preferences

**Never emit a secret.** No passwords, API keys, tokens, connection strings,
certificates or private keys in generated code, in variable defaults, in
example `tfvars`, or in comments. Reference a managed secret store — Secrets
Manager, Key Vault, Secret Manager — and emit the *reference*. If a value is
needed to make the code coherent, emit a clearly-marked placeholder and say in
the output that it must be supplied out of band.

If the architect pastes a real credential into the conversation, do not
propagate it into a file. Say it should be rotated, because it is now in a
transcript.

**Never generate anything destructive without it being obvious.** Resources
that would delete or replace data — a database with `force_destroy`, a
`prevent_destroy = false` on a stateful resource, a lifecycle rule that expires
objects — get an explicit comment saying what is lost and under what
conditions. The architect should not discover destructive behaviour by reading
a plan output at deploy time.

**Least privilege, actually.** The execution role gets the permissions the
stack needs, enumerated. Never `*` on actions or resources, including "just for
now" — temporary IAM policies are permanent. Where you cannot determine the
minimal set, emit the narrow guess and flag it for tightening rather than
emitting a wildcard.

**Protect the state.** Remote backend with locking, encryption at rest, and
access restricted to the deployment identity. State files contain resource
attributes including, in some providers, secret values — treat the backend as a
sensitive store, and never commit local state.

**Environment separation is structural.** Workspaces, separate state, or
separate accounts — never a conditional in the code that branches on an
environment name. The failure mode is a production change applied from a
developer's shell, and it happens.

#### Practice

1. **Modules for anything used twice.** Copy-paste infrastructure diverges, and
   the divergence is discovered during an incident.
2. **Variables for everything environment-specific.** No hardcoded region,
   account id, CIDR, size or hostname.
3. **Outputs for everything another stack consumes**, so the coupling is
   declared rather than discovered.
4. **Tags on every resource:** environment, team, cost centre, project, and
   whatever the organisation's scheme requires. Tags are how cost becomes
   attributable and how orphaned resources get found later.
5. **Drift detection** on a cadence. Infrastructure as code that has drifted is
   documentation, not control.
6. **Pin provider and module versions.** An unpinned provider means the
   infrastructure changes when nobody deployed anything.

#### What to say alongside the code

Generated IaC is untrusted until reviewed, applied to a non-production
environment, and scanned. Say so, and say specifically:

- **what requires environment-specific configuration** before it will apply
- **what this code assumes exists** — a VPC, a DNS zone, an account structure
- **what it will cost**, at least in order of magnitude, and what drives it
- **what is destructive on a re-apply**, if anything
- **what it does not cover** — monitoring, backup schedules, DNS, whatever the
  scope excluded

Recommend `plan`/`what-if` and a policy scan before any apply, and never
recommend applying against production as the first exercise of new code.

#### Wiring it back

Every resource in the generated code should map to an actor in the path map. A
resource that does not is either missing from the design or unnecessary, and
both are worth resolving.

Where a resource implements a residual, comment it as such — naming the
stressors it clears. That comment is what stops the next engineer removing an
apparently redundant queue during a cost-reduction exercise.
