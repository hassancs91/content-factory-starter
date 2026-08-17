#!/usr/bin/env python3
"""Cloudflare DNS for lab subdomains.

A lot of experiments are only honest with a real hostname: TLS issuance, OAuth
callbacks, webhooks, and any screenshot where the URL bar is part of the proof.

Everything the factory creates lives under a single lab zone, so `sweep` can clean
the whole namespace without risking a record somebody else made. Records are created
UNPROXIED (grey cloud) so the box can issue its own certificates, with a short TTL so
a destroyed box stops resolving quickly.

    python dns.py set myapp 203.0.113.10     # → myapp.<CF_LAB_DNS_ZONE>
    python dns.py rm myapp
    python dns.py list
    python dns.py sweep [--kill]

Config, both from the project-root .env:
    CLOUDFLARE_LAB_DNS_TOKEN   scoped Zone.DNS:Edit token for ONE zone
    CF_LAB_DNS_ZONE            where lab hostnames live, e.g. lab.example.com

Point CF_LAB_DNS_ZONE at a subdomain you use for nothing else. `sweep --kill`
deletes every record under it, which is only safe if the namespace really is
disposable.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import env, require  # noqa: E402

API = "https://api.cloudflare.com/client/v4"
COMMENT = "content-factory"

# e.g. CF_LAB_DNS_ZONE=lab.example.com -> records land at <name>.lab.example.com
# and the Cloudflare zone is example.com.
LAB_SUFFIX = "." + env("CF_LAB_DNS_ZONE", "").strip(".")
ZONE_NAME = ".".join(LAB_SUFFIX.strip(".").split(".")[-2:])


def token():
    if LAB_SUFFIX == ".":
        raise SystemExit(
            "CF_LAB_DNS_ZONE is not set.\n"
            "  Needed for: naming lab subdomains, e.g. CF_LAB_DNS_ZONE=lab.example.com\n"
            "  Add it to your project-root .env."
        )
    return require("CLOUDFLARE_LAB_DNS_TOKEN",
                   "creating and deleting lab DNS records via the Cloudflare API")


def api(method, path, body=None):
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Cloudflare API {method} {path} -> {e.code}: {e.read().decode(errors='replace')}")
    if not data.get("success"):
        sys.exit(f"Cloudflare API error: {data.get('errors')}")
    return data


def zone_id():
    zones = api("GET", f"/zones?name={ZONE_NAME}")["result"]
    if not zones:
        sys.exit(f"Zone {ZONE_NAME} not visible to this token")
    return zones[0]["id"]


def fqdn(name):
    return name if name.endswith(LAB_SUFFIX) else f"{name}{LAB_SUFFIX}"


def lab_records(zid):
    recs = api("GET", f"/zones/{zid}/dns_records?per_page=500")["result"]
    return [r for r in recs if r["name"].endswith(LAB_SUFFIX)]


def cmd_set(args):
    zid = zone_id()
    name = fqdn(args.name)
    body = {"type": "A", "name": name, "content": args.ip, "ttl": 60,
            "proxied": False, "comment": COMMENT}
    existing = [r for r in lab_records(zid) if r["name"] == name and r["type"] == "A"]
    if existing:
        api("PUT", f"/zones/{zid}/dns_records/{existing[0]['id']}", body)
        print(f"updated {name} -> {args.ip}")
    else:
        api("POST", f"/zones/{zid}/dns_records", body)
        print(f"created {name} -> {args.ip}")


def cmd_rm(args):
    zid = zone_id()
    name = fqdn(args.name)
    targets = [r for r in lab_records(zid) if r["name"] == name]
    if not targets:
        print(f"no record for {name}")
        return
    for r in targets:
        api("DELETE", f"/zones/{zid}/dns_records/{r['id']}")
        print(f"deleted {r['type']} {r['name']} -> {r['content']}")


def cmd_list(_args):
    recs = lab_records(zone_id())
    if not recs:
        print(f"no records under *{LAB_SUFFIX}")
    for r in recs:
        print(f"  {r['type']:<5} {r['name']:<45} -> {r['content']}  (proxied={r['proxied']})")


def cmd_sweep(args):
    zid = zone_id()
    recs = lab_records(zid)
    if not recs:
        print("sweep: clean — no lab records")
        return
    for r in recs:
        print(f"  {r['type']:<5} {r['name']:<45} -> {r['content']}")
    if args.kill:
        for r in recs:
            api("DELETE", f"/zones/{zid}/dns_records/{r['id']}")
        print(f"sweep: deleted {len(recs)}")
    else:
        print(f"sweep: {len(recs)} record(s) (use --kill to delete)")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set")
    s.add_argument("name")
    s.add_argument("ip")
    r = sub.add_parser("rm")
    r.add_argument("name")
    sub.add_parser("list")
    w = sub.add_parser("sweep")
    w.add_argument("--kill", action="store_true")
    args = p.parse_args()
    {"set": cmd_set, "rm": cmd_rm, "list": cmd_list, "sweep": cmd_sweep}[args.cmd](args)


if __name__ == "__main__":
    main()
