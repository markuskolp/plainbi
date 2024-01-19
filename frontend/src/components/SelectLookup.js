import React from "react";
import { useState, useEffect, useRef, useCallback } from "react";
import Axios from "axios";
import { Select } from "antd";
import LoadingMessage from "./LoadingMessage";

const SelectLookup = ({ name, lookupid, defaultValue, onChange, disabled, token, allowNewValues, multiple = false }) => {

  const [loading, setLoading] = useState(true);
  const [lookupData, setLookupData] = useState([]);

  useEffect(() => {
    getLookupData(lookupid);
  }, [lookupid]);

  // getLookupData
  const getLookupData = async (lookupid) => {

    console.log("getLookupData for id: " + lookupid);
    
    //await Axios.get("/api/data/lookup/"+lookupid+".json").then(
      await Axios.get("/api/repo/lookup/"+lookupid+"/data", {headers: {Authorization: token}}).then(
      (res) => {
        //const resData = res.data; 
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        //console.log("getLookupData result: " + JSON.stringify(resData));
        setLookupData(resData.map((row) => ({
          value: row.r,
          label: row.d
        })));
        setLoading(false);
      }
    );
  };

  const handleChange = (value) => {
    const emuEvent = { "target": { "name": name, "value": value ? value : null}} // emulate event.target.name/.value object // set value to null if undefined (happens with select list if selecting nothing)
    console.log("Select change: " + JSON.stringify(emuEvent));
    onChange(emuEvent); 
  };


  // adds new entries to lookup data if it does not exist
  const currentValue = useRef();
  const onSearch = useCallback((value) => {

    currentValue.current = value;

    if (allowNewValues && value && !lookupData.some((op) => op.label === value)) { //.indexOf(value) === 0)) {
      setLookupData([...lookupData, {
        value: value,
        label: value
      }]);
    } else {
      setLookupData([...lookupData]);
    }
  }, [lookupData]);
  

  return (loading ? (
          <LoadingMessage />
        ) : (
        <React.Fragment>
          <Select
            placeholder="bitte auswählen ..."
            //mode={multiple ? "multiple" : ""}
            allowClear
            showSearch
            disabled={disabled}
            options={lookupData}
            //defaultValue={multiple ? (defaultValue || "").split(",") : defaultValue} // if multiple, then split default value
            defaultValue={defaultValue} // if multiple, then split default value
            onChange={handleChange}
            onSearch={onSearch}
            name={name}
            optionFilterProp="label" // filter by label (not by value/key)
          />
        </React.Fragment>
      )
    )

};

export default SelectLookup;
