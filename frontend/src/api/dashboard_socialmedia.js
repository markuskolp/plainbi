
export const dashboard_socialmedia  = 
{
  dashboardName: "Social Media",
  id: 3,
  alias: "socialmedia",
  data_status: {
    //title: "Datenstand",
    vizState: {
      query:{
        "measures": ["SocialMedia.aktuellsteDaten"],
        "limit": 1
      },
      chartType:"data_status",
      //format: "DD.MM.YYYY HH24:MI:SS"
    }
  },
  dashboardFilters : [
    {
      columnId: "SocialMediaPlattform.socialMediaPlattformNr",
      columnLabel: "SocialMediaPlattform.socialMediaPlattform",
      displayName: "Social Media Plattform",
      defaultValue: "Linkedin",
      type: "lookup",
      query : {
        "order": [
          [
            "SocialMediaPlattform.socialMediaPlattform",
            "asc"
          ]
        ],
        "dimensions": [
          "SocialMediaPlattform.socialMediaPlattformNr",
          "SocialMediaPlattform.socialMediaPlattform"
        ],
        "filters": [
          {
            "member": "SocialMediaPlattform.socialMediaPlattform",
            "operator": "set"
          }
        ],
        "measures": [
          "SocialMedia.followerTagesstand"
        ]
        ,
        "limit": 5000
      }
    },
    {
      columnId: "Veranstaltungsreihe.veranstaltungsreiheCode",
      columnLabel: "Veranstaltungsreihe.veranstaltungsreiheName",
      displayName: "Veranstaltungsreihe",
      defaultValue: "EXPO REAL",
      type: "lookup",
      query : {
        "order": [
          [
            "Veranstaltungsreihe.veranstaltungsreiheName",
            "asc"
          ]
        ],
        "dimensions": [
          "Veranstaltungsreihe.veranstaltungsreiheName",
          "Veranstaltungsreihe.veranstaltungsreiheCode"
        ],
        "filters": [
          {
            "member": "SocialMediaPlattform.socialMediaPlattform",
            "operator": "set"
          }
        ],
        "measures": [
          "SocialMedia.followerTagesstand"
        ]
        ,
        "limit": 5000
      }
    },
    {
      columnId: "SocialMedia.datum",
      columnLabel: "SocialMedia.datum",
      defaultValue: "last_30_days",
      type: "daterange"
      //query : {} -- spaeter hier evtl. Abfrage angeben, damit nur Datümer von den Fakten/Bewegungsdaten gezeigt werden
    }
  ],
  dashboardItems: [
      {
        vizState: {
          query:{
            "order": {},
            "filters": [
              {
                "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
                "operator": "equals",
                "values": [
                  "EXR"
                ]
              }
            ],
            "measures": [
              "SocialMedia.followerAktuell"
            ],
            "timeDimensions": [
              {
                "dimension": "SocialMedia.datum"
              }
            ]
          },
          chartType:"number"
        },
        name: "Follower (aktuell)",
        id: 10,
        layout: {x:0,y:0,w:4,h:3}
    },
    {
      vizState: {
        query:{
          "order": {},
          "filters": [
            {
              "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
              "operator": "equals",
              "values": [
                "EXR"
              ]
            }
          ],
          "measures": [
            "SocialMedia.followerGewonnen"
          ],
          "timeDimensions": [
            {
              "dimension": "SocialMedia.datum"
            }
          ]
        },
        chartType:"number"
      },
      name: "Follower (gewonnen)",
      id: 20,
      layout: {x:4,y:0,w:4,h:3}
    },
    {
      vizState: {
        query:{
          "order": {},
          "filters": [
            {
              "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
              "operator": "equals",
              "values": [
                "EXR"
              ]
            }
          ],
          "measures": [
            "SocialMedia.impressionen"
          ],
          "timeDimensions": [
            {
              "dimension": "SocialMedia.datum"
            }
          ]
        },
        chartType:"number"
      },
      name: "Impressionen",
      id: 30,
      layout: {x:8,y:0,w:4,h:3}
  },
  {
    vizState: {
      query:{
        "order": {},
        "filters": [
          {
            "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
            "operator": "equals",
            "values": [
              "EXR"
            ]
          }
        ],
        "measures": [
          "SocialMedia.interaktionen"
        ],
        "timeDimensions": [
          {
            "dimension": "SocialMedia.datum"
          }
        ]
      },
      chartType:"number"
    },
    name: "Interaktionen",
    id: 40,
    layout: {x:12,y:0,w:4,h:3}
  },
  {
    vizState: {
      query:{
        "order": {},
        "filters": [
          {
            "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
            "operator": "equals",
            "values": [
              "EXR"
            ]
          }
        ],
        "measures": [
          "SocialMedia.klicks"
        ],
        "timeDimensions": [
          {
            "dimension": "SocialMedia.datum"
          }
        ]
      },
      chartType:"number"
    },
    name: "Klicks",
    id: 50,
    layout: {x:16,y:0,w:4,h:3}
  },
  {
    vizState: {
      query:{
        "order": {},
        "filters": [
          {
            "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
            "operator": "equals",
            "values": [
              "EXR"
            ]
          }
        ],
        "measures": [
          "SocialMedia.likes"
        ],
        "timeDimensions": [
          {
            "dimension": "SocialMedia.datum"
          }
        ]
      },
      chartType:"number"
    },
    name: "Likes",
    id: 60,
    layout: {x:20,y:0,w:4,h:3}
  },
  {
    vizState: {
      query:{
        "dimensions": [
          "Veranstaltungsreihe.veranstaltungsreiheLogoUrl"
        ],
        "measures": [
          "SocialMedia.followerAktuell"
        ],
        "filters": [
          {
            "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
            "operator": "equals",
            "values": [
              "EXR"
            ]
          }
        ],
        "limit": 1
      },
      chartType:"image"
    },
    //name: "Logo VR",
    id: 61,
    layout: {x:20,y:3,w:3,h:3}
  },
  {
    vizState: {
      query:{
        "dimensions": [
          "SocialMediaPlattform.socialMediaPlattformLogoURL"
        ],
        "measures": [
          "SocialMedia.followerAktuell"
        ],
        "filters": [
          {
            "member": "SocialMediaPlattform.socialMediaPlattformNr",
            "operator": "equals",
            "values": [
              "LIN"
            ]
          }
        ],
        "limit": 1
      },
      chartType:"image"
    },
    //name: "Logo Plattform",
    id: 62,
    layout: {x:20,y:5,w:2,h:2}
  },
  {
    vizState: {
      query:{
      "measures": [
        "SocialMedia.followerGewonnen"
      ],
      "timeDimensions": [
        {
          "dimension": "SocialMedia.datum",
          "granularity": "day"
        }
      ],
      "segments": [
        "SocialMedia.hatWerte"
      ],
      "filters": [
        {
          "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
          "operator": "equals",
          "values": [
            "EXR"
          ]
        }
      ],
      "dimensions": [
        "SocialMediaVertriebsweg.socialMediaVertriebsweg"
      ]
      },
      chartType:"line",
      switch: [
        {
          name: 'Kennzahl',
          type: "measure",
          defaultId: "SocialMedia.followerGewonnen",
          switchItems: [
            {
              id: "SocialMedia.followerTagesstand",
              label: "Follower"
            },{
              id: "SocialMedia.followerGewonnen",
              label: "Follower (gewonnen)"
            },
            {
              id: "SocialMedia.impressionen",
              label: "Impressionen"
            },
            {
              id: "SocialMedia.interaktionen",
              label: "Interaktionen"
            },
            {
              id: "SocialMedia.klicks",
              label: "Klicks"
            },
            {
              id: "SocialMedia.likes",
              label: "Likes"
            }
          ]
        },
        {
          name: 'Zeitgranularität',
          type: "timeDimension",
          defaultId: "SocialMedia.datum///day",
          switchItems: [
            {
              id: "SocialMedia.datum///day",
              label: "Tag",
              granularity: "day"
            },
            {
              id: "SocialMedia.datum///week",
              label: "Woche",
              granularity: "week"
            },
            {
              id: "SocialMedia.datum///month",
              label: "Monat",
              granularity: "month"
            }
          ]
        }
      ]
    },
    name: "Verlauf",
    id: 100,
    layout: {x:0,y:3,w:20,h:10}
  },
  {
    vizState: {
      query:{
        "limit": 5000,
        "timeDimensions": [
          {
            "dimension": "SocialMedia.datum",
            "granularity": "month"
          }
        ],
        "segments": [
          "SocialMedia.hatWerte"
        ],
        "filters": [
          {
            "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
            "operator": "equals",
            "values": [
              "EXR"
            ]
          },
          {
            "member": "SocialMedia.interaktionen",
            "operator": "set"
          }
        ],
        "measures": [
          "SocialMedia.followerMonatsstand",
          "SocialMedia.followerGewonnenOrganic",
          "SocialMedia.followerGewonnenPaid",
          "SocialMedia.impressionenOrganic",
          "SocialMedia.impressionenPaid",
          "SocialMedia.interaktionenOrganic",
          "SocialMedia.interaktionenPaid",
          "SocialMedia.klicksOrganic",
          "SocialMedia.klicksPaid",
          "SocialMedia.likesOrganic",
          "SocialMedia.likesPaid",
          "SocialMedia.kommentareOrganic",
          "SocialMedia.kommentarePaid",
          "SocialMedia.beitraege_geteiltOrganic",
          "SocialMedia.beitraege_geteiltPaid"
        ],
        "order": [
          [
            "SocialMedia.datum",
            "asc"
          ]
        ]
      },
      pivotConfig: {
        "x": [
          "measures"
        ],
        "y": [
          "SocialMedia.datum.month"
        ],
        "fillMissingDates": false,
        "joinDateRange": false
      },
      chartType:"pivottable"
    },
    name: "Monatsverlauf",
    id: 110,
    layout: {x:0,y:13,w:24,h:22}
  }
  ]
}

;


