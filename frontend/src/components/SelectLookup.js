import React from "react";
import { useState, useEffect, useRef, useCallback } from "react";
import Axios from "axios";
import { Select, message, Alert, Typography, Space } from "antd";
import LoadingMessage from "./LoadingMessage";
import { AlertOutlined, WarningOutlined } from "@ant-design/icons";
const { Text } = Typography;

const SelectLookup = ({ name, lookupid, defaultValue, onChange, disabled, token, allowNewValues, multiple = false }) => {

  const [loading, setLoading] = useState(true);
  const [lookupData, setLookupData] = useState([]);
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [errorDetail, setErrorDetail] = useState('');

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
            value: row.r === 0 ? row.r.toString() : row.r, // Ant Select Element cannot handle the value 0 - it turns it to NULL - therefore it is casted to a string here
            label: row.d
          })));
          setLoading(false);
        }
        ).catch(
          function (error) {
            setError(true);
            setLoading(false);
            setErrorMessage('Es gab einen Fehler beim Laden der Werte.');
            setErrorDetail(error.toString());
            console.log(error);
            //console.log(error.response.data.message);
            //console.log(error.response.data.detail);
          }
      );
  };

  const handleChange = (value) => {
    const valueCleansed = Array.isArray(value) ? value.join(",") : value; // split Array into 1 string separated by (mulitselect) "," -  otherwise leave value (single)
    const emuEvent = { "target": { "name": name, "value": valueCleansed ? valueCleansed : null}} // emulate event.target.name/.value object // set value to null if undefined (happens with select list if selecting nothing)
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
        ) : (error ? (
              <Space>
                <WarningOutlined style={{color:'darkred'}}/>
                <Text style={{color:'darkred'}}>{errorMessage}</Text>
              </Space>
            ) : (
            <React.Fragment>
              <Select
                placeholder="bitte auswählen ..."
                mode={multiple ? "multiple" : ""}
                allowClear
                showSearch
                disabled={disabled}
                options={lookupData}
                defaultValue={multiple ? (defaultValue || "").split(",") : (defaultValue === 0 ? defaultValue.toString(): defaultValue)} // if multiple, then split default value // Ant Select Element cannot handle the value 0 - it turns it to NULL - therefore it is casted to a string here
                //defaultValue={defaultValue} // if multiple, then split default value
                onChange={handleChange}
                onSearch={onSearch}
                name={name}
                optionFilterProp="label" // filter by label (not by value/key)
              />
            </React.Fragment>
          )
        )
    )
};

export default SelectLookup;
