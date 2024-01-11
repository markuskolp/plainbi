TOP
- Filter in Queries anwenden

	findet "filter" der zu VA passt
	query.filters.filter(x => x.member === "Veranstaltung.veranstaltungName")
	
	position nehmen und diesen ersetzen !
	t.b.d.

=> Dashboard 1+2 fertigmachen

- Drill zu Daten
- Explore d.h. Dashboard erstellen/editieren, SQL anzeigen

=> bereit für Vorstellung im Team

=> evtl. ein Webanalytics Dashboard auch umsetzen ?

#-----------------------------------------------------------------------------------------------------
# Prio 1
#-----------------------------------------------------------------------------------------------------

Darstellungen ergänzen:
	- Datenstand von Cube.js bekommen
		- geht grundsätzlich -> aber auch Filter mitgeben ! -> Anzeige verbessern (nicht als Kachel, sondern evtl. als Teil von Dashboard-Funktionalität: d.h. Datenstand von "Datensatz" (Tickets) bekommen
	- dann Kartenkomponente ergänzen
		- als Teil von "ChartRenderer" machen auch mit Query, etc. und Geoentität - hier fix auf "country"
		- vor allem die Dimension/Kennzahl nicht mehr hartverdrahtet in Map.js !

Abrunden Version 1:
	- Dashboard "Tickets" fertigmachen
	- dann "Zutritte" (Datenmodell in Cube.js + erstmal Dashboard-Definition fest hinterlegen)
	- über "id" oder "alias" aufrufbar machen ../dashboard/1, ../dashboard/2 


#-----------------------------------------------------------------------------------------------------
# Prio 2
#-----------------------------------------------------------------------------------------------------

- "Drill zu Daten" probieren: https://cube.dev/blog/introducing-a-drill-down-table-api-in-cubejs
- PDF Export von Dashboard (erstmal clientseitig)
- "Tabs"
- "Explore" einführen
	- auch "Generiertes SQL" und "JSON Query" von Cube anzeigen
	- auch "Definition" vom Explore anzeigen (JSON mit Name, Viz-Definition, ...)
	- Speichern in plainbi Repo, auch dann Auflisten z.B. unter ".../dashboards" zum Öffnen oder Löschen
	- Dashboard "Editiermodus" - sobald man was verändert, dann Speichern Button zeigen <oder> erzwingen das man vorher den "Editiermodus" einschaltet

#-----------------------------------------------------------------------------------------------------
# Prio 3
#-----------------------------------------------------------------------------------------------------


- Interaktion (Click) in Card geht nicht z.B. die drei Pünktchen ?! -> erstmal lösen über Umschaltfläche auf "Dashboard editieren" ?

- Zahlen in Tabellen auf DE formatieren -> Spalten mit Werten erkennen und numberFormatter() einsetzen
- Fullscreen umsetzen
- "Refresh" umsetzen
- Switch einbauen (z.B. von kumuliert zu nicht kumuliert)
- Styling komplett und Objekte als Komponenten abstrahieren
	Header, Filterbereich, Dashboard, Dashboarditems, ChartRenderer
- Styling von Charts
	- die blaue Farbe der Messe nehmen
- Styling von Tables
	- Kennzahlspalten rechtsbündig (Titel und Zahlen)
	- Scrollbar nur zeigen wenn notwendig
	- Scrollbar optisch anders
	- Spaltentitel sollten immer passen und nicht umbrechen
- "Reduzieren", d.h. vieles nur zeigen bei Hover (z.B. die 3 Pünktchen, das kleine Symbol rechts unten in den Cards, die Symbole auf Dashboardebene (Fullscreen, ...)



#-----------------------------------------------------------------------------------------------------
# Prio 4
#-----------------------------------------------------------------------------------------------------

- Charts
	- stacked bar chart
	- grouped bar chart
- Table
	- analog wie bei CRUDPage.js mit Sortierung
	- Pagination angebbar
	- Gesamtsumme ein/ausschaltbar
- Filter auf Ebene "Dashboard" + "Tabs" erlauben
	- hier diverse Filter wie Mehrfachauswahl, Datumsauswahl (auch mit relativen Zeiträumen), etc.

#-----------------------------------------------------------------------------------------------------
# Prio 5
#-----------------------------------------------------------------------------------------------------

- Umstellen auf Vega-Charts und ein paar Diagrammtemplates vordefinieren
- "Optionen" einführen im "Explore"

#-----------------------------------------------------------------------------------------------------
# Backlog
#-----------------------------------------------------------------------------------------------------

- Filter:
	- Gruppierung nach Jahren options -> label options -> label value
- useQuery.js
	- eigener Wrapper anstatt useCubeQuery.js -> useEffect() kann "query" als Object nicht vergleichen - workaround über Vergleich der Attribute - verbessern !
- Karte
	- geojson von Countries nicht vollständig (ISO2)
	- geojson Daten grundsätzlich mal in eine DB laden und daraus erzeugen !
	- oder auch über cube.js holen (analog zu blogartikel)
	- auch die Mittelpunkte
	- zeigen, falls 
- Dashboardfilter: Fehler beheben, dass die Select-Liste manchmal nicht beladen wird bzw. es 3x durch die Stelle läuft
- Vertical bar chart mit Vega
	- y-achse genug Platz für Labels (siehe Länderranking)
	- was tun wenn die Anzahl zu hoch ist (z.B. 100 Länder -> Labels von y-Achse nur zum Teil zeigen ? Diagramm scrollbar machen ?)
- PDF Export von Dashboard (serverseitig generieren)
- pre-aggregates mal konfigurieren (falls es irgendwo langsam ist)
- evtl. Cube Core auf neueste Version umstellen und "running-total" davon ausprobieren
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
- Crossdrill (temporäre übergreifende Filter) -> z.B. Artikel auswählen
- Cube Datenmodell im Web editieren in plainbi
- Berechtigungen umsetzen (zuerst auf Cube/View Ebene (Datensätze), dann auf Spalten, dann auf Zeilen)

- Mapkomponente 
		- bei React-Map-GL bleiben oder doch auf Leaflet umstellen ?
		- ISO-Code oder Name verwenden zum Mappen mit GeoJSON
		- Zahl darstellen und evtl. auch Ländername bei Mouseover
		- evtl. Einfärben nach Abstufungen
		- nicht gematchte Einträge anzeigen
		- Startpunkt der Karte angeben (z.B. DE)
		- evtl. auch Heatmap
		- Zoombuttons gehen nicht weil RGL dazwischenfunkt -> kurzfristig gelöst mit draggable/resizable false bei RGL


