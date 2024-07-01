# plainbi backlog

## Backend

- Backend Logging prüfen (Passwörter, etc.) und reduzieren (Daten von Resultset, etc.) bzw. aussagekräftiger
- plainbi_user 
	- Passwortfeld: NULL reinschreiben anstatt X beim gehashten Passwortfeld bei lokalen Usern
	- mit NULL (leerem Passwort) darf man sich aber nicht anmelden können
- Login
	- E-mail Adresse auch erlauben anstatt Usernamen und damit gegen AD prüfen
- Adhocs
	- default Sortierungsfeld bei Adhoc – geht das überhaupt? bei CSV/Excel kommt auf jeden Fall ein Fehler
- E-Mail auslösen z.B. beim Speichern („Berichtsempfänger“)
	z.B. ein Email Endpoint (an/cc/bcc, subject, body)
- bei „Neu“ in TV-Tabelle, kein Überschreiben eines Datensatzes erlauben
- plainbi_audit_adhoc View ergänzen um "username"
- Unique constraints  sind im repo create script drinnen, aber am linux noch nicht aktiv
- Adhoc Export Excel -> Infoseite in Arial 9 ;-)
- Dokumentation in Github schreiben zu Endpunkten, Konfigdateien, Install, Docker, etc.
- Swagger
- Datenbankprozedur auslösen über Frontend (z.B. um eine komplexere Verarbeitung anzustossen)

## Frontend

- für UIs mit Typ JSON, SQL, ... den MonacoEditor verwenden
- bessere Fehlermeldungen -> warum wir z.B. bei Adhoc nicht die Meldung ausgegeben wie beim lokalen Entwickeln
- Oben ein Homebutton einfügen, damit man immer zurück kommt
- Homepage
	- Suchfeld fehlt
	- die „berechtigten Inhalte“ weiter strukturieren können (damit es übersichtlich bleibt)
- Filter in Spaltentitel (evtl. Backend erweitern)
- 1 bis n vordefinierte Filter für ganze Seite (z.B. nicht konfigurierte Mappings, etc.) und entscheiden ob einer der Filter beim Einstieg auch sofort ziehen soll
- Subpage (Master-Detail) 
- evtl. auch Applikationsübergreifender Filter (z.B. Veranstaltung auswählen)
- Infobutton auf Seitenebene oder was zum auf- und zuklappen mit Text
- Edit-Page
	- defaultValue ermöglichen (z.B. bei Berichtsversand OnBe)
	- Validierung einbauen
	- wenn man neben Modal klickt dann nur Schliessen, wenn noch nichts geändert wurde ! (auch bei Abbrechen Button nachfragen ob man wirklich Abbrechen will)
	- Zahleneingabe mit NK-Stellen - aktuell . statt , (englisch)
- Sequence in plainbi Frontend ermöglichen -> mal testen mit vv_veranstalter (auch mal IDENTITY Spalte)
- Parameter bei Adhocs implementieren
- Adhoc Serverside Pagination nutzen

- Code komplett überarbeiten, formatieren, schöner schreiben, etc.

- Webapplikation auf Security challengen

Bugfixing:
- Filter bei Settings, Adhoc App, Ressourcen App geht nur auf ID anstatt auf Namen !
- Filter und Pagination: wenn man auf Seite 2 ist und weitersucht kommt kein Ergebnis -> immer auf Page 1 zurückspringen !
- PK mit Slash Problem
- environment_color_banner wird noch nicht verwendet

Dokumentation schreiben/aktualisieren in Github
-  zu Applikationen
