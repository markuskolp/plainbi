cube(`Ticket`, {
  sql: `SELECT * FROM mart.e_ticket`,
  
  preAggregations: {
    // Pre-Aggregations definitions go here
    // Learn more here: https://cube.dev/docs/caching/pre-aggregations/getting-started
  },
  
  segments: {
    
	onlineBestellungen: {
      title: `Onlinebestellungen`,
      sql: `${CUBE.stornoDt} is null and ${CUBE.registrierungDt} is not null and ${CUBE.kaufDt} is not null and ${CUBE.istFkmRelevant} = 'J' and ${CUBE.istTest} = 'N' and ${CUBE.istLegitimiert} <> 'N' and ${Registrierungskanal.registrierungskanalNr} not in ('onsite') `
    }
	
  },
  
  joins: {
    Tickettyp: {
      sql: `${CUBE.ticketTypId} = ${Tickettyp}.ticketTypId`,
      relationship: `belongsTo`
    },
    Produkt: {
      relationship: `belongs_to`,
      sql: `${CUBE.veranstaltungsproduktId} = ${Produkt.veranstaltungsproduktId}`
    },
    Land: {
      relationship: `belongs_to`,
      sql: `${CUBE.besitzerLandId} = ${Land.landId}`
    },
    Vertriebskanal: {
      relationship: `belongs_to`,
      sql: `${CUBE.vertriebskanalId} = ${Vertriebskanal.vertriebskanalId}`
    },
    Veranstaltung: {
      relationship: `belongs_to`,
      sql: `${CUBE.veranstaltungId} = ${Veranstaltung.veranstaltungId}`
    },
    Registrierungskanal: {
      relationship: `belongs_to`,
      sql: `${CUBE.registrierungskanalId} = ${Registrierungskanal.registrierungskanalId}`
    }
  },
  
  measures: {
    anzahlTickets: {
      title: `Anz. Tickets`,
	  sql: `ticket_id`,
      type: `count_distinct`,
      drillMembers: []
    },
	anzahlTicketsKumuliert: {
      title: `Anz. Tickets (kumuliert)`,
      sql: `sum(count(distinct ticket_id)) over (order by ${CUBE.dayBeforeEnd} desc)`,
      type: `number`,
      drillMembers: []
    }
  },
  
  /*
  fehlt:
  
  - segment für Onlinebestellungen - Zeiträume noch einschränken ?
  
			and e.registrierung_dt < current_timestamp
			and e.registrierung_dt <= v.veranstaltung_ende_dt 
			
  - kumulierte Werte -> siehe neue Version von Cube Core
	
  - Ticketkategorie
  
  - war auf Messe (ableiten von MEE Datum)
  
  - drillMember
  */
  
  dimensions: {
	  
	 
    ticketTypId: {
      sql: `ticket_typ_id`,
      type: `number`,
	  shown: false
    },
    veranstaltungsproduktId: {
      sql: `veranstaltungsprodukt_id`,
      type: `number`,
	  shown: false
    },
	besitzerLandId: {
      sql: `besitzer_land_id`,
      type: `number`,
      shown: false
    },	
	vertriebskanalId: {
      sql: `vertriebskanal_id`,
      type: `number`,
      shown: false
    },
	veranstaltungId: {
      sql: `veranstaltung_id`,
      type: `number`,
	  shown: false
    },
    registrierungskanalId: {
      sql: `registrierungskanal_id`,
      type: `number`,
	  shown: false
    },
	  
	  
	  
	  
	dayBeforeEnd: {
	  title: `Tage vor VA-Ende`,
	  sql: `DATEDIFF(DAY, ${CUBE.registrierungDt}, ${Veranstaltung.veranstaltungEndeDt})`,
	  type: `number`
	},
	
	
	
	ticketId: {
      sql: `ticket_id`,
      type: `number`,
      primaryKey: true,
	  shown:false
    },
	
	/*
    ticketNr: {
      sql: `ticket_nr`,
      type: `string`
    },
    */
    quellNr: {
      title: `interne Ticket-Nr.`,
      sql: `quell_nr`,
      type: `string`
    },
    /*
    quelle: {
      sql: `quelle`,
      type: `string`
    },
    */
    barcode: {
      title: `Barcode`,
      sql: `barcode`,
      type: `string`
    },
    /*
    regcode: {
      sql: `regcode`,
      type: `string`
    },
    */
    istDurchGutschein: {
      sql: `ist_durch_gutschein`,
      type: `string`,
	  shown: false
    },
    /*
    aktionscode: {
      sql: `aktionscode`,
      type: `string`
    },
    */
    istTest: {
      title: `ist Testticket/-kauf ?`,
      sql: `ist_test`,
      type: `string`
    },
    
    istFkmRelevant: {
      title: `ist FKM relevant ?`,
      sql: `ist_fkm_relevant`,
      type: `string`
    },
    
    istLegitimiert: {
      title: `ist legitimiert ?`,
      sql: `ist_legitimiert`,
      type: `string`
    },
    /*
    rechnungsnr: {
      sql: `rechnungsnr`,
      type: `string`
    },
    
    erstellungDt: {
      sql: `erstellung_dt`,
      type: `time`
    },
    */
    registrierungDt: {
      title: `Registrierungsdatum`,
      sql: `registrierung_dt`,
      type: `time`
    },
    
    stornoDt: {
      title: `Stornodatum`,
      sql: `storno_dt`,
      type: `time`
    },
    
    kaufDt: {
      title: `Kaufdatum`,
      sql: `kauf_dt`,
      type: `time`
    },
    
    bezahlungDt: {
      title: `Bezahldatum`,
      sql: `bezahlung_dt`,
      type: `time`
    },
    
    meeDt: {
      title: `MEE Datum`,
      sql: `mee_dt`,
      type: `time`
    }
	
  },
  
  dataSource: `default`
});
