import React from "react";
import { Map as ReactMapGl, NavigationControl} from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const mapboxtoken = 'pk.eyJ1IjoibWFya3Vza29scDMwNDMwIiwiYSI6ImNscWhxNWVqYTFjdDAya3RrZnUyc2trZ2IifQ.29kFpGDemWCOwA8DUMqJ5w';

const Map = () => {

  useEffect(() => {
    initialize();
  }, []);

  const initialize = async () => {

    await Axios.get("/api/repo/application", {headers: {Authorization: props.token}}).then(
      (res) => {
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setApps(resData);
        setLoading(false);
      }
    ).catch(
      function (error) {
        setError(true);
        setLoading(false);
        message.error('Es gab einen Fehler beim Laden der Applikationen.');
      }
    );
    
  };
  
  return (
      <div style={{height: "100%"}}>
      <ReactMapGl
        mapboxAccessToken={mapboxtoken}
        initialViewState={{
          longitude: 11.576124,
          latitude: 48.137154,
          zoom: 3 
        }} // start with Munich in Zoomlevel 5
        mapStyle="mapbox://styles/mapbox/light-v9"
        width="100%"
        height="100%"

      >
        <NavigationControl />
      </ReactMapGl>
    </div>
  );
};

export default Map;

