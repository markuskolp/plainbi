cube(`Land`, {
  sql: `SELECT * FROM mart.d_land`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started
  },
  
  joins: {
    
  },
    
  dimensions: {
	landId: {
      sql: `land_id`,
      type: `number`,
      shown: false
    },
	/*
    landNr: {
      sql: `land_nr`,
      type: `string`
    },
	*/
    landIso2: {
		title: `Länderkürzel (ISO2)`,
      sql: `land_iso2`,
      type: `string`
    },
    
    landIso3: {
		title: `Länderkürzel (ISO3)`,
      sql: `land_iso3`,
      type: `string`
    },
    
    land: {
		title: `Land`,
      sql: `land`,
      type: `string`
    },
    
    landGruppe: {
		title: `Ländergruppe`, // In- vs. Ausland
      sql: `land_gruppe`,
      type: `string`
    },
    
    landGruppe2: {
		title: `Ländergruppe (DE separat)`, // In- vs. Ausland
      sql: `land_gruppe_2`,
      type: `string`
    },
	/*    
    inAusland: {
		title: `In-/Ausland`, // In- vs. Ausland
      sql: `in_ausland`,
      type: `string`
    }
	*/
  },
  
  dataSource: `default`
});
