import React, {useRef, useCallback} from "react";
import { message } from "antd";
import Axios from "axios";
import { Map as ReactMapGl, NavigationControl, Source, Layer, FullscreenControl} from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { geojsonCountries } from './geojsonCountries.js';
import {defaultFillLayer, defaultLineLayer} from './map-style.js';
import {MapRef} from 'react-map-gl';

const mapboxtoken = 'pk.eyJ1IjoibWFya3Vza29scDMwNDMwIiwiYSI6ImNscWhxNWVqYTFjdDAya3RrZnUyc2trZ2IifQ.29kFpGDemWCOwA8DUMqJ5w';

const Map = () => {

  const data = geojsonCountries;
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
        }} // start with Munich in Zoomlevel 5
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

