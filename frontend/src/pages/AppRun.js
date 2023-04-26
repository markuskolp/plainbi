import React from "react";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import NoPage from "./NoPage";
import Axios from "axios";
import CRUDApp from "../components/CRUDApp";

// TODO: get metadata from API (id or alias) -> if not found -> show error on whole page ! (setAppNotFound = false)

const AppRun = () => {

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
    /*
    let appIndex = -1;
    let pageIndex = 0;
    if (id_type === "id") {
      console.log("type id");
      appIndex = appMetadata.findIndex((x) => x.id === id);
      console.log(appIndex);
    } else {
      console.log("type alias");
      appIndex = appMetadata.findIndex((x) => x.alias === id);
      console.log(appIndex);
    }
    const appMetadataRelevant = appMetadata[appIndex === -1 ? 0 : appIndex];
    */
    // get app metadata
    await Axios.get("/api/crud/metadata/DWH_ADMIN.json").then(
//      await Axios.get("/api/crud/metadata/ADHOC.json").then(
      (res) => {
        //console.log(Array.isArray(res.data));
        //console.log(JSON.stringify(res.data));
        setAppMetadata(res.data);
        //console.log(appMetadata);
        setLoading(false);
      }
    );
  };

  return appNotFound === true ? (
        <NoPage />
      ) : (loading ? (
          <h1>Lädt...</h1>
        ) : (
          <React.Fragment>
            <CRUDApp name={appMetadata.name} pages={appMetadata.pages}/>
          </React.Fragment>
        )
      )
  ;
};


export default AppRun;

