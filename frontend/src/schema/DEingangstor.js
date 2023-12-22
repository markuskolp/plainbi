cube(`DEingangstor`, {
  sql: `SELECT * FROM mart.d_eingangstor`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started
  },
  
  joins: {
    
  },
  
  dimensions: {
    /*
	eingangstorNr: {
      sql: `eingangstor_nr`,
      type: `string`
    },
	*/
	eingangstorId: {
      sql: `eingangstor_id`,
      type: `number`,
	  shown: false
    },
    
    eingangstorName: {
		title: `Eingang`,
      sql: `eingangstor_name`,
      type: `string`
    },
    /*
    eingangstorKurz: {
      sql: `eingangstor_kurz`,
      type: `string`
    },
    
    eingangstorCode: {
      sql: `eingangstor_code`,
      type: `string`
    },
    */
    eingangstorGruppe: {
		title: `Eingang (Gruppe)`,
      sql: `eingangstor_gruppe`,
      type: `string`
    }
  },
  
  dataSource: `default`
});
