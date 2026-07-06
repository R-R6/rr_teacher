"""Probe CloudRun endpoints (no secrets)."""
import re
import sys
import urllib.error
import urllib.request

BASE = "https://chem-backend-268016-4-1440725000.sh.run.tcloudbase.com"


def fetch(path: str, timeout: int = 20):
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": "probe-cloudrun/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, dict(resp.headers.items()), resp.read()


def main() -> int:
    paths = ["/health", "/admin-console/", "/admin-console/index.html"]
    for path in paths:
        try:
            status, headers, body = fetch(path)
            server = headers.get("Server", "")
            print(f"{path}\t{status}\tserver={server}\tbody={body[:80]!r}")
        except urllib.error.HTTPError as exc:
            server = exc.headers.get("Server", "") if exc.headers else ""
            print(f"{path}\tHTTP {exc.code}\tserver={server}\tbody={exc.read()[:120]!r}")
        except Exception as exc:
            print(f"{path}\tERR {type(exc).__name__}: {exc}")

    try:
        _, _, html_bytes = fetch("/admin-console/")
        html = html_bytes.decode("utf-8", "replace")
        assets = re.findall(r'(?:src|href)="([^"]+)"', html)
        print("assets:", assets)
        for asset in assets:
            if asset.startswith("http"):
                continue
            path = asset if asset.startswith("/") else f"/admin-console/{asset.lstrip('./')}"
            try:
                status, headers, _ = fetch(path)
                print(f"  {path}\t{status}\tserver={headers.get('Server', '')}")
            except urllib.error.HTTPError as exc:
                server = exc.headers.get("Server", "") if exc.headers else ""
                print(f"  {path}\tHTTP {exc.code}\tserver={server}")
            except Exception as exc:
                print(f"  {path}\tERR {exc}")
    except Exception as exc:
        print("asset probe failed:", exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
