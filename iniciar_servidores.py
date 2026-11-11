import os, subprocess, sys, time

PASTA = os.path.dirname(os.path.abspath(__file__))
PORTAS = [9001, 9002, 9003]

processos = []
for porta in PORTAS:
    processos.append(subprocess.Popen([sys.executable, "app.py", str(porta)], cwd=PASTA))

print("3 servidores iniciados. Ctrl+C para parar todos.", flush=True)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    for p in processos:
        p.terminate()
    print("Servidores parados")
