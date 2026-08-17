#!/usr/bin/env python3
"""DigitalOcean VM lifecycle for the content factory.

Stdlib only. Every box is named cf-<slug> and tagged 'content-factory', so `sweep`
can always find anything this tool ever created — which is the whole reason an
abandoned experiment box cannot quietly bill you for a month.

Destroy is guarded: it refuses any box a live session holds, or that another piece
names in its PIECE.md lab_resources. See modules/lab.md for the full command list.

Config, all from the project-root .env:
    DO_TOKEN         DigitalOcean API token (required)
    CF_LAB_SSH_KEY   private key for lab boxes (default ~/.ssh/cf_lab)
    CF_LAB_REGION    default region (default fra1)
    CF_LAB_SIZE      default droplet size (default s-2vcpu-4gb)

To use a different cloud, this is the only file to rewrite: the rest of the
pipeline only ever asks it for "a box named cf-<slug>", and for it to go away.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import CONTENT_LAB, env, require  # noqa: E402

API = "https://api.digitalocean.com/v2"
KEY_PATH = Path(env("CF_LAB_SSH_KEY", str(Path.home() / ".ssh" / "cf_lab"))).expanduser()
KEY_NAME = "content-factory-lab"
KNOWN_HOSTS = CONTENT_LAB / ".ssh_known_hosts"
KNOWN_HOSTS_DIR = CONTENT_LAB / ".ssh_known_hosts.d"
TAG = "content-factory"
DEFAULT_SIZE = env("CF_LAB_SIZE", "s-2vcpu-4gb")
GOLDEN_BUILD_SIZE = "s-1vcpu-2gb"  # build the golden on the smallest disk we will ever boot
DEFAULT_REGION = env("CF_LAB_REGION", "fra1")
BASE_IMAGE = "ubuntu-24-04-x64"


def token():
    return require("DO_TOKEN", "creating and destroying lab VMs via the DigitalOcean API")


def api(method, path, body=None):
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"DO API {method} {path} -> {e.code}: {detail}")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------- parallel-session guard ---
# Destroying a droplet is irreversible and cheap to trigger by accident: the S4
# hard rule is "`sweep` must come back empty", which reads as an instruction to
# kill everything — including the box another session is running experiments on.
# So both destructive paths ask the lock + the ledger who else cares first.

def _factory():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import ledger
        import lock
        return lock, ledger
    except Exception:
        return None, None


def piece_of(droplet_name: str) -> str:
    return droplet_name[3:] if droplet_name.startswith("cf-") else droplet_name


def lock_holder(slug: str):
    """(state, who) for a piece lock — ('MINE'|'LIVE'|'DEAD'|..., label) or (None, None)."""
    lock, _ = _factory()
    if not lock:
        return None, None
    p = lock.LOCK_DIR / f"{slug}.lock"
    if not p.exists():
        return None, None
    data = lock._read(p)
    return lock.liveness(data), (data.get("label") or data.get("session") or "?")[:8]


def pieces_referencing(*tokens) -> list:
    """Slugs whose PIECE.md `lab_resources` names this droplet or IP. Catches the
    borrowed-box case: one piece owns `cf-<slug>`, a sibling piece is using it."""
    _, ledger = _factory()
    if not ledger:
        return []
    live = [t for t in tokens if t]
    return [p["slug"] for p in ledger.pieces()
            if any(t in (p.get("lab_resources") or "") for t in live)]


def destroy_blockers(name: str, ip: str = "") -> list:
    slug = piece_of(name)
    out = []
    state, who = lock_holder(slug)
    if state in ("LIVE", "HELD"):
        out.append(f"session `{who}` holds the `{slug}` lock ({state}) — it may be mid-experiment")
    for other in sorted(set(pieces_referencing(name, ip)) - {slug}):
        o_state, o_who = lock_holder(other)
        held = f", locked by `{o_who}`" if o_state in ("LIVE", "HELD", "MINE") else ""
        out.append(f"piece `{other}` lists it in lab_resources{held}")
    return out


def full_name(slug):
    return slug if slug.startswith("cf-") else f"cf-{slug}"


def find_droplets(name=None):
    out, page = [], 1
    while True:
        d = api("GET", f"/droplets?per_page=200&page={page}&tag_name={TAG}")
        out += d.get("droplets", [])
        if not d.get("links", {}).get("pages", {}).get("next"):
            break
        page += 1
    # Safety net: also catch cf-* droplets that somehow lost the tag
    d2 = api("GET", "/droplets?per_page=200")
    seen = {x["id"] for x in out}
    out += [x for x in d2.get("droplets", []) if x["name"].startswith("cf-") and x["id"] not in seen]
    if name:
        out = [x for x in out if x["name"] == name]
    return out


def droplet_ip(d):
    for net in d.get("networks", {}).get("v4", []):
        if net.get("type") == "public":
            return net.get("ip_address")
    return None


def wait_for(desc, fn, timeout, interval=6):
    start = time.time()
    while time.time() - start < timeout:
        result = fn()
        if result:
            return result
        time.sleep(interval)
    sys.exit(f"Timed out after {timeout}s waiting for: {desc}")


def ensure_ssh_key():
    if not KEY_PATH.exists():
        log(f"Generating dedicated lab key at {KEY_PATH}")
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", str(KEY_PATH), "-N", "", "-C", KEY_NAME],
            check=True, capture_output=True,
        )
    pub = (KEY_PATH.with_suffix(".pub")).read_text().strip()
    for k in api("GET", "/account/keys?per_page=200").get("ssh_keys", []):
        if k["name"] == KEY_NAME or k["public_key"].split()[1] == pub.split()[1]:
            return k["fingerprint"]
    log("Registering lab key with DigitalOcean")
    return api("POST", "/account/keys", {"name": KEY_NAME, "public_key": pub})["ssh_key"]["fingerprint"]


def latest_golden():
    snaps = [s for s in api("GET", "/snapshots?resource_type=droplet&per_page=200").get("snapshots", [])
             if s["name"].startswith("cf-golden")]
    return max(snaps, key=lambda s: s["created_at"]) if snaps else None


def known_hosts_for(slug=None) -> Path:
    """Per-piece known_hosts. `StrictHostKeyChecking=accept-new` makes ssh APPEND to
    this file, so two sessions sshing at the same moment can interleave writes into
    one shared file and produce a corrupt entry — which surfaces later as a bogus
    host-key failure that looks like an attack, not a race."""
    if not slug:
        return KNOWN_HOSTS
    KNOWN_HOSTS_DIR.mkdir(parents=True, exist_ok=True)
    return KNOWN_HOSTS_DIR / f"{piece_of(slug)}.known_hosts"


def ssh_base(ip, slug=None):
    kh = known_hosts_for(slug)
    kh.parent.mkdir(parents=True, exist_ok=True)
    return [
        "ssh", "-i", str(KEY_PATH),
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", f"UserKnownHostsFile={kh}",
        "-o", "ConnectTimeout=10",
        "-o", "BatchMode=yes",
        f"root@{ip}",
    ]


def wait_ssh(ip, slug=None, timeout=240):
    def probe():
        r = subprocess.run(ssh_base(ip, slug) + ["echo ok"], capture_output=True, text=True)
        return r.returncode == 0
    wait_for(f"SSH on {ip}", probe, timeout, interval=10)


def create(slug, size=DEFAULT_SIZE, region=DEFAULT_REGION, image=None, wait_boot=True):
    name = full_name(slug)
    if find_droplets(name):
        sys.exit(f"{name} already exists — destroy it first or pick another slug")
    fingerprint = ensure_ssh_key()
    if image in (None, "golden"):
        g = latest_golden()
        if g:
            image_id, image_desc = g["id"], f"snapshot {g['name']}"
        else:
            image_id, image_desc = BASE_IMAGE, f"base {BASE_IMAGE} (no golden snapshot yet)"
    else:
        image_id, image_desc = image, str(image)
    log(f"Creating {name} ({size}, {region}, {image_desc})")
    d = api("POST", "/droplets", {
        "name": name, "region": region, "size": size, "image": image_id,
        "ssh_keys": [fingerprint], "tags": [TAG], "monitoring": False, "backups": False,
    })["droplet"]
    if not wait_boot:
        return d
    d = wait_for(f"{name} active", lambda: next(
        (x for x in find_droplets(name) if x["status"] == "active" and droplet_ip(x)), None), 300)
    ip = droplet_ip(d)
    log(f"{name} active at {ip}; waiting for SSH")
    wait_ssh(ip, slug)
    log(f"{name} ready: root@{ip}")
    print(ip)
    return d


def destroy(slug, force=False):
    name = full_name(slug)
    targets = find_droplets(name)
    if not targets:
        log(f"No droplet named {name}")
        return
    blockers = destroy_blockers(name, droplet_ip(targets[0]) or "")
    if blockers and not force:
        print(f"[BLOCKED] refusing to destroy {name}:")
        for b in blockers:
            print(f"  - {b}")
        print("\n  Destroying it would delete evidence another piece still depends on.")
        print("  Clear the reference from that piece's PIECE.md `lab_resources` (or wait")
        print("  for its session to finish), then re-run. Override: --force")
        sys.exit(1)
    for d in targets:
        log(f"Destroying {d['name']} (id {d['id']})")
        api("DELETE", f"/droplets/{d['id']}")
    wait_for(f"{name} gone", lambda: not find_droplets(name), 120)
    log(f"{name} destroyed")


def sweep(kill=False, force=False):
    alive = find_droplets()
    if not alive:
        print("sweep: clean — no cf-* droplets alive")
        return
    guarded, free = [], []
    for d in alive:
        blockers = destroy_blockers(d["name"], droplet_ip(d) or "")
        (guarded if blockers else free).append((d, blockers))
        flag = "  [GUARDED]" if blockers else ""
        print(f"  {d['name']}  {d['status']}  {droplet_ip(d) or '-'}  "
              f"{d['size_slug']}  created {d['created_at']}{flag}")
        for b in blockers:
            print(f"      ↳ {b}")
    if not kill:
        print(f"sweep: {len(alive)} alive ({len(guarded)} guarded) — use --kill to destroy")
        return
    targets = alive if force else [d for d, _ in free]
    skipped = [] if force else [d["name"] for d, _ in guarded]
    for d in targets:
        log(f"Destroying {d['name']}")
        api("DELETE", f"/droplets/{d['id']}")
    if targets:
        wait_for("swept droplets gone",
                 lambda: not [x for x in find_droplets()
                              if x["id"] in {t["id"] for t in targets}], 180)
    print(f"sweep: killed {len(targets)}")
    if skipped:
        # Never let a teardown report "clean" when it deliberately left boxes alive.
        print(f"sweep: SKIPPED {len(skipped)} guarded droplet(s): {', '.join(skipped)}")
        print("       Another piece still claims them. Use --kill --force to override.")


def snapshot(slug, snap_name):
    name = full_name(slug)
    d = (find_droplets(name) or sys.exit(f"No droplet {name}"))[0]
    log(f"Powering off {name}")
    api("POST", f"/droplets/{d['id']}/actions", {"type": "shutdown"})
    deadline = time.time() + 180
    while time.time() < deadline:
        if any(x["status"] == "off" for x in find_droplets(name)):
            break
        time.sleep(8)
    else:  # graceful shutdown didn't take — force it
        log("Graceful shutdown timed out; forcing power_off")
        api("POST", f"/droplets/{d['id']}/actions", {"type": "power_off"})
        wait_for(f"{name} off (forced)", lambda: next(
            (x for x in find_droplets(name) if x["status"] == "off"), None), 120, interval=8)
    log(f"Snapshotting as {snap_name} (this is the slow part)")
    act = api("POST", f"/droplets/{d['id']}/actions", {"type": "snapshot", "name": snap_name})["action"]
    wait_for(f"snapshot {snap_name}", lambda: api(
        "GET", f"/actions/{act['id']}")["action"]["status"] == "completed", 1800, interval=20)
    log(f"Snapshot {snap_name} done")


def golden(size=GOLDEN_BUILD_SIZE, region=DEFAULT_REGION):
    slug = "golden-build"
    snap_name = f"cf-golden-{date.today().strftime('%Y%m%d')}"
    d = create(slug, size=size, region=region, image=BASE_IMAGE)
    ip = droplet_ip(find_droplets(full_name(slug))[0])
    bootstrap = Path(__file__).parent / "bootstrap-ubuntu.sh"
    log(f"Running bootstrap on {ip}")
    with open(bootstrap, "rb") as f:
        r = subprocess.run(ssh_base(ip, slug) + ["bash -s"], stdin=f, capture_output=True, text=True)
    print(r.stdout[-3000:])
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        sys.exit(f"bootstrap failed (exit {r.returncode}) — droplet {full_name(slug)} left alive for debugging")
    snapshot(slug, snap_name)
    destroy(slug, force=True)      # golden-build is never a piece's lab box
    log(f"Golden image ready: {snap_name}")


def run_cmd(slug, command):
    name = full_name(slug)
    d = (find_droplets(name) or sys.exit(f"No droplet {name}"))[0]
    ip = droplet_ip(d)
    r = subprocess.run(ssh_base(ip, slug) + [command],
                       stdin=sys.stdin if not sys.stdin.isatty() else None)
    sys.exit(r.returncode)


def list_all():
    ds = find_droplets()
    print(f"droplets ({len(ds)}):")
    for d in ds:
        print(f"  {d['name']}  {d['status']}  {droplet_ip(d) or '-'}  {d['size_slug']}  {d['region']['slug']}")
    snaps = api("GET", "/snapshots?resource_type=droplet&per_page=200").get("snapshots", [])
    print(f"snapshots ({len(snaps)}):")
    for s in snaps:
        print(f"  {s['name']}  {s['size_gigabytes']}GB  {s['regions']}  {s['created_at']}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ssh-key")
    sub.add_parser("list")
    sub.add_parser("golden")
    c = sub.add_parser("create")
    c.add_argument("slug")
    c.add_argument("--size", default=DEFAULT_SIZE)
    c.add_argument("--region", default=DEFAULT_REGION)
    c.add_argument("--image", default=None, help="'golden' (default), snapshot id, or base image slug")
    d = sub.add_parser("destroy")
    d.add_argument("slug")
    d.add_argument("--force", action="store_true",
                   help="destroy even if another piece/session still claims it")
    s = sub.add_parser("sweep")
    s.add_argument("--kill", action="store_true")
    s.add_argument("--force", action="store_true",
                   help="with --kill, also destroy guarded droplets")
    sn = sub.add_parser("snapshot")
    sn.add_argument("slug")
    sn.add_argument("name")
    ipp = sub.add_parser("ip")
    ipp.add_argument("slug")
    r = sub.add_parser("run")
    r.add_argument("slug")
    r.add_argument("command", nargs=argparse.REMAINDER, help="command to run (prefix with --)")
    sc = sub.add_parser("ssh-cmd")
    sc.add_argument("slug")
    a = p.parse_args()

    if a.cmd == "ssh-key":
        print("fingerprint:", ensure_ssh_key())
    elif a.cmd == "list":
        list_all()
    elif a.cmd == "golden":
        golden()
    elif a.cmd == "create":
        create(a.slug, size=a.size, region=a.region, image=a.image)
    elif a.cmd == "destroy":
        destroy(a.slug, force=a.force)
    elif a.cmd == "sweep":
        sweep(kill=a.kill, force=a.force)
    elif a.cmd == "snapshot":
        snapshot(a.slug, a.name)
    elif a.cmd == "ip":
        dd = find_droplets(full_name(a.slug)) or sys.exit(f"No droplet {full_name(a.slug)}")
        print(droplet_ip(dd[0]))
    elif a.cmd == "run":
        cmd = a.command[1:] if a.command and a.command[0] == "--" else a.command
        run_cmd(a.slug, " ".join(cmd) if cmd else sys.exit("no command given"))
    elif a.cmd == "ssh-cmd":
        dd = find_droplets(full_name(a.slug)) or sys.exit(f"No droplet {full_name(a.slug)}")
        print(" ".join(ssh_base(droplet_ip(dd[0]), a.slug)))


if __name__ == "__main__":
    main()
