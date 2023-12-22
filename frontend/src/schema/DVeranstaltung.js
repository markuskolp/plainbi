cube(`Veranstaltung`, {
  sql: `SELECT * FROM mart.d_veranstaltung`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started
  },
  
  joins: {
    
  },
  
  
  dimensions: {
	  
	veranstaltungId: {
      sql: `veranstaltung_id`,
      type: `number`,
	  shown: false
    },
	/*
    veranstaltungNr: {
      sql: `veranstaltung_nr`,
      type: `string`
    },
    
    veranstaltungCode: {
      sql: `veranstaltung_code`,
      type: `string`
    },
	*/
    
    veranstaltungName: {
		title: `Veranstaltung`,
      sql: `veranstaltung_name`,
      type: `string`
    },
	veranstaltungJahr: {
		title: `Veranstaltungsjahr`,
      sql: `veranstaltung_jahr`,
      type: `number`
    },
    /*
    veranstaltungStatus: {
      sql: `veranstaltung_status`,
      type: `string`
    },
    
    veranstaltungUrl: {
		title: `Webseite (URL)`,
      sql: `veranstaltung_url`,
      type: `string`
    },
    
    istErstveranstaltung: {
      sql: `ist_erstveranstaltung`,
      type: `string`
    },
    
    istTerminal: {
      sql: `ist_terminal`,
      type: `string`
    },
    
    veranstaltungsreiheNr: {
      sql: `veranstaltungsreihe_nr`,
      type: `string`
    },
    */
    veranstaltungsreiheName: {
		title: `Veranstaltungsreihe`,
      sql: `veranstaltungsreihe_name`,
      type: `string`
    },
    /*
    veranstaltungsreiheCode: {
      sql: `veranstaltungsreihe_code`,
      type: `string`
    },
    
    veranstaltungsreiheUrl: {
      sql: `veranstaltungsreihe_url`,
      type: `string`
    },
    
    veranstaltungsreiheLogoUrl: {
      sql: `veranstaltungsreihe_logo_url`,
      type: `string`
    },
    
    veranstaltungsreiheGeschaeftsbereich: {
      sql: `veranstaltungsreihe_geschaeftsbereich`,
      type: `string`
    },
    
    veranstaltungsreiheProjektgruppe: {
      sql: `veranstaltungsreihe_projektgruppe`,
      type: `string`
    },
    
    veranstaltungsreiheKategorieNr: {
      sql: `veranstaltungsreihe_kategorie_nr`,
      type: `string`
    },
    
    veranstaltungsreiheKategorie: {
      sql: `veranstaltungsreihe_kategorie`,
      type: `string`
    },
    
    veranstalterNr: {
      sql: `veranstalter_nr`,
      type: `string`
    },
    
    veranstalter: {
      sql: `veranstalter`,
      type: `string`
    },
    */
    veranstaltungBeginnDt: {
		title: `Beginn`,
      sql: `veranstaltung_beginn_dt`,
      type: `time`
    },
    
    veranstaltungEndeDt: {
		title: `Ende`,
      sql: `veranstaltung_ende_dt`,
      type: `time`
    },
    /*
    veranstaltungVerkaufsstartDt: {
		title: `Verkaufsstart (Aussteller)`,
      sql: `veranstaltung_verkaufsstart_dt`,
      type: `time`
    }
	*/
  },
  
  dataSource: `default`
});
