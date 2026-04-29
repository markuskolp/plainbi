# PlainBI — Claude Code Instructions

## Git
- Aktiver Arbeits-Branch: `refactor/frontend-api-layer`
- **Nie `git commit` ausführen** — der Nutzer committed immer selbst
- Kein `git push` ohne explizite Aufforderung
- Merge nach `main` erfolgt später, wenn das Refactoring abgeschlossen ist

## Projektstruktur
```
plainbi/
├── backend/
│   └── plainbi_backend/
│       ├── api.py          # REST-Endpoints (~3.700 Zeilen)
│       └── db.py           # DB-Abstraktionsschicht (~1.970 Zeilen)
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── CRUDPage.js         # Kern-Render-Engine
│       │   ├── CRUDModal.js        # Edit/New Modal
│       │   ├── CRUDFormItem.js     # Alle ui-Feldtypen
│       │   ├── CRUDToolbar.js      # Toolbar (extrahiert)
│       │   ├── CRUDCalendar.js     # Kalender-View (extrahiert)
│       │   └── SelectLookup.js     # Dropdown mit Lookup
│       ├── hooks/
│       │   └── useApiState.js      # Loading/Error-State Hook
│       ├── utils/
│       │   ├── apiClient.js        # Zentraler Axios-Client
│       │   ├── pkUtils.js          # PK/URL-Hilfsfunktionen
│       │   └── dataUtils.js        # extractResponseData, sortByName
│       └── pages/
│           ├── Login.js, LoginSSO.js, ThemeLayout.js
│           └── ...
└── README.md
```

## Frontend-Konventionen
- **API-Aufrufe immer über `apiClient`** (nicht Axios direkt) — Auth-Header und 401-Handling sind dort zentralisiert
- **`useApiState`-Hook** für loading/error/errorMessage/errorDetail State
- **`setRecordData(prev => ...)`** — immer functional update, nie `setRecordData({ ...recordData, ... })`
- Keine `console.log` Statements
- Keine ungenutzten Imports
- Keine Kommentare außer wenn das Warum nicht offensichtlich ist

## CRUDFormItem — ui-Typen
Alle möglichen Werte für das `ui`-Feld in der JSON-Konfiguration:
`textinput`, `email`, `numberinput`, `textarea`, `textarea_markdown`,
`textarea_sql`, `textarea_json`, `textarea_base64`,
`datepicker`, `datetimepicker`, `switch`, `label`, `hidden`,
`lookup`, `lookupn`, `password`, `password_nomem`,
`html` (nur Tabellenansicht), `modal_json_to_table` (nur Tabellenansicht)

## Monaco Editor (textarea_sql / textarea_json)
- Library: `@monaco-editor/react` (nicht react-monaco-editor)
- Uncontrolled mode: kein `value`-Prop, Initialisierung via `onMount` + `editor.setValue()`
- `isExternalUpdate`-Ref verhindert Feedback-Loop bei programmatischen `setValue()`-Aufrufen
- `useEffect([defaultValue])` synchronisiert Editor wenn Datensatz vom API geladen wird
- **Offener Bug**: Klick-Position im Modal manchmal falsch (Cursor springt in falsche Zeile)
  - `afterOpenChange` + `editor.layout()` ist bereits implementiert, hilft aber nicht vollständig
  - Nächste Schritte: `fixedOverflowWidgets: true`, Form.Item name-Prop entfernen für Monaco

## callRestAPI / callStoredProcedure
- In CRUDPage.js und CRUDModal.js vorhanden
- `apiClient.post(url, body, { headers: { 'Content-Type': 'application/json;charset=utf-8', 'Access-Control-Allow-Origin': '*' } })`
- Content-Type Header muss explizit gesetzt werden (Axios setzt bei String-Body sonst text/plain)

## Backend (api.py)
- `/api/exec/<db>/<procname>` — führt gespeicherte Prozedur aus
- Body kann leer sein → wird als `{}` behandelt (keine Parameter)
- Nur MS SQL Server unterstützt für dbexec
- Parameterwerte werden als Strings in SQL eingebettet — bei String-Werten ggf. Quotes prüfen
