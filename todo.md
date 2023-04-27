# Prio

Prio 1
- Adhoc
- CRUD

Prio 2
- versionierte Tabellen
- Security (Login/Logout) -> changed_by füllen !


## backend

- env auslagern (server, database, username, password)
- plainbi repository: sqlite -> auch versionierte tabellen?
	-> datenmodell !
- versionierung (mit parameter angeben /v) --> evtl. muster: "%tv_%"
- date/timestamp
- unit tests
- datenbankunabhängig: mssql, postgre, sqlite
- adhoc:
	- sql ausführen und daten zurückliefern als JSON
	- wenn format=XLSX, dann Excel zurückliefern
- security (login/logout) - session handling in flask - user erstmal in plainbi repository anlegen (später gegen AD/LDAP und SSO)

|adhoc|
|-|
|adhoc_id|
|adhoc_name|
|sql|
|output_format (HTML, XLSX, CSV)|

GET: /api/data/adhoc/<nr>/ -> liefert JSON
  
GET: /api/data/adhoc/<nr>/excel -> liefer Excel-Datei
