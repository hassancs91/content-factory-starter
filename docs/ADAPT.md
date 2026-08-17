# Adapting the five blocks to your niche

The kit ships with a software-shaped lab because that is where it was built. **The blocks
are roles, not tools.** Swap the implementations, keep the roles and the checkpoints, and
the pipeline works the same.

Here is the whole thing in one question per block:

| Block | The question |
|---|---|
| Contract | What are your stages, your rules, and where must the system stop for you? |
| Senses | How do you know what your audience actually asks? |
| Hands | What does the system capture as proof? |
| Lab | Where does your niche's truth get tested? |
| Brain | What are your opinions, stories and numbers, written down? |

Four of the five transfer almost unchanged. The interesting one is the lab.

## The lab is the block people get wrong

The lab is not "a server". **The lab is wherever your niche's truth gets tested by the
system itself.** The test for whether you have one is blunt:

> Can the system produce a number, an outcome, or an artifact that does not exist anywhere
> else on the internet?

If yes, you have a lab. If no, you have a research step, and your page will be a better-written
version of what already ranks.

### Email marketing

**Lab:** your email tool. The system builds a real A/B test, sends it to a real segment, and
writes from the actual open and click rates.

**Hands:** the exported report, and screenshots of both variants as subscribers saw them.

A piece on subject lines that cites your own 4,000-recipient test is a different object than
one that cites a listicle of other people's tests. You already run these tests — the change
is treating the result as publishable evidence instead of internal data.

### Personal finance

**Lab:** a spreadsheet or model the system builds and then stress-tests. Run the scenario at
3% and at 9%. Run it through a 2008. Find the input where the advice inverts.

**Hands:** the model itself, downloadable, plus the chart of where it breaks.

The differentiator is almost always the same: everyone explains the rule of thumb, nobody
publishes where it stops working.

### E-commerce, SaaS, or any tool you teach

**Lab:** a demo store or a sandbox account. The system sets up the real flow, walks it,
times it, and breaks it.

**Hands:** screenshots of the real screens — `capture.py` and `auth.py` work unchanged here,
and this is the closest non-software fit to the shipped tooling.

Highest-value experiments: the migration everyone dreads, the setting whose documentation is
wrong, and the limit nobody publishes because you only find it by hitting it.

### Fitness, cooking, crafts, anything physical

**Lab:** the physical attempt, logged. Four proofing times. Three sets of measurements over
six weeks. The same recipe with the substitute ingredient.

**Hands:** you, with a camera, on a schedule the manifest set in advance.

The system cannot run this one — but it can design the protocol, hold you to the schedule,
demand the control condition, and refuse the claim when the evidence file is missing. That
turns out to be most of the value.

### Consulting, B2B, professional services

**Lab:** anonymized client outcomes with real numbers, or a teardown the system performs
live on a public artifact — a real site, a real filing, a real contract, analyzed on camera
against your framework.

**Hands:** the teardown itself, and the before-and-after.

Careful here: the confidentiality gate belongs in the contract as a hard rule, not in your
memory of it. Write it into `SKILL.md` so the system asks before every ship.

## When you genuinely have no lab

Some pieces do not need one — an opinion essay, a personal story, a synthesis where your
argument *is* the contribution. Run those without S4 and say so in the manifest.

What does not change: the claims map, the verification loops, and your read at the end. **A
piece with no lab still needs receipts** for every factual statement in it. Skipping S4 is a
scope decision; skipping S7 is how you publish something wrong.

## The other four blocks

**Contract.** Yours will differ mostly in the gates. Regulated industries add a compliance
checkpoint. A team adds an editor checkpoint. Keep the number of stopping points small —
every checkpoint costs a human context switch, and a pipeline with six of them gets
abandoned.

**Senses.** Outside software, search volume is often the *worst* signal available. A niche
where your five best topics all show "10/mo" is not a niche without demand; it is a niche
your keyword tool cannot see. Weight your comments section, your inbox, and the questions
you get asked on calls above any tool. The recon report has room for both.

**Hands.** `capture.py` handles anything with a URL. Beyond that, "hands" means whatever
turns an outcome into a file: an export, a photo, a recording, a scan. The requirement is
not that it be automated, only that it be *reproducible* — a refresh run has to be able to
produce the same artifact again.

**Brain.** This one is universal and it is the block most people under-build. Ten files
about how you think is the difference between the factory writing *your* piece and writing
*a* piece. Start with your five best stories and the real numbers in them.

## The order to build in

1. **Contract.** One markdown file: your stages, your rules, one checkpoint. Start here even
   if you build nothing else — most of the value is in having written the process down.
2. **Claims map.** The first time it catches an invented number, the whole design clicks.
3. **Brain.** Ten files.
4. **One piece, end to end.** Not ten. Then fix what hurt and run the next one.
5. **The lab.** Last, and only once you know which claim you keep wishing you could prove.
