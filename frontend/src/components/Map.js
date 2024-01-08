import React from "react";
import { message } from "antd";
import Axios from "axios";
import { Map as ReactMapGl, NavigationControl, Source, Layer} from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { geojsonCountries } from './geojsonCountries.js';
import {defaultFillLayer, defaultLineLayer} from './map-style.js';

const mapboxtoken = 'pk.eyJ1IjoibWFya3Vza29scDMwNDMwIiwiYSI6ImNscWhxNWVqYTFjdDAya3RrZnUyc2trZ2IifQ.29kFpGDemWCOwA8DUMqJ5w';

const Map = () => {

  const data = geojsonCountries;
  
  return (
      <div style={{height: "100%"}}>
      <ReactMapGl
        mapboxAccessToken={mapboxtoken}
        initialViewState={{
          longitude: 11.576124,
          latitude: 48.137154,
          zoom: 3 
        }} // start with Munich in Zoomlevel 5
        mapStyle="mapbox://styles/mapbox/light-v11"
        width="100%"
        height="100%"

      >
        <NavigationControl />
        <Source type="geojson" data={data}>
          <Layer {...defaultFillLayer} />
          <Layer {...defaultLineLayer} />
        </Source>
      </ReactMapGl>
    </div>
  );
};

export default Map;

