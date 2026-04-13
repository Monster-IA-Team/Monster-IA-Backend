# FastAPI + PostgreSQL Boilerplate

Prosty boilerplate do szybkiego startu projektu z **FastAPI** i **PostgreSQL**.
Obsługuje Windows i Linux, z Dockerem i `.env` do konfiguracji portów i bazy danych.

---

## Struktura projektu

```
./
├── app/
│   └── main.py
├── Dockerfile
├── Dockerfile.install
├── requirements.txt
├── compose.yml
├── .env.example
└── README.md
```

- `Dockerfile` – główny Dockerfile do uruchamiania aplikacji.
- `Dockerfile.install` – do tworzenia kontenera do instalacji zależności.
- `requirements.txt` – lista zależności Python.
- `compose.yml` – konfiguracja Docker Compose.
- `.env.example` – przykładowa konfiguracja portów i bazy danych.

## Instalacja zależności

### 1. Zbuduj obraz do instalacji paczek

```bash
docker build -f Dockerfile.install -t project-install .
```

### 2. Uruchom kontener z montowaniem katalogu projektu

#### Linux

```bash
docker run -it --mount type=bind,source="$(pwd)",target=/app project-install
```

#### Windows (PowerShell / CMD)

```powershell
docker run -it --mount type=bind,source="${PWD}",target=/app project-install
```

### 3. W kontenerze

1. Utwórz i aktywuj środowisko wirtualne:

```bash
python -m venv venv
source venv/bin/activate
```

2. Zainstaluj paczki, np.:

```bash
pip psycopg2-binary ...
```

3. Zapisz je do `requirements.txt`:

```bash id="pip-freeze"
pip freeze > requirements.txt
```

4. Wyjdź z kontenera:

```bash id="exit-container"
exit
```

> Nie commituj katalogu `venv` – usuń go po wygenerowaniu `requirements.txt`.

---

## Uruchamianie aplikacji

1. Zmień nazwę z `.env.example` na `.env` i dostosuj zmienne jeżeli to konieczne
2. Zbuduj i uruchom kontenery:

```bash
docker compose up --build
```

3. Aplikacja FastAPI będzie dostępna pod:

```text
http://localhost:8000
http://localhost:8000/docs
```
