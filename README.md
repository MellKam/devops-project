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

## Wymagania funkcjonalne projektu

### 1. Aplikacja Flask
- Prosta aplikacja HTTP (np. endpoint `/health` + 2–3 inne)
- Połączona z bazą PostgreSQL
- Zawiera przykładowy model (np. Users, Tasks, Products)
- Zawiera testy pytest (minimum: 3 testy)

### 2. Dockerfile — obowiązkowe etapy

#### Etap 1 — builder
- Instaluje pełne zależności z `requirements.txt`
- Instaluje dodatkowe zależności na potrzeby wymagań
- Kopiuje kod aplikacji
- Służy jako baza dla testów i finala

#### Etap 2 — test
- Korzysta z buildera
- Uruchamia pytest
- Jeśli testy nie przejdą → build jest zatrzymany

#### Etap 3 — final
- Lekki obraz produkcyjny (`python-slim`)
- Kopiuje tylko kod i zależności z buildera
- Używany przez docker-compose w środowisku runtime

### 3. Docker Compose — obowiązkowe usługi

| Usługa | Opis |
|---|---|
| `app` | Flask (obraz final), używa obu sieci `front_net` + `back_net`, zależność od `db` i `seed_runner` |
| `nginx` | Reverse proxy kierujący ruch do Flask, logi zapisane do wolumenu `nginx_logs` |
| `db` | PostgreSQL, trwałe dane w wolumenie `db_data`, działa tylko w sieci `back_net` |
| `migration_runner` | Jednorazowy kontener wykonujący migracje (opcjonalnie, ale zalecane) |
| `seed_runner` | Jednorazowy kontener seedujący bazę i generujący pliki do `seed_output` |

**Sieci:**
- `front_net` — dla ruchu publicznego (NGINX ↔ Flask)
- `back_net` — dla bazy (Flask ↔ PostgreSQL)

**Wolumeny:**
- `db_data` — dane PostgreSQL
- `nginx_logs` — logi NGINX
- `seed_output` — pliki seedera

### 4. Seeder bazy — wymagania

Seeder ma:
- być osobnym skryptem Python lub Bash
- uruchamiać się jako kontener
- tworzyć dane startowe (min. 5 rekordów)
- generować pliki:
  - `seed.log`
  - np. `products.csv`, `data.json`
- zapisywać pliki do wolumenu `seed_output`
- kończyć działanie, nie działać nonstop

### 5. Testy (pytest)

Wymagane minimum:
- 1 test jednostkowy
- 1 test logiki aplikacji
- 1 test endpointu HTTP (np. `/health`)
- testy muszą być uruchamiane w build stage

### 6. GitHub Actions — obowiązkowe elementy

#### CI Pipeline
- uruchamia się na `pull_request` i `push`
- kroki:
  1. Checkout
  2. Build image (builder)
  3. Run test stage (pytest)
  4. Build final image
  5. Push obrazu do ACR lub GHCR
  6. CodeQL scan (minimalna konfiguracja)

#### CD Pipeline
- uruchamiany ręcznie lub z tagów
- pobiera obraz
- wykonuje `docker compose pull`
- wykonuje `docker compose up -d`
- restartuje aplikację

### 7. Azure IaC (minimum wymagane)

W katalogu `infra/` musi znaleźć się plik Bicep lub ARM, który tworzy:
- **Resource Group** — wymagane
- **Azure Container Registry (ACR)** — wymagane
- Storage Account — opcjonalnie

> Środowisko produkcyjne nie działa w Azure — Azure jest tu tylko jako IaC + registry.

### 8. Oczekiwana struktura repozytorium

```
.
├── app/
│   ├── src/
│   ├── tests/
│   ├── seed/
│   │   └── run_seed.py
│   ├── requirements.txt
│   └── migrations/
│
├── docker/
│   ├── nginx.conf
│   └── seed_script.sh (opcjonalnie)
│
├── Dockerfile
├── docker-compose.yml
│
├── infra/
│   ├── main.bicep
│   ├── parameters.json
│   └── README.md
│
└── .github/workflows/
    ├── ci.yml
    └── cd.yml
```

---

## Co będzie oceniane?

| Obszar | Waga |
|---|---|
| Dockerfile (builder/test/final) | 25% |
| Docker Compose (sieci, wolumeny, seed, nginx) | 25% |
| GitHub Actions CI/CD | 20% |
| IaC (Azure Bicep/ARM) | 10% |
| Seeder + migracje | 10% |
| Jakość kodu i testów | 10% |

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
