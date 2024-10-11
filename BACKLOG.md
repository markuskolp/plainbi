# plainbi backlog

## Backend

- Backend Logging prüfen (Passwörter, etc.) und reduzieren (Daten von Resultset, etc.) bzw. aussagekräftiger
- plainbi_user 
	- ~~Passwortfeld: NULL reinschreiben anstatt X beim gehashten Passwortfeld bei lokalen Usern~~
	- ~~mit NULL (leerem Passwort) darf man sich aber nicht anmelden können~~
- plainbi_datasource
	- db_type enthält jdbc-url inkl. PWs !
- ~~Login~~
	- ~~E-mail Adresse auch erlauben anstatt Usernamen und damit gegen AD prüfen~~
- Adhocs
	- default Sortierungsfeld bei Adhoc – geht das überhaupt? bei CSV/Excel kommt auf jeden Fall ein Fehler
- ~~E-Mail auslösen z.B. beim Speichern („Berichtsempfänger“)~~
	~~z.B. ein Email Endpoint (an/cc/bcc, subject, body)~~
- **bei „Neu“ in TV-Tabelle, kein Überschreiben eines Datensatzes erlauben**
~~- plainbi_audit_adhoc View ergänzen um "username"git~~ 
- Unique constraints  sind im repo create script drinnen, aber am linux noch nicht aktiv
- Adhoc Export Excel -> Infoseite in Arial 9 ;-)
- Dokumentation in Github schreiben zu Endpunkten, Konfigdateien, Install, Docker, etc.
- ~~Swagger~~
- ~~Datenbankprozedur auslösen über Frontend (z.B. um eine komplexere Verarbeitung anzustossen)~~
- **SSO (Single Sign On) ermöglichen**
	- https://www.youtube.com/watch?v=oW1SJxGiaZA
	- https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-web-app-python-flask?tabs=windows 
	- https://learn.microsoft.com/de-de/entra/external-id/customers/sample-web-app-python-flask-sign-in?tabs=windows
- eindeutige Spaltenwerte einer Tabelle (damit man diese als Spaltenfilter anzeigen könnte)
	/api/distinctvalues/{db}/{tab}/{col}
- ~~TV-Version wird geschlossen  bei Fehlern , aber sollte bleiben~~
	~~Wir haben auch ein Fall, dass beim Editieren ein Fehler auftritt z.B. weil ein NOT NULL Feld nicht gefüllt wurde.~~
	~~Das passt grundsätzlich, aber die TV-Version hängt dann „in der Luft“.~~
	~~Vermutlich weil du zuerst das Update auf die TV machst und das invalid setzt.~~
	~~Danach dann das Insert, welches dann fehlschlägt.~~
	~~Kann das irgendwie in 1 Transaktion erfolgen ?~~
	~~Oder umgedreht ?~~


## Frontend

asap

~~- Problem bei Mapping App (Geschlecht): Uncaught InvalidCharacterError: Failed to execute 'btoa' on 'Window': The string to be encoded contains characters outside of the Latin1 range.    at te (CRUDPage.js:252:16)~~
~~- Problem mit Lookup bei Anlage von Lookups (datasource_id wird nicht gefüllt) oder bei Adhoc (Anforderer Lookup geht nicht)~~
- **default sort order** bei Adhoc geht nicht - führt zu einem Fehler (siehe auch oben bei Backend)
- wenn man direkt auf ein Adhoc per URL geht und die Session abgelaufen ist, kommt nur ein Adhocfehler -> er sollte eigentlich auf die Loginseite springen mit Fehlerhinweis "Session abgelaufen"

~~- Globale Einstellungen/Logos noch nicht ausgerollt bei MM -> build und deploy?~~
- plainbi_static_files: base64 UI Element besser machen (siehe todos in CRUDFormItem.js)
- datasource bei Pages rausnehmen in Init-Skripten + MM DEV/TEST/PROD (Applikations-Spezifikationen durchsuchen)
~~- bei Adhoc App ist die Pagination auf DEV ganz weit unten ?~~
~~- mal bei diesen Apps auch die Sortierung/Filterung umstellen auf Bezeichnung anstatt auf ID !~~
- **für UIs mit Typ JSON, SQL, ... den MonacoEditor verwenden**
- **bessere Fehlermeldungen** -> warum wird z.B. bei Adhoc nicht die Meldung ausgegeben oder beim Speichern eines bestehenden Eintrags (z.B. User/Gruppenzuordnung) wie beim lokalen Entwickeln -> bei CRUD Operationen sehe ich auch keine Fehlerinhalte in error.response... (kommt da noch nichts vom Backend oder geht es nicht ?)
~~- Oben ein Homebutton einfügen, damit man immer zurück kommt~~
- bei Settings eine Übersicht machen von User<>Gruppe<>Ressource -> damit man das mal in 1 Überblick hat -> später mit Subpage auch immer von Entität ausgehend die Zuordnung/Übersicht erlauben (z.B. User -> zugeordnete Gruppen -> zugeordnete Ressourcen | Gruppe -> zugeordnete User -> zugeordnete Ressourcen) -> damit man das von jeder Richtung pflegen könnte
- Homepage
	- Suchfeld fehlt
- **Filter in Spaltentitel (Backend ist bereits erweitert dafür)**
	- Endpunkt notwendig: /api/distinctvalues/{db}/{tab}/{col}
- 1 bis n vordefinierte Filter für ganze Seite (z.B. nicht konfigurierte Mappings, etc.) und entscheiden ob einer der Filter beim Einstieg auch sofort ziehen soll
- **Subpage (Master-Detail)**
- evtl. auch Applikationsübergreifender Filter (z.B. Veranstaltung auswählen)
- Infobutton auf Seitenebene oder was zum auf- und zuklappen mit Text
- Edit-Page
	- **defaultValue** ermöglichen (z.B. bei Berichtsversand OnBe)
	- Validierung einbauen
	- wenn man neben Modal klickt dann nur Schliessen, wenn noch nichts geändert wurde ! (auch bei Abbrechen Button nachfragen ob man wirklich Abbrechen will)
	- Zahleneingabe mit NK-Stellen - aktuell . statt , (englisch)
~~- Sequence in plainbi Frontend ermöglichen~~
- Identity Spalten bei PK ermöglichen
- Parameter bei Adhocs implementieren
- Adhoc Serverside Pagination nutzen
- **Tabellenspaltenbreite nicht optimal (Header abgeschnitten, etc.)**
~~- PK mit Sonderzeichen ermöglichen~~
~~- HTML Anzeige in Tabelle/Liste ermöglichen z.B. für Links etc. -> "ui":"html"~~
~~- Datum formatieren in Anzeige (date: YYYY-MM-DD, datetime: YYYY-MM-DD HH:mm:ss), auch Sortierung soll dann gehen (Backend muss evtl. auch den Wert so liefern !)~~
~~- Seite per URL aufrufbar machen (bisher geht nur App) -> /apps/<app_alias>/<page_alias~~
~~- Seite filterbar machen per URL-Parameter /apps/<app_alias>/<page_alias>?<column_name>=<filter_value>&<column_name>=<filter_value>...**~~
    ~~show_breadcrumb":"true", "parent_page": {"alias":"testlaeufe","name":"Testläufe"},~~
~~- page.hide_in_navigation~~

- Default Sortierung für Pages (z.B. absteigend nach Feld x)

- Datensatz per URL aufrufen (d.h. gleich im Editiermodus / Modal) -> bisher nur Seitenfilterung per URL

- Code komplett überarbeiten, formatieren, schöner schreiben, etc.

- Webapplikation auf Security challengen
  - Anforderungen von OWASP für NODE.JS umgesetzt werden (siehe Nodejs Security - OWASP Cheat Sheet Series  sowie Best Practices Top 10 Node.js Security Best Practices for 2023 - Risks & Prevention | Snyk) .

- TileVA.js -> Image verzieht sich wenn die Bildschirmbreite zu klein wird -> div und img element - das img übernimmt die Höhe, wenn man diese entfernt geht es -> aber wie lösen?

Bugfixing:
~~- Filter bei Settings, Adhoc App, Ressourcen App geht nur auf ID anstatt auf Namen !~~
- **Filter und Pagination: wenn man auf Seite 2 ist und weitersucht kommt kein Ergebnis -> immer auf Page 1 zurückspringen !**
- environment_color_banner wird noch nicht verwendet


Dokumentation schreiben/aktualisieren in Github
-  zu Applikationen
