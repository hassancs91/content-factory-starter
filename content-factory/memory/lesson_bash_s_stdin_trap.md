# Upload droplet scripts, never pipe them: the `bash -s` stdin trap

**What happened (update-docker-containers, 2026-08-11):** E1 ran via
`do.py run <slug> -- 'bash -s' < script.sh`. The script died silently at its first
`docker compose exec -T db psql ...` line, with exit 0: `exec -T` hands the executing
process the script's OWN stdin, and psql consumed the entire rest of the script as
input. Everything after that line simply never ran, and nothing failed.

**Rule:** any command that reads stdin (`psql`, `mysql`, `ssh`, `docker exec -T`,
`cat`, `read`) inside a piped script will eat the script. Upload-then-execute instead:

```bash
do.py run <slug> -- 'cat > /root/e1.sh' < scripts/e1.sh
do.py run <slug> -- 'bash /root/e1.sh'  > evidence/e1.out 2>&1
```

Two ways it hides: exit code is 0 (the eater exits happily), and the output file ends
mid-experiment looking like a truncation, not a failure. If an evidence file ends
earlier than the script's last `echo`, suspect this first.

Related: [[lesson_experiments_that_break_their_transport]] (same family: the transport
and the experiment interfering with each other).
