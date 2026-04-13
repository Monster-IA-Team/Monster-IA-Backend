# Monster IA

Aplikacja ...

---

## Struktura projektu

```
./
├── app/
│   └── pliki aplikacji
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

Zależności nalezy dodawać do pliku `requirements.txt`. Podczas budowy kontenera będą one się samodzielnie instalować.

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

## Przydatne adresy

| Usługa        | Adres                      |
| ------------- | -------------------------- |
| Swagger       | http://localhost:8000/docs |
| Głowny adress | http://localhost:8000      |
