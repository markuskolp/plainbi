# PlainBI — Claude Code Instructions

## Git
- Aktiver Arbeits-Branch: `main` (refactor/frontend-api-layer ist bereits gemerged)
- **Nie `git commit` ausführen** — der Nutzer committed immer selbst
- Kein `git push` ohne explizite Aufforderung
- Feature-Branches für größere Themen existieren remote (z.B. `lookup-serverside`, `column_filter`, `adhoc_fixes`, `backend_fastapi`) — vor Arbeit an einem Thema prüfen, ob es dort bereits (unfertigen) Code gibt

## Projektstruktur
```
plainbi/
├── BACKLOG.md               # Themen-/Feature-Backlog (Backend + Frontend + Bugs)
├── REFACTOR.md               # Notizen zu Code-Qualität/Architektur-Schwächen
├── backend/
│   ├── backend_doku.md       # Kurzreferenz, verweist auf README.md/endpoints.md
│   ├── endpoints.md          # Vollständige REST-Endpoint-Referenz
│   └── plainbi_backend/
│       ├── api.py            # REST-Endpoints (~3.900 Zeilen, Flask, mit Flasgger/Swagger-Docstrings)
│       └── db.py             # DB-Abstraktionsschicht (~1.970 Zeilen)
└── frontend/
    └── src/
        ├── components/
        │   ├── CRUDPage.js            # Kern-Render-Engine (Tabellenansicht)
        │   ├── CRUDModal.js           # Edit/New/Duplicate Modal, Master/Detail-Tabs
        │   ├── CRUDDetailTab.js       # Master/Detail Tab-Inhalt
        │   ├── CRUDFormItem.js        # Alle ui-Feldtypen (Rendering)
        │   ├── CRUDToolbar.js         # Suche + Buttons
        │   ├── CRUDCalendar.js        # Kalender-View
        │   ├── ColumnSettingsDrawer.js # Spalten Ein-/Ausblenden + Reihenfolge
        │   ├── ColumnFilterDropdown.js # Spaltenfilter (Distinct-Values + Suche)
        │   ├── CodeMirrorEditor.js    # SQL/JSON-Editor (ersetzt Monaco)
        │   ├── SelectLookup.js        # Lookup-Dropdown, server-seitige Suche
        │   ├── Table.js               # Ant-Design-Table-Wrapper
        │   └── CRUDApp.js             # App-Rendering, löst detail_pages-Aliases auf
        ├── hooks/
        │   └── useApiState.js         # Loading/Error-State Hook
        ├── utils/
        │   ├── apiClient.js           # Zentraler Axios-Client mit Auth-Interceptor
        │   ├── pkUtils.js             # PK/URL-Hilfsfunktionen
        │   ├── dataUtils.js           # extractResponseData, sortByName, isTrue()
        │   └── sorter.js
        └── pages/
            ├── Login.js, LoginSSO.js, ThemeLayout.js
            ├── Home.js, Apps.js, AppRuntime.js, AdhocRuntime.js
            ├── Settings.js, UserProfile.js, NoPage.js
            └── ...
```

Feature-/Konfigurationsdokumentation (CRUD-App-JSON-Spec, Adhoc-Queries, Lookups, Env-Vars) steht in `README.md` — hier stehen nur interne Arbeitskonventionen.

## Frontend-Konventionen
- **API-Aufrufe immer über `apiClient`** (nicht Axios direkt) — Auth-Header und 401-Handling sind dort zentralisiert
- **`useApiState`-Hook** für loading/error/errorMessage/errorDetail State
- **`setRecordData(prev => ...)`** — immer functional update, nie `setRecordData({ ...recordData, ... })`
- **`isTrue()`** (dataUtils.js) für Boolean-Felder aus der JSON-Config nutzen — erkennt `true`/`"true"` und `1`/`"1"` (DB liefert manche Flags als Integer)
- Keine `console.log` Statements
- Keine ungenutzten Imports
- Keine Kommentare außer wenn das Warum nicht offensichtlich ist

## CRUDFormItem — ui-Typen
Vollständige Liste und Bedeutung siehe README.md, Abschnitt "table_columns" → `ui`.

## CodeMirror-Editor (textarea_sql / textarea_json)
- Library: `@uiw/react-codemirror` (CodeMirror 6) — **kein Monaco mehr**, `@monaco-editor/react` wurde komplett entfernt (löste den früheren Klick-Position-Bug)
- Controlled mode über `useState` (`cmValue`/`cmFullscreenValue` in CRUDFormItem.js) statt uncontrolled `setValue()`-Aufrufen
- Vollbild-Modal (95vw) für beide Feldtypen, Wert-Sync über Ref + `useEffect`
- Font-Override in `index.css` (`.cm-editor *`) nötig wegen globalem `* { font-family: Inter !important }`; Selection-Highlighting über `.cm-selectionBackground` (Multi-Line) + `::selection` (Inline)

## Tabellen-State (CRUDPage)
- Spaltenauswahl/-reihenfolge/-breite, Filter und Sortierung werden pro Page in `localStorage` persistiert
- Key-Schema: `plainbi_state_<pathname>/<tableName>` (Filter/Sort) und `plainbi_cols_<pathname>/<tableName>` (Spalten) — `tableName` im Key verhindert Konflikte, wenn mehrere `CRUDPage`-Instanzen auf einer Seite laufen (z.B. Settings)
- "Zurücksetzen"-Button erscheint nur wenn der State vom Default abweicht (`isDirty`-Check)

## callRestAPI / callStoredProcedure
- In CRUDPage.js und CRUDModal.js vorhanden (siehe README.md "external_actions" für die JSON-Config)
- `apiClient.post(url, body, { headers: { 'Content-Type': 'application/json;charset=utf-8', 'Access-Control-Allow-Origin': '*' } })`
- Content-Type Header muss explizit gesetzt werden (Axios setzt bei String-Body sonst text/plain)

## Backend (api.py)
- Vollständige Endpoint-Referenz: `backend/endpoints.md`; Konfiguration/Env-Vars: `README.md`
- `/api/exec/<db>/<procname>` — führt gespeicherte Prozedur aus, Body kann leer sein (→ `{}`, keine Parameter), nur MS SQL Server unterstützt, Parameterwerte werden als Strings in SQL eingebettet (bei String-Werten Quotes im Body selbst setzen)
- Jeder Request-Handler hat einen Flasgger/Swagger-Docstring (`---` gefolgt von YAML) — beim Ändern eines Endpoints diesen mitpflegen
- `@audited`-Decorator loggt Status/Dauer/Fehlermeldung nach `plainbi_audit` — bei neuen Endpoints mit übernehmen, sofern sinnvoll
