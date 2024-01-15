
export const dashboard_tickets  = 
{
  dashboardName: "Tickets",
  id: 1,
  alias: "tickets",
  data_status: {
    //title: "Datenstand",
    vizState: {
      query:{
        "measures": ["Ticket.aktuellsteDaten"],
        //"order": {"Ticket.registrierungDt": "asc"},
        "limit": 1
      },
      chartType:"data_status",
      //format: "DD.MM.YYYY HH24:MI:SS"
    }
  },
  dashboardItems: [
      {
        vizState: {
          query:{
            "limit": 5000,
            "segments": [
              "Ticket.onlineBestellungen"
            ],
            "measures": [
              "Ticket.anzahlTickets"
            ],
            "order": {
              "Ticket.registrierungDt": "asc"
            },
            "filters": [
              {
                "member": "Veranstaltung.veranstaltungNr",
                "operator": "equals",
                "values": [
                  "4542023"
                ]
              }
            ]
          },
          chartType:"number"
        },
        name: "Onlinebestellungen",
        id: 10,
        layout: {x:0,y:0,w:4,h:3}
    },
    {
      vizState: {
        query:{
          "order": {
            "Veranstaltung.veranstaltungBeginnDt": "asc"
          },
          "filters": [
            {
              "member": "Veranstaltung.veranstaltungNr",
              "operator": "equals",
              "values": [
                "4542023"
              ]
            }
          ],
          "measures": [
            "Veranstaltung.dayBeforeEndm"
          ]
        },
        chartType:"number"
      },
      name: "Tage bis VA-Ende",
      id: 11,
      layout: {x:0,y:4,w:4,h:3}
  },
    {
        vizState: {
          query:{
            "filters": [
              {
                "member": "Veranstaltung.veranstaltungNr",
                "operator": "equals",
                "values": [
                  "4542023"
                ]
              }
            ],
            "limit": 5000,
            "segments": [
              "Ticket.onlineBestellungen"
            ],
            "dimensions": [
              "Ticket.dayBeforeEnd"
            ],
            "order": [
              [
                "Ticket.dayBeforeEnd",
                "desc"
              ]
            ],
            "measures": [
              "Ticket.anzahlTicketsKumuliert"
            ]
          },
          pivotConfig:
          {
            "x": [
              "Ticket.dayBeforeEnd"
            ],
            "y": [
              "measures"
            ],
            "fillMissingDates": true,
            "joinDateRange": false
          },
          chartType:"bar"
        },
        name: "Verlauf nach Tagen vor VA-Ende",
        id: 14,
        layout: {x:5,y:0,w:20,h:6}
    },
    {
        vizState: {
          query:{
            "limit": 10,
            "segments": [
              "Ticket.onlineBestellungen"
            ],
            "measures": [
              "Ticket.anzahlTickets"
            ],
            "order": {
              "Ticket.anzahlTickets": "desc"
            },
            "filters": [
              {
                "member": "Veranstaltung.veranstaltungNr",
                "operator": "equals",
                "values": [
                  "4542023"
                ]
              }
            ],
            "dimensions": [
              "Land.land"
            ],
            "timeDimensions": []
          },
          chartType:"verticalbar"
        },
        name: "Länderranking (Top 10)",
        id: 15,
        layout: {x:8,y:6,w:8,h:8}
    },
    /*{
        vizState: {
          query:{
            "limit": 5000,
            "segments": [
              "Ticket.onlineBestellungen"
            ],
            "measures": [
              "Ticket.anzahlTickets"
            ],
            "order": {
              "Ticket.anzahlTickets": "desc"
            },
            "filters": [
              {
                "member": "Veranstaltung.veranstaltungNr",
                "operator": "equals",
                "values": [
                  "4542023"
                ]
              }
            ],
            "dimensions": [
              "Land.land"
              //,"Land.landIso2"
            ],
            "timeDimensions": []
          },
          chartType:"table"
        },
        name: "Länderranking",
        id: 16,
        layout: {x:0,y:14,w:12,h:8}
    },*/
    {
        vizState: {
          query:{
            "limit": 5000,
            "segments": [
              "Ticket.onlineBestellungen"
            ],
            "measures": [
              "Ticket.anzahlTickets"
            ],
            "filters": [
              {
                "member": "Veranstaltung.veranstaltungNr",
                "operator": "equals",
                "values": [
                  "4542023"
                ]
              }
            ],
            "dimensions": [
              "Produkt.vaProduktName",
              //"Produkt.vaProduktCode",
              "Vertriebskanal.vertriebskanalName"
            ],
            "order": {
              "Ticket.anzahlTickets": "desc"
            }
          },
          pivotConfig: {
            "x": [
              "Produkt.vaProduktName",
              //Produkt.vaProduktCode",
            ],
            "y": [
              "Vertriebskanal.vertriebskanalName",
              "measures"
            ],
            "fillMissingDates": true,
            "joinDateRange": false
          },
          chartType:"pivottable"
        },
        name: "Produktranking",
        id: 18,
        layout: {x:0,y:6,w:8,h:8}
    },
    {
        vizState: {
          query:{
            "limit": 5000,
            "segments": [
              "Ticket.onlineBestellungen"
            ],
            "measures": [
              "Ticket.anzahlTickets"
            ],
            "order": {
              "Ticket.anzahlTickets": "desc"
            },
            "filters": [
              {
                "member": "Veranstaltung.veranstaltungNr",
                "operator": "equals",
                "values": [
                  "4542023"
                ]
              }
            ],
            "dimensions": [
              "Land.land",
              "Land.landIso2"
            ],
            "timeDimensions": []
          },
          chartType:"map"
        },
        name: "Länderranking",
        id: 20,
        layout: {x:16,y:6,w:8,h:8}
    }
  ]
}

;
