# Monster IA

Aplikacja <KIEDYŚ SIĘ COŚ WPISZE>

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

## Pro tip dla Visual Studio Code

Jeśli VS Code nie podpowiada importów z bibliotek Pythona (np. brak autocomplete), najczęściej wynika to z braku lokalnego środowiska wirtualnego.

Najprostsze rozwiązanie to utworzenie tymczasowego `.venv`:

1. Otwórz Command Palette:

```
Ctrl + Shift + P
```

2. Wybierz:

```
Python: Create Environment
```

3. Następnie:

- wybierz `venv`
- wskaż odpowiednią wersję Pythona
- ustaw nazwę środowiska jako `.venv`

4. Na końcu wybierz instalację zależności z `requirements.txt`

Po tym VS Code powinien poprawnie:

- rozpoznawać importy
- podpowiadać kod
- wykrywać błędy

**Tip:** To środowisko jest tylko pomocnicze — aplikacja i tak działa w Dockerze, więc `.venv` nie wpływa na runtime projektu.

## Przydatne adresy

| Usługa        | Adres                       |
| ------------- | --------------------------- |
| Swagger       | http://localhost:8000/docs  |
| Głowny adress | http://localhost:8000       |
| MinIo         | http://localhost:9001/login |
