import sys, random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
NAME = f"app{PORT - 9000}"

PRODUTOS = {
    "1": ("Camiseta", 49.90),
    "2": ("Tênis", 199.90),
    "3": ("Mochila", 89.90),
}


def pagina(corpo):
    return f"<h1>ShopNow</h1>{corpo}<p><small>Respondido pelo servidor: {NAME}</small></p>"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            return self.responder(200, "OK")

        if self.path == "/":
            itens = "".join(
                f'<li>{nome} - R$ {preco:.2f} <a href="/comprar/{id}">Comprar</a></li>'
                for id, (nome, preco) in PRODUTOS.items()
            )
            self.responder(200, pagina(f"<h2>Produtos</h2><ul>{itens}</ul>"))

        elif self.path.startswith("/comprar/") and self.path.split("/")[-1] in PRODUTOS:
            nome, preco = PRODUTOS[self.path.split("/")[-1]]
            pedido = random.randint(100000, 999999)
            self.responder(200, pagina(
                f"<h2>Compra realizada!</h2><p>Pedido #{pedido}</p>"
                f"<p>Produto: {nome}</p><p>Valor: R$ {preco:.2f}</p>"
                f'<a href="/">Voltar</a>'
            ))

        else:
            self.responder(404, pagina("<h2>Página não encontrada</h2>"))

    def responder(self, code, texto):
        body = texto.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer.request_queue_size = 128
    print(f"{NAME} rodando em http://127.0.0.1:{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()