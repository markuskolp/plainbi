cube(`Vertriebskanal`, {
  sql: `SELECT * FROM mart.d_vertriebskanal`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started
  },
  
  joins: {
    
  },
  
  
  dimensions: {
	  /*
    vertriebskanalNr: {
      sql: `vertriebskanal_nr`,
      type: `string`
    },
    
    vertriebskanalSort: {
      sql: `vertriebskanal_sort`,
      type: `string`
    },
    
    vertriebskanalTyp: {
      sql: `vertriebskanal_typ`,
      type: `string`
    },
    */
	
	vertriebskanalId: {
      sql: `vertriebskanal_id`,
      type: `number`,
      shown: false
    },
    vertriebskanalName: {
		title: `Vertriebskanal`,
      sql: `vertriebskanal_name`,
      type: `string`
    }
  },
  
  dataSource: `default`
});
