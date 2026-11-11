# ShopNow - Balanceador de Carga

3 instâncias do site da ShopNow + balanceador de carga em Python (somente biblioteca padrão).

## Requisitos

- Python 3
- Apache Benchmark (`ab`) no PATH, para os testes de carga. No PowerShell, na janela onde for rodar os testes:

```
$env:Path += ";CAMINHO_DO_APACHE\Apache24\bin"
```

## Como rodar

Em 2 terminais, na pasta do projeto:

```
python iniciar_servidores.py     # sobe app1, app2 e app3 (portas 9001, 9002, 9003)
python balancer.py               # sobe o balanceador (porta 8080)
```

Acesse http://127.0.0.1:8080. Para simular uma compra: http://127.0.0.1:8080/comprar/1 (produtos 1, 2 e 3).

O endereço http://127.0.0.1:8080/status mostra o algoritmo ativo e quantas requisições cada servidor recebeu.

## Algoritmos

- **Round Robin**: reveza as requisições entre os servidores vivos.
- **Random**: escolhe aleatoriamente um dos servidores vivos.

Para trocar em tempo real, sem reiniciar nada (zera os contadores do `/status`):

```
http://127.0.0.1:8080/algorithm/round_robin
http://127.0.0.1:8080/algorithm/random
```

## Tolerância a falhas

- **Health check**: a cada 2s o balanceador consulta `/health` de cada servidor e o marca como UP ou DOWN.
- **Failover**: se um servidor falha durante uma requisição, o balanceador tenta outro.
- Se todos caírem, responde 503.

## Testes (Apache Benchmark)

Com os servidores e o balanceador rodando, em um terceiro terminal.

Carga com Round Robin:

```
curl.exe http://127.0.0.1:8080/algorithm/round_robin
ab -n 2000 -c 50 http://127.0.0.1:8080/
curl.exe http://127.0.0.1:8080/status
```

Carga com Random:

```
curl.exe http://127.0.0.1:8080/algorithm/random
ab -n 2000 -c 50 http://127.0.0.1:8080/
curl.exe http://127.0.0.1:8080/status
```

Falha de servidor durante a carga (30000 requisições, e o app2 é derrubado depois de 5s):

```
.\carga_com_falha.bat
```

O esperado é `Failed requests: 0` e o app2 com `"alive": false` e menos requisições que os outros. O terminal do balanceador mostra `[HEALTH] ... -> DOWN` e `[FAILOVER]`.

Para religar o app2 (em outro terminal): `python app.py 9002`. Em até 2s o health check o marca como UP.

## Resultados

| Teste | Req/s | Tempo por requisição | Falhas | app1 / app2 / app3 |
|---|---|---|---|---|
| Round Robin | | | | |
| Random | | | | |
| Falha do app2 (Round Robin) | | | | |

git
https://github.com/daniel47899/Balanceador-ShopNow