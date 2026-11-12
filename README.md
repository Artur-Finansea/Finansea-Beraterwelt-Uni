# Finansea-Beraterwelt-Uni

Die Finansea-Beraterwelt ist ein kleines Dashboard mit einem React-/Bootstrap-Frontend und einem Python-Flask-Backend. Das Frontend ruft den Backend-Status über `/api/status` ab. Die lokalen Anwendungsdaten werden mit SQLite und Flask-SQLAlchemy verwaltet.

## Voraussetzungen

- Python 3 mit `pip`
- Node.js mit `npm`

## Backend starten

Im Projektverzeichnis:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app init-db
python app.py
```

Der Befehl `init-db` legt fehlende Tabellen an, ohne vorhandene Daten zu löschen. Die lokale Datenbank wird unter `backend/instance/finansea.db` gespeichert und durch `.gitignore` von Git ausgeschlossen. Das Backend läuft anschließend standardmäßig unter `http://127.0.0.1:5000` und startet ohne Debug-Modus.

Die Datenbank kann aus dem Projektstamm auch direkt mit der vorhandenen virtuellen Umgebung initialisiert werden:

```powershell
.\backend\.venv\Scripts\python.exe -m flask --app backend.app init-db
```

Für die lokale Entwicklung kann der Debug-Modus ausdrücklich aktiviert werden:

```powershell
$env:FLASK_DEBUG = "1"
python app.py
```

Nach der Entwicklung kann die Variable mit `Remove-Item Env:FLASK_DEBUG` wieder entfernt werden.

## Frontend starten

In einem zweiten Terminal im Projektverzeichnis:

```powershell
cd frontend
npm install
npm run dev
```

Die von Vite angezeigte Adresse im Browser öffnen. Während der lokalen Entwicklung leitet Vite Anfragen an `/api` an das Flask-Backend weiter.

## Prüfungen

Backend-Tests mit einer flüchtigen In-Memory-Datenbank und ausschließlich fiktiven Daten:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend\tests
```

Frontend-Prüfungen:

```powershell
npm run lint --prefix frontend
npm run build --prefix frontend
```
