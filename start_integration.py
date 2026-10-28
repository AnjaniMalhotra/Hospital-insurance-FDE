"""Starts the hospital AFTER the FDE (branch fde-solution): Nirmaya Mail, the HMS with the Claim Reconciliation tab
and the Insurer Desk (demo), each as its own process, like separate servers in real life.
Mail and the Insurer Desk are SHARED with the main-branch hospital: if they are already running (started by the
other hospital's start script), they are reused, so both HMS versions can run side by side.
Run: GEMINI_API_KEY=... python start_integration.py      Stop: Ctrl+C       Reset the demo data first with: python demo/seed.py
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORTS = {"mail": 8025, "smtp": 2525, "hms": 8062, "desk": 8070}  # main's HMS is on 8061; mail + desk are shared
SERVICES = [  # (name, script, port, shared with the other hospital?, what it is)
    ("Nirmaya Mail", "mail_portal/backend/server.py", PORTS["mail"], True, f"webmail  (SMTP on port {PORTS['smtp']})"),
    ("Nirmaya HMS", "integration/backend/app.py", PORTS["hms"], False, "the hospital's HMS + Claim Reconciliation tab"),
    ("Insurer Desk", "demo/insurer_desk/app.py", PORTS["desk"], True, "DEMO TOOL: plays the insurers"),
]
ADDRESSES = {  # how this hospital's services find each other
    "SMTP_PORT": str(PORTS["smtp"]), "HMS_URL": f"http://localhost:{PORTS['hms']}", "HMS_WEB": f"http://localhost:{PORTS['hms']}",
    "MAIL_URL": f"http://localhost:{PORTS['mail']}", "MAIL_WEB": f"http://localhost:{PORTS['mail']}",
}


def running(port):
    """Is something already listening on this port? (e.g. the shared Mail or Desk, started by the other hospital)"""
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    if not (ROOT / "integration" / "database" / "hms.db").exists():
        print("No HMS database yet: seeding the demo data first...")
        subprocess.run([sys.executable, str(ROOT / "demo" / "seed.py")], check=True)
    procs, lines = [], []
    for name, script, port, shared, what in SERVICES:
        if shared and running(port):
            lines.append(f"  SHARED {name:15} http://localhost:{port}   already running (started by the other hospital)")
            continue
        procs.append(subprocess.Popen([sys.executable, str(ROOT / script)], cwd=ROOT, env={**os.environ, **ADDRESSES,
                                      "PORT": str(port)}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        lines.append((procs[-1], f"{name:15} http://localhost:{port}   {what}"))
    time.sleep(3)
    print("\nAll systems running:\n")
    for line in lines:
        print(line if isinstance(line, str) else f"  {'OK  ' if line[0].poll() is None else 'FAIL'}   {line[1]}")
    print("\nPress Ctrl+C to stop this hospital (shared services stop with the hospital that started them).")
    try:
        while all(p.poll() is None for p in procs):
            time.sleep(1)
        print("A service stopped unexpectedly (is its port already in use?). Stopping the rest.")
    except KeyboardInterrupt:
        pass
    for p in procs:
        p.terminate()


if __name__ == "__main__":
    main()
