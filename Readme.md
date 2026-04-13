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

## Migracje

Obecnie na poczet developmentu została dodana do `compose.yml` taka linijka:

```docker
command: sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"
```

tworzy ona automatycznie migracje. Na faze `DEV` jest to dobre rozwiązanie. W produkcji trzeba usunąc tą linijke i robić to ręcznie przy włączonym kontenerze.

```docker
docker compose exec api alembic revision --autogenerate -m "opis zmian"
docker compose exec api alembic upgrade head
```

## Przydatne adresy

| Usługa        | Adres                      |
| ------------- | -------------------------- |
| Swagger       | http://localhost:8000/docs |
| Głowny adress | http://localhost:8000      |
