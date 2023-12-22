cube(`Tickettyp`, {
  sql: `SELECT * FROM mart.d_ticket_typ`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started
  },
  
  joins: {
    
  },
  
  dimensions: {
    ticketTypNr: {
		title: `Tickettyp (Kürzel)`,
      sql: `ticket_typ_nr`,
      type: `string`
    },
    /*
    ticketTypSort: {
      sql: `ticket_typ_sort`,
      type: `string`
    },
    */
    ticketTypId: {
      sql: `ticket_typ_id`,
      type: `number`,
	  shown: false
    },
    ticketTypName: {
		title: `Tickettyp`,
      sql: `ticket_typ_name`,
      type: `string`
    }
  },
  
  dataSource: `default`
});
