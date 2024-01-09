import React, {useRef, useCallback} from "react";
import { message } from "antd";
import Axios from "axios";
import { Map as ReactMapGl, NavigationControl, Source, Layer, FullscreenControl} from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { geojsonCountries } from './geojsonCountries.js'; 
import {defaultFillLayer, defaultLineLayer} from './map-style.js';
import {MapRef} from 'react-map-gl';
import { useCubeQuery } from "@cubejs-client/react";

const mapboxtoken = 'pk.eyJ1IjoibWFya3Vza29scDMwNDMwIiwiYSI6ImNscWhxNWVqYTFjdDAya3RrZnUyc2trZ2IifQ.29kFpGDemWCOwA8DUMqJ5w';

const Map = () => {

  let geoData = geojsonCountries;

  //.filter((item) => item['MapboxCoords.coordinates'] != null)  

  const mapRef = useRef();

  const onMapLoad = () => {
    const map = mapRef.current?.getMap();
    map?.getStyle().layers.forEach((thisLayer) => {
      if (thisLayer.id.indexOf("-label") > 0) {
        console.log("onMapLoad() - change text language of layer: " + thisLayer.id);
        map?.setLayoutProperty(thisLayer.id, "text-field", ["get", "name_de"]); // change to german labels
      }
    });
  };

  let data = {
    type: 'FeatureCollection',
    features: [],
  };  

  const { resultSet } = useCubeQuery(  
    {
      "limit": 5000,
      "segments": [
        "Ticket.onlineBestellungen"
      ],
      "measures": [
        "Ticket.anzahlTickets"
      ],
      "order": {
        "Ticket.anzahlTickets": "desc"
      },
      "filters": [
        {
          "member": "Veranstaltung.veranstaltungName",
          "operator": "equals",
          "values": [
            "EXPO REAL 2023"
          ]
        }
      ],
      "dimensions": [
        "Land.land",
        "Land.landIso2"
      ],
      "timeDimensions": []
    }
  );

  const getGeometry = (type, key) => {
    try {
      //console.log("found geometry for key: " + key);
      return geojsonCountries['features'].filter((item)=>item['properties']['ISO_A2'] === key)[0]['geometry'];
    } catch (err) {
      console.log("DID NOT find geometry for: " + key);
      return {"type":"Point","coordinates":[]};
    }
    
  }
  
  if (resultSet) {
    resultSet
      .tablePivot()
      //.filter((item) => item['MapboxCoords.coordinates'] != null)
      .map((item) => {
        data['features'].push({
          type: 'Feature',
          properties: {
            name: item['Land.land'],
            key: item['Land.landIso2'],
            value: parseInt(item[`Ticket.anzahlTickets`])
          }  ,
          geometry: 
            getGeometry('country', item['Land.landIso2']) // get geometry of country

        });
      });
    console.log("data features");
    console.log(data);
  }

  return (
      <div style={{height: "100%"}}>
      <ReactMapGl
        ref={mapRef} 
        mapboxAccessToken={mapboxtoken}
        initialViewState={{
          longitude: 11.576124,
          latitude: 48.137154,
          zoom: 3 ,
          projection: 'naturalEarth' // https://docs.mapbox.com/mapbox-gl-js/guides/projections/
        }} // start with Munich and zoom to see whole Europe
        mapStyle="mapbox://styles/mapbox/light-v11"
        width="100%"
        height="100%"
        onLoad={onMapLoad}
      >
        <NavigationControl />
        <FullscreenControl />
        <Source type="geojson" data={data}>
          <Layer {...defaultFillLayer} />
          <Layer {...defaultLineLayer} />
        </Source>
      </ReactMapGl>
    </div>
  );

};



export default Map;

/*

Heatmap

const { resultSet } = useCubeQuery({ 
  measures: ['Users.count'],
  dimensions: ['Users.geometry'],
});

let data = {
  type: 'FeatureCollection',
  features: [],
};

if (resultSet) {
  resultSet.tablePivot().map((item) => {
    data['features'].push({
      type: 'Feature',
      properties: {
        value: parseInt(item['Users.count']),
      },
      geometry: JSON.parse(item['Users.geometry']),
    });
  });
}
<Source type='geojson' data={data}>
  <Layer {...{
    type: 'heatmap',
    paint: {
      'heatmap-intensity': intensity,
      'heatmap-radius': radius,
      'heatmap-weight': [ 'interpolate', [ 'linear' ], [ 'get', 'value' ], 0, 0, 6, 2 ],
      'heatmap-opacity': 1,
    },
  }} />
</Source>

*/



/*

Choropleth

const { resultSet } = useCubeQuery({
  measures: [ `Users.total` ],
  dimensions: [ 'Users.country', 'MapboxCoords.coordinates' ]
});

if (resultSet) {
  resultSet
    .tablePivot()
    .filter((item) => item['MapboxCoords.coordinates'] != null)
    .map((item) => {
      data['features'].push({
        type: 'Feature',
        properties: {
          name: item['Users.country'],
          value: parseInt(item[`Users.total`])
        },
        geometry: {
          type: 'Polygon',
          coordinates: [ item['MapboxCoords.coordinates'].split(';').map((item) => item.split(',')) ]
        }
      });
    });
}

'fill-color': { 
  property: 'value',
  stops: [ 
    [1000000, `rgba(255,100,146,0.1)`], 
    [10000000, `rgba(255,100,146,0.4)`], 
    [50000000, `rgba(255,100,146,0.8)`], 
    [100000000, `rgba(255,100,146,1)`]
  ],
}

*/