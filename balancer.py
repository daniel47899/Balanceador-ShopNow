import json, time, random, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError

BACKENDS = ["http://127.0.0.1:9001", "http://127.0.0.1:9002", "http://127.0.0.1:9003"]
ALGORITHM = "round_robin"

lock = threading.Lock()
state = {b: {"alive": True, "total": 0} for b in BACKENDS}
rr_index = 0


def choose(tried):
    global rr_index
    with lock:
        candidates = [b for b in BACKENDS if state[b]["alive"] and b not in tried]
        if not candidates:
            return None

        if ALGORITHM == "random":
            chosen = random.choice(candidates)
        else:
            chosen = None
            for _ in range(len(BACKENDS)):
                b = BACKENDS[rr_index % len(BACKENDS)]
                rr_index += 1
                if b in candidates:
                    chosen = b
                    break

        state[chosen]["total"] += 1
        return chosen


def health_check():
    while True:
        for b in BACKENDS:
            try:
                urlopen(b + "/health", timeout=1).read()
                alive = True
            except Exception:
                alive = False
            with lock:
                if state[b]["alive"] != alive:
                    print(f"[HEALTH] {b} -> {'UP' if alive else 'DOWN'}", flush=True)
                state[b]["alive"] = alive
        time.sleep(2)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global ALGORITHM
        if self.path.startswith("/algorithm/"):
            novo = self.path.split("/")[-1]
            if novo not in ("round_robin", "random"):
                return self.reply(400, b"Use round_robin ou random", "text/plain")
            with lock:
                ALGORITHM = novo
                for b in BACKENDS:
                    state[b]["total"] = 0
            print(f"[ALGORITMO] trocado para {novo}", flush=True)
            return self.reply(200, f"Algoritmo: {novo}".encode(), "text/plain")

        if self.path == "/favicon.ico":
            return self.reply(204, b"", "image/x-icon")

        if self.path == "/status":
            with lock:
                body = json.dumps({"algorithm": ALGORITHM, "backends": state}, indent=2).encode()
            return self.reply(200, body, "application/json")

        tried = set()
        while True:
            backend = choose(tried)
            if backend is None:
                return self.reply(503, b"Nenhum servidor disponivel", "text/plain")
            try:
                resp = urlopen(backend + self.path, timeout=5)
                return self.reply(resp.status, resp.read(), "text/html; charset=utf-8")
            except HTTPError as e:
                return self.reply(e.code, e.read(), "text/html")
            except Exception:
                with lock:
                    state[backend]["alive"] = False
                print(f"[FAILOVER] {backend} falhou, tentando outro", flush=True)
                tried.add(backend)

    def reply(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    threading.Thread(target=health_check, daemon=True).start()
    print(f"Balanceador rodando na porta 8080 | algoritmo: {ALGORITHM}", flush=True)
    ThreadingHTTPServer.request_queue_size = 128
    ThreadingHTTPServer(("127.0.0.1", 8080), Handler).serve_forever()