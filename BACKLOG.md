# plainbi backlog

## Backend


Weiterentwicklung:

- **Audit erweitern mit Status, d.h. ob Aufruf erfolgreich war oder nicht - gerade bei Adhocs**
- Tausendertrennzeichen in Adhoc Excelexport (5.321 anstatt 5321) - NK-Stellen so belassen (aber evtl. geht vorformatieren auf 2 NK-Stellen, aber nur wenn es ein Float/Decimal ist ?)
- Backend Logging prüfen (Passwörter, etc.) und reduzieren (Daten von Resultset, etc.) bzw. aussagekräftiger
- Unique constraints  sind im repo create script drinnen, aber am linux noch nicht aktiv
- ~~Adhoc Export Excel -> Infoseite in Arial 9 ;-)~~
- Dokumentation in Github schreiben zu Endpunkten, Konfigdateien, Install, Docker, etc.
- plainbi_datasource: db_type enthält jdbc-url inkl. pw's !
- ~~ohne Gruppenzuordnung ausgeben bei Admin's, damit sie alle Inhalte auf der Homepage sehen (falls diese keiner Gruppe zugeordnet sind) .> als gid "nogroup" verwenden~~
- ~~"usercol" als Parameter übergeben, damit Backend weiß, dass es beim insert/update den Username hier mitgeben soll (notwendig für vv-Trigger Logik)~~
- ~~URL-Parameter "cols", damit man beim Holen von Daten nur die Spalten verwendet werden die man auch anzeigt / ebenso bei der Suche beachten~~


## Frontend

Weiterentwicklung:

- defaultOrderBy verbessern - evtl. doch bei getColumn() nur über "defaultSortOrder" und weiter unten über "multiple" gehen um die Reihenfolge anzugeben bei mehreren Spalten
- **Adhoc Tool ausbauen z.B. mit Cube JS zu einem SFO ähnlichen Berichtserstellungstool (Listenansicht)**
- **Gruppe auf Startseite nur zeigen, wenn es Inhalte gibt**
~~- Fehler beim Löschen z.B. von Adhoc besser anzeigen (wenn z.B. noch Berechtigung existiert und fk-constraint zuschlägt)~~
- Sicht speichern übergreifend (nur Admin) oder je User (dabei Sortierung sowie Filter merken)
- Zurückbutton: durch den neuen Home-Button lass ich den Zurückbutton evtl. komplett verschwinden.
- Anzahl Datensätze pro Tabelle nicht überall einstellbar, warum ?

- Rechtekonzept:
  - z.B. auf TEST/PROD nicht erlauben, dass man Applikationen und Lookups anlegen kann
  - unterscheiden in Lese/Schreibrechte bei Applikationen
  - auch auf "Page" Ebene Lese/Schreibrechte vergeben

- Ressource "page" und "page_attachment" hinzufügen, damit man per Markdown eine Doku pflegen kann (Seiten oder News/Blogeintrag)
- User auch vorab anlegen -> am besten über ein Button wo man aus dem AD auch die auslesen kann (falls AD in .env hinterlegt ist)
-  **ohne Gruppenzuordnung** ausgeben bei Admin's, damit sie alle Inhalte auf der Homepage sehen (falls diese keiner Gruppe zugeordnet sind)
  - Endpoint /group/<gid>/resources -> hier kann man für <gid> auch **nogroup** schreiben, dann kommen alle Ressourcen die keiner Gruppe zugeordnet sind (Admins only)
- insert/update plainbi - nur felder liefern die verändert wurden (bisher wird immer der gesamte Record geliefert im PUT/POST Body)
- 1 bis n vordefinierte Filter für ganze Seite (z.B. nicht konfigurierte Mappings, etc.) und entscheiden ob einer der **Filter beim Einstieg (je Seite)** auch sofort ziehen soll
- **App Spezifikation validieren**
- plainbi_static_files: base64 UI Element besser machen (siehe todos in CRUDFormItem.js)
- datasource bei Pages rausnehmen in Init-Skripten + MM DEV/TEST/PROD (Applikations-Spezifikationen durchsuchen)
- bei Settings eine Übersicht machen von User<>Gruppe<>Ressource -> damit man das mal in 1 Überblick hat -> später mit Subpage auch immer von Entität ausgehend die Zuordnung/Übersicht erlauben (z.B. User -> zugeordnete Gruppen -> zugeordnete Ressourcen | Gruppe -> zugeordnete User -> zugeordnete Ressourcen) -> damit man das von jeder Richtung pflegen könnte
- Homepage: Suchfeld 
- evtl. auch Applikationsübergreifender Filter (z.B. Veranstaltung auswählen)
- Infobutton auf Seitenebene oder was zum auf- und zuklappen mit Text
- Identity Spalten bei PK ermöglichen
- **Tabellenspaltenbreite nicht optimal (Header abgeschnitten, etc.)**
- **Datensatz per URL aufrufen** (d.h. gleich im Editiermodus / Modal)
	- offen: auch für composite key ermöglichen !
- Code komplett überarbeiten, formatieren, schöner schreiben, etc.
- Webapplikation auf Security challengen
  - Anforderungen von OWASP für NODE.JS umgesetzt werden (siehe Nodejs Security - OWASP Cheat Sheet Series  sowie Best Practices Top 10 Node.js Security Best Practices for 2023 - Risks & Prevention | Snyk) .
- environment_color_banner wird noch nicht verwendet
- Bilder hochladen (als BLOB speichern) und anzeigen (bisher sonst nur base64 möglich) - evtl. auch Angabe eines Pfads zur Bilddatei (http...) mit Anzeigefunktion

- Edit only if in certain user or group (otherwise read only or hidden)
- Grid edit
- Tree view (mit Editiermöglichkeit / Iconauswahl)
- Conditional row formatting (e.g. background color for the row)

- Cascading prompts: also having a label dependent on a selected/entered value (e.g. ID of a address -> show the full address for this)
- Input search box (Lookup) with onSearch loading from server: https://ant.design/components/input#input-demo-search-input-loading


Bugs:

- Timeout bei external action je ID unterscheiden !


  const [externalActionTimeout, setExternalActionTimeout]=useState([]);
  
      let existingTimeoutObject = externalActionTimeout.find((ext) => ext.id === id);
      let existingTimeoutObjectHasTimeout = false;
      try { existingTimeoutObjectHasTimeout = existingTimeoutObject.timeout ? true : false; } catch(err) {}
      console.log("exists ? " + existingTimeoutObjectHasTimeout)
      if(existingTimeoutObjectHasTimeout) {

 setExternalActionTimeout( 
          externalActionTimeout.map(ext =>
            ext.id === id ? { ...ext, 
              id: id,
              timeout: setTimeout(() => {
                console.log("timeout over")
                setExternalActionTimeout(null)
                clearTimeout(this)
              }, wait_repeat_in_ms)
            } : ext
          )
        );

- wenn AdHocs (erwarteterweise) keine Daten liefern, gibt es bei Ausgabe als Excel oder CSV einen Fehler , aber HTML funktioniert
- wenn der Name des AdHocs zu lange ist, wirft das Portal keinen Fehler, sondern sagt, es wurde erfolgreich gespeichert - es gibt aber keinen neuen Adhoc in der Liste
- Sortierung aus Tabelle/View wird nicht übernommen ? (gerade bei View mit "order by offset 0 rows")
- Seitenfilter und dann im Suchfeld suchen -> Seitenfilter wird aufgehoben z.B. https://dwh.mmgmuc.de/apps/dwh_testsuite/testlauf?test_lauf_id=202
- applikations-spec: ignoriere groß/klein bei spaltennamen, pk, ...
- wenn man User löscht und dieser zu einer Gruppe gehört, dann wird "erfolgreich" gezeigt (obwohl dieser nicht gelöscht wurde) - es sollte der Fehler gezeigt werden
- **Filter und Pagination: wenn man auf Seite 2 ist und weitersucht kommt kein Ergebnis -> immer auf Page 1 zurückspringen !**
- **abgelaufene Session/Token**: in Settings-Bereich auch auf abgelaufenes Token achten -> ruft aber CRUDPage auf ?!
- TileVA.js -> Image verzieht sich wenn die Bildschirmbreite zu klein wird -> div und img element - das img übernimmt die Höhe, wenn man diese entfernt geht es -> aber wie lösen?
