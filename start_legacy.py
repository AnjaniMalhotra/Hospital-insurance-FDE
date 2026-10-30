"""Starts the hospital as it works TODAY (branch main): Nirmaya Mail, the legacy HMS and the Insurer Desk (demo),
each as its own process, like separate servers in real life.
Run: python start_legacy.py      Stop: Ctrl+C       Reset the demo data first with: python demo/seed.py
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# The three systems to start: each with its script and port.
SERVICES = [  # (name, script, port, what it is)
    ("Nirmaya Mail", "mail_portal/backend/server.py", 8025, "webmail  (SMTP on port 2525)"),
    ("Nirmaya HMS", "legacy_system/backend/app.py", 8061, "the hospital's HMS (original)"),
    ("Insurer Desk", "demo/insurer_desk/app.py", 8070, "DEMO TOOL: plays the insurers"),
]


# Starts all three systems, prints their addresses, and stops them when you press Ctrl+C.
def main():
    if not (ROOT / "database" / "hms.db").exists():
        print("No HMS database yet: seeding the demo data first...")
        subprocess.run([sys.executable, str(ROOT / "demo" / "seed.py")], check=True)
    procs = []
    for name, script, port, _ in SERVICES:
        procs.append(subprocess.Popen([sys.executable, str(ROOT / script)], cwd=ROOT, env={**os.environ, "PORT": str(port)},
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    time.sleep(3)
    print("\nAll systems running:\n")
    for (name, _, port, what), p in zip(SERVICES, procs):
        print(f"  {'OK  ' if p.poll() is None else 'FAIL'} {name:15} http://localhost:{port}   {what}")
    print("\nPress Ctrl+C to stop everything.")
    try:
        while all(p.poll() is None for p in procs):
            time.sleep(1)
        print("A service stopped unexpectedly (is its port already in use?). Stopping the rest.")
    except KeyboardInterrupt:
        pass
    for p in procs:
        p.terminate()


# Runs main() when this file is started directly.
if __name__ == "__main__":
    main()
