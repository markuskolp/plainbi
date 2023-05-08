import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Select } from "antd";


const SelectLookup = ({ lookupid, defaultValue }) => {

  const [loading, setLoading] = useState(true);
  const [lookupData, setLookupData] = useState([]);

  useEffect(() => {
    getLookupData(lookupid);
  }, [lookupid]);

  // getTableData
  const getLookupData = async (lookupid) => {

    console.log("getLookupData for id: " + lookupid);
    
    await Axios.get("/api/data/lookup/"+lookupid+".json").then(
      (res) => {
        console.log("getLookupData result: " + JSON.stringify(res.data));
        setLookupData(res.data.map((row) => ({
          value: row.r,
          label: row.d
        })));
        setLoading(false);
      }
    );
  };

  return (loading ? (
          <h1>Lädt...</h1>
        ) : (
        <React.Fragment>
          <Select
            placeholder="bitte auswählen ..."
            allowClear
            showSearch
            options={lookupData}
            defaultValue={defaultValue}
          />
        </React.Fragment>
      )
    )

};

export default SelectLookup;
