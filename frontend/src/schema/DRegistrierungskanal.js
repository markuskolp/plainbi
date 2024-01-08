cube(`Registrierungskanal`, {
  sql: `SELECT * FROM mart.d_registrierungskanal`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started
  },
  
  joins: {
    
  },
  
  
  dimensions: {
	
    registrierungskanalNr: {
      sql: `registrierungskanal_nr`,
      type: `string`,
	  shown: false
    },
    
    registrierungskanalSort: {
      sql: `registrierungskanal_sort`,
      type: `string`
    },
	
    
    registrierungskanalId: {
      sql: `registrierungskanal_id`,
      type: `number`,
	  shown: false
    },
    registrierungskanalName: {
		title: `Registrierungskanal`,
      sql: `registrierungskanal_name`,
      type: `string`
    }
  },
  
  dataSource: `default`
});
