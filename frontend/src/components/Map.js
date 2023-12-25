import React, {useState} from "react";
import { Button, Empty } from "antd";
import { Map as ReactMapGl, NavigationControl} from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';


const mapboxtoken = 'pk.eyJ1IjoibWFya3Vza29scDMwNDMwIiwiYSI6ImNscWhxNWVqYTFjdDAya3RrZnUyc2trZ2IifQ.29kFpGDemWCOwA8DUMqJ5w';

const Map = () => {
  
  const [viewport, setViewport] = useState();

  return (
    <React.Fragment>
      <ReactMapGl
        {...viewport}
        mapboxAccessToken={mapboxtoken}
        initialViewState={{
          longitude: 11.576124,
          latitude: 48.137154,
          zoom: 3 
        }} // start with Munich in Zoomlevel 5
        mapStyle="mapbox://styles/mapbox/light-v9"
        width="100%"
        height="100%"
        onViewportChange={viewport => setViewport(viewport)}
      >
        <NavigationControl />
      </ReactMapGl>
    </React.Fragment>
  );
};

export default Map;


/*

  const [view, setViewport] = useState({
    longitude: 11.576124,
    latitude: 48.137154,
    zoom: 3 
  }); // start with Munich in Zoomlevel 5

  return (
    <React.Fragment>
      <ReactMapGl
        {...view}
        mapboxAccessToken={mapboxtoken}
        style={{width: '100%', height: '100%'}}
        //mapStyle="mapbox://styles/mapbox/streets-v9"
        mapStyle="mapbox://styles/mapbox/light-v9"
        //onViewportChange={viewport => setViewport(viewport)}
      >
        <NavigationControl />
      </ReactMapGl>
    </React.Fragment>
  );
};


*/