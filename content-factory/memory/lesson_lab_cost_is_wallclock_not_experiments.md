---
name: lesson_lab_cost_is_wallclock_not_experiments
description: Droplet cost tracks how long the box stays alive, not how many experiments run on it — estimate the session shape, and never install iptables-persistent on a ufw box.
---

# Lab cost is wall-clock, not experiment count

`secure-coolify-vps` estimated **$1.20** at Checkpoint 1 for eleven experiments on one
`s-2vcpu-4gb`, budgeting 24 h of droplet life plus a second boot in case the baseline got
contaminated. Actual: **$0.04**. The box lived 55 minutes and everything ran in one pass.

The estimate was not wrong about the work, it was wrong about the *shape of the session*.
Eleven experiments cost four cents because they ran back to back on a box that was already
warm.

**When writing a manifest, estimate two things separately:**

1. How long the box has to stay alive. That is the entire cost. Anything with a wait in it
   (a 24 h scan window, a certificate renewal, an overnight) dominates; a dense run of
   scripted experiments is nearly free.
2. Whether a second clean boot is genuinely needed. Reserve it only when a later experiment
   *destroys* the state an earlier one measured. On this piece E2 did contaminate the
   baseline, and it still did not matter, because E1's evidence was already captured.

Over-estimating is cheap and under-estimating triggers the >50% stop-and-ask rule, so keep
padding the estimate. But say in the manifest which line item is the wall-clock driver, so
the owner is approving a *duration*, not a vague number.

## The trap that cost a rebuild

**Never `apt install iptables-persistent` on a box running ufw.** On Ubuntu 24.04 the
packages conflict and apt **removes ufw** to satisfy the install. Under `apt -y` there is
no prompt and nothing in the foreground output says so; it shows up only in
`/var/log/apt/history.log`. It left the lab box with no firewall mid-experiment.

To persist iptables rules on a ufw box, append them to `/etc/ufw/after.rules` instead. ufw
reapplies that file at boot and on `ufw reload`, it holds only your rules, and it needs
nothing installed. Verified across a container restart, a `systemctl restart docker`, and a
full reboot.
