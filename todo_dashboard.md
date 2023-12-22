#-----------------------------------------------------------------------------------------------------
# Prio 1
#-----------------------------------------------------------------------------------------------------

Darstellungen
	- "Verlauf nach VA-Tagen": pivotConfig (z.B. wg. Tage vor VA-Ende)
	- die drei Pünktchen beim Card gehen nicht mehr ?!

Modellierung
	- Cube.js Modell umstellen auf "Neu-DWH"
	- auch kumuliert hinbekommen
	- evtl. Cube Core auf neueste Version umstellen

Filter:
	- Auswahl von Veranstaltungsfilter in die Queries übernehmen !
	- Select beladen aus Cube.js (VA-Liste, nur wo es Ticketzahlen (Onlinebestellungen) gibt)
	- Default setzen beim Einstieg

Darstellungen ergänzen:
	- Datenstand von Cube.js bekommen
	- "Tage vor VA-Ende"
	- dann Kartenkomponente ergänzen
		- starten mit React-Leaflet und Länder GeoJSON -> CartoDB.PositronNoLabels
		- ISO-Code oder Name verwenden zum Mappen mit GeoJSON
		- Zahl darstellen und evtl. auch Ländername bei Mouseover
		- evtl. Einfärben nach Abstufungen
		- nicht gematchte Einträge anzeigen
		- +/- Zoom
		- Startpunkt der Karte angeben (z.B. DE)
		- evtl. auch Heatmap

Abrunden Version 1:
	- Dashboard "Tickets" fertigmachen, dann "Zutritte" (erstmal Definition fest hinterlegen)
	- über "id" oder "alias" aufrufbar machen ../dashboard/1, ../dashboard/2 


#-----------------------------------------------------------------------------------------------------
# Prio 2
#-----------------------------------------------------------------------------------------------------

- Fullscreen umsetzen
- "Refresh" umsetzen
- Switch einbauen (z.B. von kumuliert zu nicht kumuliert)
- Styling komplett und Objekte als Komponenten abstrahieren
	Header, Filterbereich, Dashboard, Dashboarditems, ChartRenderer
- Styling von Charts
	- vertical bar chart !
	- die blaue Farbe der Messe nehmen
- Styling von Tables
	- Kennzahlspalten rechtsbündig (Titel und Zahlen)
	- Scrollbar nur zeigen wenn notwendig
	- Scrollbar optisch anders
	- Spaltentitel sollten immer passen und nicht umbrechen
- "Drill zu Daten" probieren: https://cube.dev/blog/introducing-a-drill-down-table-api-in-cubejs
- PDF Export von Dashboard (clientseitig)
- "Reduzieren", d.h. vieles nur zeigen bei Hover (z.B. die 3 Pünktchen, das kleine Symbol rechts unten in den Cards, die Symbole auf Dashboardebene (Fullscreen, ...)



#-----------------------------------------------------------------------------------------------------
# Prio 3
#-----------------------------------------------------------------------------------------------------

- Table
	- analog wie bei CRUDPage.js mit Sortierung
	- Pagination angebbar
	- Gesamtsumme ein/ausschaltbar
- dann Tabs erlauben
- "Explore" einführen
- auch "Generiertes SQL" und "JSON Query" von Cube anzeigen
- auch "Definition" vom Explore anzeigen (JSON mit Name, Viz-Definition, ...)
- Speichern in plainbi Repo, auch dann Auflisten z.B. unter ".../dashboards" zum Öffnen oder Löschen
- Dashboard "Editiermodus" - sobald man was verändert, dann Speichern Button zeigen <oder> erzwingen das man vorher den "Editiermodus" einschaltet
- Filter auf Ebene "Dashboard" + "Tabs" erlauben
	- hier diverse Filter wie Mehrfachauswahl, Datumsauswahl (auch mit relativen Zeiträumen), etc.

#-----------------------------------------------------------------------------------------------------
# Prio 4
#-----------------------------------------------------------------------------------------------------

- Umstellen auf Vega-Charts und ein paar Diagrammtemplates vordefinieren
- "Optionen" einführen im "Explore"

#-----------------------------------------------------------------------------------------------------
# Backlog
#-----------------------------------------------------------------------------------------------------

- Dashboardwidget für "Markdown"
- Drillthrough von einem Dashboard zu einem anderen Dashboard
- Pivot Tabelle beginnen
- bedingte Formatierung in Tabellen
- Zahlen und Balken in Tabellen
- Formatierung bei Delta Spalten (z.B. grün/rot Hinweis oder Pfeiler oder ...)
- Vergleich bei BigNumber erlauben
- Tooltip bei Diagrammen konfigurieren
- PoP (Period over Period) comparison
- CSV/Excel Export bei Tabellen
- PDF Export von Dashboard (serverseitig generieren)
- Crossdrill (temporäre übergreifende Filter) -> z.B. Artikel auswählen
- Cube Datenmodell im Web editieren in plainbi
- Berechtigungen umsetzen (zuerst auf Cube/View Ebene (Datensätze), dann auf Spalten, dann auf Zeilen)


pivotConfig:
{
  "x": [
    "Tickets.dayBeforeEnd"
  ],
  "y": [
    "measures"
  ],
  "fillMissingDates": true,
  "joinDateRange": false
}


  pivotConfig: {
  "x": [
    "Artikel.articleNameDe",
    "Artikel.articleNumber"
  ],
  "y": [
    "Artikel.ticketCategoryDe",
    "measures"
  ],
  "fillMissingDates": true,
  "joinDateRange": false
}