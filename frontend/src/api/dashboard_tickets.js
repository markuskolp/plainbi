
export const dashboard_tickets  = 
{
  dashboardName: "Tickets",
  id: 1,
  alias: "tickets",
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
                "member": "Veranstaltung.veranstaltungName",
                "operator": "equals",
                "values": [
                  "EXPO REAL 2023"
                ]
              }
            ]
          },
          chartType:"number"
        },
        name: "Onlinebestellungen",
        id: 10,
        layout: {x:0,y:0,w:4,h:4}
    },
    {
      vizState: {
        query:{
          "order": {
            "Veranstaltung.veranstaltungBeginnDt": "asc"
          },
          "filters": [
            {
              "member": "Veranstaltung.veranstaltungName",
              "operator": "equals",
              "values": [
                "EXPO REAL 2023"
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
      layout: {x:0,y:4,w:4,h:4}
  },
    {
        vizState: {
          query:{
            "filters": [
              {
                "member": "Veranstaltung.veranstaltungName",
                "operator": "equals",
                "values": [
                  "EXPO REAL 2023"
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
        layout: {x:5,y:0,w:20,h:8}
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
                "member": "Veranstaltung.veranstaltungName",
                "operator": "equals",
                "values": [
                  "EXPO REAL 2023"
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
        name: "Länderranking",
        id: 15,
        layout: {x:0,y:8,w:12,h:8}
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
                "member": "Veranstaltung.veranstaltungName",
                "operator": "equals",
                "values": [
                  "EXPO REAL 2023"
                ]
              }
            ],
            "dimensions": [
              "Land.land"
            ],
            "timeDimensions": []
          },
          chartType:"table"
        },
        name: "Länderranking",
        id: 16,
        layout: {x:12,y:8,w:12,h:8}
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
            "filters": [
              {
                "member": "Veranstaltung.veranstaltungName",
                "operator": "equals",
                "values": [
                  "EXPO REAL 2023"
                ]
              }
            ],
            "dimensions": [
              "Produkt.vaProduktName",
              "Produkt.vaProduktCode",
              "Vertriebskanal.vertriebskanalName"
            ],
            "order": {
              "Ticket.anzahlTickets": "desc"
            }
          },
          pivotConfig: {
            "x": [
              "Produkt.vaProduktName",
              "Produkt.vaProduktCode"
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
        layout: {x:0,y:16,w:24,h:8}
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
                "member": "Veranstaltung.veranstaltungName",
                "operator": "equals",
                "values": [
                  "EXPO REAL 2023"
                ]
              }
            ],
            "dimensions": [
              "Land.land"
            ],
            "timeDimensions": []
          },
          chartType:"map"
        },
        name: "Länderranking",
        id: 20,
        layout: {x:0,y:24,w:24,h:12}
    }
  ]
}

;
