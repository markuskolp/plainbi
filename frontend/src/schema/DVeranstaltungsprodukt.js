cube(`Produkt`, {
  sql: `SELECT * FROM mart.d_veranstaltungsprodukt`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started
  },
  
  joins: {
	  
  },
  
  dimensions: {
	  
    veranstaltungsproduktId: {
      sql: `veranstaltungsprodukt_id`,
      type: `number`,
	  shown: false
    },
	
	vaProduktName: {
		title: `Produkt`,
      sql: `va_produkt_name`,
      type: `string`
    },
    
    vaProduktCode: {
		title: `Produkt Nr`,
      sql: `va_produkt_code`,
      type: `string`
    },
    /*
    vaProduktTyp: {
      sql: `va_produkt_typ`,
      type: `string`
    },
    */
    gueltigkeitstyp: {
      sql: `gueltigkeitstyp`,
      type: `string`,
	  shown: false
    },
    /*
    istFkmRelevant: {
      sql: `ist_fkm_relevant`,
      type: `string`
    },
    
    produktNr: {
      sql: `produkt_nr`,
      type: `string`
    },
    
    produktName: {
      sql: `produkt_name`,
      type: `string`
    },
    
    produktTyp: {
      sql: `produkt_typ`,
      type: `string`
    }
	*/
  },
  
  dataSource: `default`
});
