import React, {useRef, useCallback} from "react";
import { Map as ReactMapGl, NavigationControl, Source, Layer, FullscreenControl} from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { geojsonCountries } from './geojsonCountries.js'; 
import { geojsonCountriesCentroids } from './geojsonCountriesCentroids.js'; 
//import {defaultFillLayer, defaultLineLayer} from './map-style.js';
//import {MapRef} from 'react-map-gl';
//import * as turf from '@turf/turf';

const mapboxtoken = 'pk.eyJ1IjoibWFya3Vza29scDMwNDMwIiwiYSI6ImNscWhxNWVqYTFjdDAya3RrZnUyc2trZ2IifQ.29kFpGDemWCOwA8DUMqJ5w';

const Map = ( { resultSet }) => {

  let geoData = geojsonCountries;

  const options = [
    {
      'fill-color': {
        property: 'value',
        stops: [
          [50, `rgba(125, 179, 255,0.1)`],
          [100, `rgba(125, 179, 255,0.4)`],
          [5000, `rgba(125, 179, 255,0.8)`],
          [10000, `rgba(125, 179, 255,1)`]
        ]
      }
    },
    {
      type: 'symbol',
      layout: {
        'text-field': ['number-format', ['get', 'value'], { 'min-fraction-digits': 0, 'max-fraction-digits': 0 }],
        'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
        'text-size': {
          property: 'value',
          stops: [
            [{ zoom: 0, value: 50 }, 10],
            [{ zoom: 0, value: 100 }, 12],
            [{ zoom: 0, value: 5000 }, 14],
            [{ zoom: 0, value: 10000 }, 16]
          ]
        }
      },
      paint: {
        'text-color': ['case', ['<', ['get', 'value'], 100000000], '#43436B', '#43436B'],
        'text-halo-color': '#FFFFFF',
        'text-halo-width': 1
      }
    }
  ];

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

  let dataCentroid = {
    type: 'FeatureCollection',
    features: [],
  };  


  const getGeometry = (type, key) => {
    try {
      return geojsonCountries['features'].filter((item)=>item['properties']['ISO_A2'] === key)[0]['geometry'];
    } catch (err) {
      console.log("getGeometry(): error for: " + key);
      return {"type":"Point","coordinates":[]};
    }    
  }

  const getGeometryCentroid = (type, key) => {
    try {
      /*
      //turf.centroid
      const countryGeoJSON = geojsonCountries['features'].filter((item)=>item['properties']['ISO_A2'] === key)[0];
      return turf.centroid(countryGeoJSON)['geometry']; 
      */
      const countryGeoJSON = geojsonCountriesCentroids.filter((item)=>item['alpha2'] === key)[0];
      console.log("countryGeoJSON");
      console.log(countryGeoJSON);
      return {"type":"Point","coordinates":[countryGeoJSON['longitude'], countryGeoJSON['latitude']]}; 
    } catch (err) {
      console.log("getGeometryCentroid(): error for: " + key);
      return {"type":"Point","coordinates":[]};
    }    
  }
/*

latitude / longitude --> 

"geometry": {
        "type": "Point",
        "coordinates": [
            -12.878009033203103,
            39.2562406539917
        ]
    }
*/
  
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
        dataCentroid['features'].push({
          type: 'Feature',
          properties: {
            name: item['Land.land'],
            key: item['Land.landIso2'],
            value: parseInt(item[`Ticket.anzahlTickets`])
          }  ,
          geometry: 
            getGeometryCentroid('country', item['Land.landIso2']) // get geometry of country
        });
      });
    console.log("data features");
    console.log(data);
    console.log("centroid of data features");
    console.log(dataCentroid);

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
          <Layer beforeId="country-label" id="countries" type="fill" paint={options[0]} />
        </Source>
        <Source type="geojson" data={dataCentroid}>
          <Layer {...options[1]} />
        </Source>
      </ReactMapGl>
    </div>
  );

};



export default Map;

/*
          <Layer {...defaultFillLayer} />
          <Layer {...defaultLineLayer} />
*/

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

          [50, `rgba(255,100,146,0.1)`],
          [100, `rgba(255,100,146,0.4)`],
          [5000, `rgba(255,100,146,0.8)`],
          [10000, `rgba(255,100,146,1)`]

*/