import React from "react";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import NoPage from "./NoPage";
import Axios from "axios";
import { message } from "antd";
import CRUDApp from "../components/CRUDApp";
import LoadingMessage from "../components/LoadingMessage";

// TODO: get metadata from API (id or alias) -> if not found -> show error on whole page ! (setAppNotFound = false)

const AppRuntime = (props) => {

  let { id } = useParams(); // get URL parameters - here the "id" of a app
  let id_type = Number.isNaN(id * 1) ? "alias" : "id"; // check whether the "id" refers to the real "id" of the app or its "alias"

  const [appNotFound, setAppNotFound] = useState(false);
  const [loading, setLoading] = useState(true);
  const [appMetadata, setAppMetadata] = useState([]);

  /***
   * Process of the CRUD* components (CRUDApp, CRUDPage)
   * - get app id or alias from URL
   * - get metadata of app from API
   *   - build page list on left
   *   - select first page
   *     - build table on right and fill with data from API
   *     - set buttons (allowed_actions)
   *        - for each row: DELETE against API
   *   - if modal selected (new button), then grab selected page id and open empty modal, also get lookup values from API
   *      - SAVE against API
   *   - if modal selected (edit button), then grab selected row id, fetch row data from API, open modal and fill values, also get lookup values from API
   *      - EDIT (update) against API
   * - if page is switched, set page id and rebuild table on right and fill with data from API
  */

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    // get app metadata
    await Axios.get("/api/repo/application/"+id, {headers: {Authorization: props.token}}).then(
        (res) => {
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        //console.log(JSON.stringify(resData));
        //console.log(JSON.parse(resData.spec_json).pages);
        setAppMetadata(resData);
        setLoading(false);
      }
    ).catch(
      function (error) {
        setAppNotFound(true);
        setLoading(false);
        message.error('Es gab einen Fehler beim Laden der Applikation.');
      }
    );
  };
  

  return appNotFound === true ? (
        <NoPage />
      ) : (loading ? (
          <LoadingMessage />
        ) : (
          <React.Fragment>
            <CRUDApp name={appMetadata.name} pages={JSON.parse(appMetadata.spec_json).pages} token={props.token}/>
          </React.Fragment>
        )
      )
  ;

};


export default AppRuntime;
