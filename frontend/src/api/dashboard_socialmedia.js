
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
  dashboardFilter : {
      columnId: "Veranstaltungsreihe.VeranstaltungsreiheNr",
      columnLabel: "Veranstaltungsreihe.VeranstaltungsreiheName",
      defaultValue: "EXR",
      query : {
        "order": [
          [
            "Veranstaltungsreihe.veranstaltungsreiheName",
            "asc"
          ]
        ],
        "dimensions": [
          "Veranstaltungsreihe.veranstaltungsreiheName",
          "Veranstaltungsreihe.veranstaltungsreiheNr"
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
      "measures": [
        "SocialMedia.impressionen"
      ],
      "timeDimensions": [
        {
          "dimension": "SocialMedia.datum",
          "granularity": "day"
        }
      ],
      "order": {
        "SocialMedia.impressionen": "desc"
      },
      "filters": [
        {
          "member": "Veranstaltungsreihe.veranstaltungsreiheCode",
          "operator": "equals",
          "values": [
            "EXR"
          ]
        },
        {
          "member": "SocialMedia.impressionen",
          "operator": "gt",
          "values": [
            "0"
          ]
        }
      ],
      "dimensions": [
        "SocialMediaVertriebsweg.socialMediaVertriebsweg"
      ]
      },
      chartType:"bar"
    },
    name: "Verlauf",
    id: 100,
    layout: {x:0,y:3,w:24,h:8}
  }
  ]
}

;
