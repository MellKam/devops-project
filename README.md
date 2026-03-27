# Opis Projektu: Docker + DevOps + IaC (Azure w wersji „minimalnej")

## Cel projektu

Celem projektu jest stworzenie kompletnego środowiska dla aplikacji webowej Flask + Nginx + PostgreSQL, które:

1. Całkowicie działa w Dockerze (backend, frontend, baza, migracje, seedowanie, testy).
2. Używa Azure tylko jako minimalnego IaC (np. Resource Group + ACR).
3. Korzysta z wielostopniowego Dockerfile:
   - **builder** — budowanie zależności i aplikacji
   - **test** — uruchamianie pytest
   - **final** — produkcyjny obraz Flask
4. Używa Docker Compose do uruchamiania wszystkich elementów.
5. Wykorzystuje dwie sieci Dockerowe:
   - `front_net` — NGINX ↔ Flask
   - `back_net` — Flask ↔ PostgreSQL
6. Wykorzystuje dedykowane wolumeny:
   - `db_data` — dane PostgreSQL
   - `nginx_logs` — logi NGINX (error + access)
   - `seed_output` — pliki wygenerowane przez seeder
7. Implementuje etap seedowania bazy, który:
   - uruchamia się w osobnym kontenerze `seed_runner`
   - zapisuje pliki do wolumenu `seed_output`
   - wykonuje się po migracjach
8. Zawiera GitHub Actions:
   - pipeline CI z testami i budowaniem obrazu
   - pipeline CD do pull + restart środowiska

---

## Uruchomienie lokalne

```bash
docker compose build --no-cache
docker compose up -d
```

Aplikacja dostępna pod adresem `http://localhost`

| Endpoint | Opis |
|---|---|
| `GET /health/live` | Liveness check |
| `GET /health/ready` | Readiness check (sprawdza bazę) |
| `GET /api/products` | Lista wszystkich produktów |
| `GET /api/products/<id>` | Pojedynczy produkt |


## Testowanie i weryfikacja 

```bash
melkam@melkam:~/devops-project$ docker ps
CONTAINER ID   IMAGE                   COMMAND                  CREATED          STATUS                        PORTS                                 NAMES
65d841cfbd2a   my-devops-project-app   "flask run"              2 minutes ago    Up About a minute (healthy)   5000/tcp                              my-devops-project-app-1
73786538046c   nginx:alpine            "/docker-entrypoint.…"   54 minutes ago   Up 54 minutes                 0.0.0.0:80->80/tcp, [::]:80->80/tcp   my-devops-project-nginx-1
020f03e5a507   postgres:14-alpine      "docker-entrypoint.s…"   54 minutes ago   Up 54 minutes (healthy)       5432/tcp                              my-devops-project-db-1
melkam@melkam:~/devops-project$ curl http://localhost/health/live
{"status":"ok"}
melkam@melkam:~/devops-project$ curl http://localhost/health/ready
{"db":true,"status":"ready"}
melkam@melkam:~/devops-project$ curl http://localhost/api/products
[{"id":1,"name":"Iphone 13","price":599.99},{"id":2,"name":"Samsung Galaxy S21","price":499.99},{"id":3,"name":"Google Pixel 6","price":399.99},{"id":4,"name":"OnePlus 9","price":429.99},{"id":5,"name":"Sony Xperia 5 II","price":949.99}]
melkam@melkam:~/devops-project$ curl http://localhost/api/products/1
{"id":1,"name":"Iphone 13","price":599.99}
melkam@melkam:~/devops-project$ curl http://localhost/api/products/999
{"error":"Not found"}
```