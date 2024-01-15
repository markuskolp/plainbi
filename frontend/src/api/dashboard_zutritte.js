
export const dashboard_zutritte  = 
{
  dashboardName: "Zutritte",
  id: 2,
  alias: "zutritte",
  data_status: {
    //title: "Datenstand",
    vizState: {
      query:{
        "measures": ["Zutritte.aktuellsteDaten"],
        //"order": {"Ticket.registrierungDt": "asc"},
        /*"filters": [
          {
            "member": "Veranstaltung.veranstaltungNr",
            "operator": "equals",
            "values": [
              "4542023"
            ]
          }
        ],*/
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
            "measures": [
              "Zutritte.anzahlTEE"
            ],
            "order": {},
            "segments": [
              "Zutritte.fkmRelevant"
            ],
            "timeDimensions": []
          },
          chartType:"number"
        },
        name: "TEE (gesamt)",
        id: 10,
        layout: {x:0,y:0,w:4,h:3}
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
          "measures": [
            "Zutritte.anzahlTEE"
          ],
          "segments": [
            "Zutritte.fkmRelevant",
            "Zutritte.heute"
          ]
        },
        chartType:"number"
      },
      name: "TEE (heute)",
      id: 11,
      layout: {x:0,y:0,w:4,h:3}
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
        "measures": [
          "Zutritte.anzahlTEE"
        ],
        "segments": [
          "Zutritte.fkmRelevant"
        ],
        "timeDimensions": [
          {
            "dimension": "Zutritte.ereignisDatum",
            "granularity": "day"
          }
        ]
      },
      chartType:"bar"
    },
    name: "je Tag",
    id: 12,
    layout: {x:4,y:0,w:6,h:6}
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
        "measures": [
          "Zutritte.anzahlTEE"
        ],
        "segments": [
          "Zutritte.fkmRelevant"
        ],
        "timeDimensions": [
          {
            "dimension": "Zutritte.ereignisZeitstempel",
            "granularity": "hour"
          }
        ]
      },
      chartType:"bar"
    },
    name: "je Tag und Stunde",
    id: 13,
    layout: {x:10,y:0,w:14,h:6}
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
          "measures": [
            "Zutritte.anzahlTEE"
          ],
          "order": {
            "Zutritte.anzahlTEE": "desc"
          },
          "segments": [
            "Zutritte.fkmRelevant"
          ],
          "dimensions": [
            "Eingang.eingangstorGruppe"
          ]
        },
        chartType:"table"
      },
      name: "Eingänge",
      id: 18,
      layout: {x:0,y:6,w:6,h:8}
  },
    {
        vizState: {
          query:{
            "limit": 10,
            "segments": [
              "Zutritte.fkmRelevant"
            ],
            "measures": [
              "Zutritte.anzahlTEE"
            ],
            "order": {
              "Zutritte.anzahlTEE": "desc"
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
        layout: {x:6,y:6,w:10,h:8}
    },
    {
        vizState: {
          query:{
            "limit": 5000,
            "segments": [
              "Zutritte.fkmRelevant"
            ],
            "measures": [
              "Zutritte.anzahlTEE"
            ],
            "order": {
              "Zutritte.anzahlTEE": "desc"
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
    },
  ]
}

;
