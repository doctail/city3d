import json, sys, urllib.request

U = "https://nodum.md/api/v1/mcp"
H = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def post(body, sid=None):
    h = dict(H)
    if sid:
        h["Mcp-Session-Id"] = sid
    r = urllib.request.urlopen(urllib.request.Request(U, json.dumps(body).encode(), h), timeout=60)
    return r.headers.get("Mcp-Session-Id"), r.read().decode()


def call(name, args):
    sid, _ = post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                   "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                              "clientInfo": {"name": "yb", "version": "0"}}})
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    _, t = post({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                 "params": {"name": name, "arguments": args}}, sid)
    d = [l[5:] for l in t.splitlines() if l.startswith("data:")]
    return json.loads(d[-1]) if d else t


if __name__ == "__main__":
    args = json.load(open(sys.argv[2])) if sys.argv[2].endswith(".json") else json.loads(sys.argv[2])
    out = call(sys.argv[1], args)
    r = out.get("result", out) if isinstance(out, dict) else out
    s = json.dumps(r.get("structuredContent", r) if isinstance(r, dict) else r, ensure_ascii=False)
    print(s[: int(sys.argv[3]) if len(sys.argv) > 3 else 1500])
