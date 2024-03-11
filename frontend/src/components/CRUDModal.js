import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import CRUDFormItem from "./CRUDFormItem";
import {
  Button,
  Modal,
  Form,
  message
} from "antd";

const CRUDModal = ({ tableColumns, handleSave, handleCancel, type, tableName, pk, pkColumns, versioned, isRepo, token }) => {
    
  const [loading, setLoading] = useState(true);
  const [recordData, setRecordData] = useState([]);
  console.log("Rendering with: ", recordData);
  console.log("pkColumns: ", pkColumns);
  let api = "/api/crud/";
  api = isRepo === 'true' ? "/api/repo/" : "/api/crud/"; // switch between repository tables and other datasources

  useEffect(() => {
    type == 'edit' ? getRecordData(tableName, pk) : setRecordData([]);
  }, [type, tableName, pk]);

  // getRecordData
  const getRecordData = async (tableName) => {
    setRecordData(null);

    const queryParams = new URLSearchParams();
    if(versioned) {
      queryParams.append("v", 1);
    }
    queryParams.append("pk", getPKParamForURL(pkColumns));
    console.log("queryParams: " + queryParams.toString());
    //var endpoint = api+tableName+'/' + encodeURIComponent(encodeURIComponent(pk)) + '?'+queryParams;
    var endpoint = api+tableName+'/' + pk + '?'+queryParams;
    //var endpoint = api+tableName+'/' + pk.replace("/", "%2F") + '?'+queryParams;
    console.log("GET endpoint: " + endpoint);

    //await Axios.get("/api/crud/"+tableName+"/"+pk).then(
    //await Axios.get(api+tableName+"/"+ pk +(versioned ? "?v" : "")+(versioned ? "&pk="+getPKParamForURL(pkColumns): "?pk="+getPKParamForURL(pkColumns)), {headers: {Authorization: token}}).then(
    //await Axios.get(api+tableName+"/"+ pk.replace("/", encodeURIComponent(encodeURIComponent("/"))) +(versioned ? "?v" : "")+(versioned ? "&pk="+getPKParamForURL(pkColumns): "?pk="+getPKParamForURL(pkColumns)), {headers: {Authorization: token}}).then(
    await Axios.get(endpoint, {headers: {Authorization: token}}).then(
        (res) => {
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setRecordData(resData);
        console.log(JSON.stringify(recordData));
        setLoading(false);
      }
      ).catch(function (error) {
        setLoading(false);
        message.error('Es gab einen Fehler beim Laden der Daten.');
      }
      )
  };

  
  const getPKParamForURL = (_pkColumn) => {
    var pkforurl = "";
    if (_pkColumn.length <= 1) {
      console.log("only 1 pk");
      // if only 1 pk take it directly
      pkforurl = _pkColumn[0];
    } else {
      console.log("composite pk");
      // if composite key, then build url-specific pk string "&pk=key1,key2,..."
      for (var i = 0; i < _pkColumn.length; i++) {
        pkforurl += _pkColumn[i];
        pkforurl += ",";
      }
      pkforurl = pkforurl.replace(/^,+|,+$/g, ''); // trim "," at beginning and end of string
    }
    console.log("getPKParamForURL: " + pkforurl);
    return pkforurl;
  }

  /*{  
    headers: { 
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    */

  // updateTableRow
  const updateTableRow = async (tableName, record, pk) => {
    setLoading(true);
    console.log("updateTableRow: " + JSON.stringify(record));
    //await Axios.put("/api/crud/"+tableName+"/"+pk, record).then( 
    let endPoint = api+tableName+"/"+pk+(versioned ? "?v" : "")+(versioned ? "&pk="+getPKParamForURL(pkColumns): "?pk="+getPKParamForURL(pkColumns));
    console.log("updateTableRow: endpoint: " + endPoint);
    await Axios.put(endPoint, record, {headers: {Authorization: token}}).then(  
        (res) => {
        message.success('Erfolgreich gespeichert.');
        handleSave();
      }
      ).catch(function (error) {
        setLoading(false);
        message.error('Es gab einen Fehler beim Speichern.');
      }
      )
  };

    // addTableRow
    const addTableRow = async (tableName, record) => {
      setLoading(true);
      console.log("addTableRow: " + JSON.stringify(record));
      //await Axios.post("/api/crud/"+tableName, record).then( 
      let endPoint = api+tableName+(versioned ? "?v" : "")+(versioned ? "&pk="+getPKParamForURL(pkColumns): "?pk="+getPKParamForURL(pkColumns));
      console.log("addTableRow: endpoint: " + endPoint);
      await Axios.post(endPoint, record, {headers: {Authorization: token}}).then( 
          (res) => {
          message.success('Erfolgreich gespeichert.');
          handleSave();
        }
        ).catch(function (error) {
          setLoading(false);
          message.error('Es gab einen Fehler beim Speichern.');
          //message.error(res.data);
        }
        )
    };
  

  const handleOk = () => {
    // add or update to API
    // TODO: check if all required fields are filled (except fields with increment)
    console.log("type: " + type + " / pk: " + pk);
    type === 'edit' ? updateTableRow(tableName, recordData, pk) : addTableRow(tableName, recordData);
  };

  const layout = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 }
  };
  const layoutpage = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 }
  };


  const handleChange = (key, value) =>{
    //console.log("event: " + JSON.stringify(event));
    console.log("recordData: " + JSON.stringify(recordData));
    //const {name, value} = event.target;
    console.log("handleChange - key: " + key + " / value: " + value);
    
    setRecordData({...recordData, [key]: value}); 
  }

  return (
    <React.Fragment>
      <Modal
            //title={name}
            open={true}
            onOk={handleOk}
            onCancel={handleCancel}
            centered
            width="80vw"
            style={{
              maxWidth:"1500px"
            }}
            footer={[
              /*deleteAllowed && <Button
                key="1"
                danger
                htmlType="button"
                icon={<DeleteOutlined />}
                onClick={showDeleteConfirm}
              >Löschen</Button>,
              */
              <Button key="2" htmlType="button" onClick={handleCancel} >Abbrechen</Button>,
              <Button key="3" type="primary" htmlType="submit" onClick={handleOk} >Speichern</Button>
            ]}
            
          >

          <Form {...layoutpage} layout="horizontal">
                { tableColumns && tableColumns.map((column) => {
                  //console.log("recordData: " + recordData);
                  let dataValue = (recordData ? recordData[column.column_name] : ""); // get record data of the current column or set to nothing
                  if (typeof dataValue === 'function') { dataValue = ""; } // if column names are keywords like "sort" then it returns a function - here we get rid of it, otherwise it causes an error later on
                  //console.log("column: " + column.column_name + " | value: " + dataValue);
                  //const dataValue = recordData[column.column_name]; // get record data of the current column or set to nothing

                  return (
                    ((type == 'new' || recordData ) && !column.showsummaryonly) ? // only show if type is "new" or the data record could be retrieved (for "editing") AND the if it is not only displayed on summary page (list view)
                    // only make item editable if it is not part of the primary key
                    <CRUDFormItem type={type} name={column.column_name} label={column.column_label} required={column.required} isprimarykey={pkColumns.includes(column.column_name)} editable={column.editable} lookupid={column.lookup} ui={column.ui} defaultValue={dataValue} onChange={handleChange} tooltip={column.tooltip} multiple={column.multiple} token={token}/>
                    : ""
                  )

                })}
              </Form>



          </Modal>

    </React.Fragment>
  );

};

export default CRUDModal;

      //import remarkGfm from 'remark-gfm';
      //remarkPlugins={[remarkGfm]} />