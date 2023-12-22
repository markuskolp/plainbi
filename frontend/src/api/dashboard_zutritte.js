
export const dashboard_zutritte  = 
{
  dashboardName: "Zutritte",
  id: 2,
  alias: "zutritte",
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
    }
  ]
}

;
