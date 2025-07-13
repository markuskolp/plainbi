import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import CRUDFormItem from "./CRUDFormItem";
import {
  Button,
  Modal,
  Form,
  message,
  Alert,
  Tooltip
} from "antd";

const CRUDModal = ({ tableColumns, handleSave, handleCancel, type, tableName, pk, pkColumns, userColumn, versioned, datasource, isRepo, token, sequence, externalActions }) => {
    
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [errorDetail, setErrorDetail] = useState('');
  const [recordData, setRecordData] = useState([]);
  
  const [externalActionTimeout, setExternalActionTimeout]=useState(null);
  const [username, setUsername] = useState("plainbi"); 

  console.log("Rendering with: ", recordData);
  console.log("pkColumns: ", pkColumns);
  console.log("pk: ", pk);
  let api = "/api/crud/";
  api = isRepo === 'true' ? "/api/repo/" : "/api/crud/" + (datasource ? datasource+'/' : '');  // switch between repository tables and other datasources /api/crud/<db>/<table>

  console.log("CRUDModal.js");

  useEffect(() => {
    console.log("CRUDModal.js - useEffect()");
    (type == 'edit' || type == 'duplicate') ? getRecordData(tableName, pk) : setRecordData([]);
  }, [type, tableName, pk]);

  // getRecordData
  const getRecordData = async (tableName) => {
    setRecordData(null);

    const queryParams = new URLSearchParams();
    
    if(versioned) {
      queryParams.append("v", 1);
    }

    queryParams.append("pk", getPKParamForURL(pkColumns));
    
    let _cols = getColsParamForURL(tableColumns);
    queryParams.append("cols", _cols); 

    console.log("queryParams: " + queryParams.toString());
    //var endpoint = api+tableName+'/' + encodeURIComponent(encodeURIComponent(pk)) + '?'+queryParams;
    var endpoint = api+tableName+'/' + pk + '?'+queryParams;
    //var endpoint = api+tableName+'/' + pk.replaceAll("/", "%2F") + '?'+queryParams;
    //var endpoint = api+tableName+'/' + encodeURIComponent(pk) + '?'+queryParams;
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
          setError(true);
          // not necessary to check token here because AppRuntime.js does this
          //if (error.response.status === 401) {
            //props.removeToken()
            //message.error('Session ist abgelaufen');
          //} else {
            setErrorMessage('Es gab einen Fehler beim Laden der Daten');
            setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
          //}
          console.log(error);
          console.log(error.response.data.message);
      }
      )
  };

  
  const getUsername = async () => {
    await Axios.get("/api/profile", {headers: {Authorization: token}}).then(
      (res) => {
        //console.log(JSON.stringify(res));
        const resData = res.data;
        console.log("/profile response: " + JSON.stringify(resData));
        setUsername(resData.username);
        console.log("setUsername: " + resData.username)
      }
    ).catch(
      function (error) {
        console.log(error);
        console.log(error.response.data.message);
      }
    );
  }

  const replaceColumnVariables = (input) => {
     let _input = input;
     tableColumns && tableColumns.map((column) => {
      let dataValue = (recordData ? recordData[column.column_name] : null); // get record data of the current column or set to null
      console.log("replaceColumnVariables - column: " + column.column_name + " | value: " + dataValue);
      _input = _input.replaceAll("${"+column.column_name+"}", dataValue);
    })
    console.log("replaceColumnVariables - before: " + input);
    console.log("replaceColumnVariables - after: " + _input);
    return _input;
  }
  
  const callStoredProcedure = (id, wait_repeat_in_ms = 1000, name, body) => {

    body = replaceColumnVariables(body);

    console.log("callStoredProcedure with id: " + id);
    if(externalActionTimeout) {
      message.info("Sie müssen " + wait_repeat_in_ms / 1000 + " Sekunden warten, bevor die Aktion wiederholt werden darf.")
      console.log("external action already called ... waiting for timeout to allow repeat"); // do nothing // clearTimeout(externalActionTimeout);
    } else {
      console.log("calling external action");
      message.info("Aktion wird ausgelöst")

      // replace placeholders in body - ${username}
      body = body.replaceAll('${username}', username);
      console.log("replaced body ${username} with " + username);

      const url = '/api/exec/' + (datasource ? datasource+'/' : '') + name;
      console.log("callStoredProcedure with url: " + url);

      Axios.defaults.headers.post['Content-Type'] ='application/json;charset=utf-8';
      Axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
      //header.Add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
      Axios.post(url, body, {headers: {Authorization: token}}).then(   // await // 
          (res) => {
            console.log(JSON.stringify(res));
            const resData = (res.data.error === undefined ? res : res.data); 
            console.log(JSON.stringify(resData));
            if (resData.error) { // response might be "200 OK", but still check for error in response body
              message.error(JSON.stringify(resData.error));
            } else {
              message.success('Erfolgreich ausgelöst.');
            }
          }
        ).catch(function (error) {
          message.error('Es gab einen Fehler beim Auslösen der Aktion');
          console.log(error);
        }
        )

      setExternalActionTimeout( 
        setTimeout(() => {
          console.log("timeout over")
          setExternalActionTimeout(null)
          clearTimeout(externalActionTimeout)
        }, wait_repeat_in_ms)
      );
      console.log("timeout for repeat set to " + wait_repeat_in_ms + " ms");
    }

  }

  const callRestAPI = (id, wait_repeat_in_ms = 1000, url, body) => {

    body = replaceColumnVariables(body);

    console.log("callRestAPI with id: " + id);
    if(externalActionTimeout) {
      message.info("Sie müssen " + wait_repeat_in_ms / 1000 + " Sekunden warten, bevor die Aktion wiederholt werden darf.")
      console.log("external action already called ... waiting for timeout to allow repeat"); // do nothing // clearTimeout(externalActionTimeout);
    } else {
      console.log("calling external action");
      message.info("Aktion wird ausgelöst")

      // todo: check method and switch between them. only allowed: get, post ?
      // todo: check for contenttype

      // replace placeholders in body - ${username}
      body = body.replaceAll('${username}', username);
      console.log("replaced body ${username} with " + username);

      Axios.defaults.headers.post['Content-Type'] ='application/json;charset=utf-8';
      Axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
      //header.Add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
      Axios.post(url, body).then(   // await // , {headers: {Authorization: token}}
          (res) => {
            console.log(JSON.stringify(res));
            const resData = (res.data.error === undefined ? res : res.data); 
            console.log(JSON.stringify(resData));
            if (resData.error) { // response might be "200 OK", but still check for error in response body
              message.error(JSON.stringify(resData.error));
            } else {
              message.success('Erfolgreich ausgelöst.');
            }
          }
        ).catch(function (error) {
          message.error('Es gab einen Fehler beim Auslösen der Aktion');
          console.log(error);
        }
        )

      setExternalActionTimeout( 
        setTimeout(() => {
          console.log("timeout over")
          setExternalActionTimeout(null)
          clearTimeout(externalActionTimeout)
        }, wait_repeat_in_ms)
      );
      console.log("timeout for repeat set to " + wait_repeat_in_ms + " ms");
    }
    
  }

  
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

  const getColsParamForURL = (_cols) => {
    var colsforurl = "";
    if (_cols.length <= 1) {
      console.log("only 1 column");
      // if only 1 column take it directly
      colsforurl = _cols[0].column_name;
    } else {
      console.log("several columns");
      // if several columns, then build url-specific string "&cols=<column_name1>,<column_name2>,..."
      for (var i = 0; i < _cols.length; i++) {
        if (_cols[i].showsummaryonly == 'true') {
          // do nothing
          console.log("getColsParamForURL - showsummaryonly: " + _cols[i].showsummaryonly + " - ignore column: " + _cols[i].column_name);
        } else {
          colsforurl += _cols[i].column_name;
          colsforurl += ",";
        }
      }
      colsforurl = colsforurl.replace(/^,+|,+$/g, ''); // trim "," at beginning and end of string
    }
    console.log("getColsParamForURL: " + colsforurl);
    return colsforurl;
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

    const queryParams = new URLSearchParams();
    
    if(versioned) {
      queryParams.append("v", 1);
    }

    queryParams.append("pk", getPKParamForURL(pkColumns));
    
    if(userColumn) {
      queryParams.append("usercol", userColumn);
    }

    console.log("queryParams: " + queryParams.toString());
    var endpoint = api+tableName+'/' + pk + '?'+queryParams;
    //let endPoint = api+tableName+"/"+pk+(versioned ? "?v" : "")+(versioned ? "&pk="+getPKParamForURL(pkColumns): "?pk="+getPKParamForURL(pkColumns));

    console.log("updateTableRow: endpoint: " + endpoint);
    await Axios.put(endpoint, record, {headers: {Authorization: token}}).then(  
        (res) => {
        message.success('Erfolgreich gespeichert.');
        handleSave();
      }
      ).catch(function (error) {
        setLoading(false);
        setErrorMessage('Es gab einen Fehler beim Speichern');
        try{setErrorDetail(error.response.data.detail);}catch(err){}
        setError(true);
        console.log(error);
      }
      )
  };

    // addTableRow
    const addTableRow = async (tableName, record) => {
      setLoading(true);
      console.log("addTableRow: " + JSON.stringify(record));
      
      const queryParams = new URLSearchParams();
    
      if(versioned) {
        queryParams.append("v", 1);
      }
  
      queryParams.append("pk", getPKParamForURL(pkColumns));
      
      if(userColumn) {
        queryParams.append("usercol", userColumn);
      }
  
      if(sequence) {
        queryParams.append("seq", sequence);
      }

      console.log("queryParams: " + queryParams.toString());
      var endpoint = api+tableName+'?'+queryParams;

      console.log("addTableRow: endpoint: " + endpoint);
      await Axios.post(endpoint, record, {headers: {Authorization: token}}).then( 
          (res) => {
          message.success('Erfolgreich gespeichert.');
          handleSave();
        }
        ).catch(function (error) {
          /*console.log("error.message: " + error.message);
          console.log("error.response: " + error.response);
          console.log("error.response.data: " + error.response.data);
          console.log("error.response.data.detail: " + error.response.data.detail);
          console.log("error.response.data.message: " + error.response.data.message);
          console.log("error.response.status: " + error.response.status)
          console.log("error.response.headers: " + error.response.headers)
          console.error('Request Failed:', error.config);
          */
          setLoading(false);
          setErrorMessage('Es gab einen Fehler beim Speichern');
          try{setErrorDetail(error.response.data.detail);}catch(err){}
          setError(true);
          console.log(error);
        }
        )
    };
  

  const handleOk = () => {
    // add or update to API
    // TODO: check if all required fields are filled (except fields with increment)
    console.log("type: " + type + " / pk: " + pk);
    type === 'edit' ? updateTableRow(tableName, recordData, pk) : addTableRow(tableName, recordData); // add is used for 'new' and 'duplicate'
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
    
    setRecordData({...recordData, [key]: (value === "" ? null : value)}); // leere Inhalte wirklich auf NULL setzen
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
            maskClosable={false}
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

          {error && (
            <Alert
              message={errorMessage}
              description={errorDetail}
              type="error"
              showIcon
            />
          )}

          {type == 'edit' && externalActions && externalActions.map((externalAction) => {
            return ( externalAction.type === 'call_rest_api' && (externalAction.position === 'detail' || !externalAction.position) ?
              <Tooltip title={externalAction.tooltip ? externalAction.tooltip : ''}>
                <Button onClick={(e) => {callRestAPI(externalAction.id, externalAction.wait_repeat_in_ms, externalAction.url, externalAction.body)}}>
                  {externalAction.label}
                </Button>
              </Tooltip>
              : null
            ) 
          })}
          
          {type == 'edit' && externalActions && externalActions.map((externalAction) => {
            return ( externalAction.type === 'call_stored_procedure' && (externalAction.position === 'detail' || !externalAction.position) ?
              <Tooltip title={externalAction.tooltip ? externalAction.tooltip : ''}>
                <Button onClick={(e) => {callStoredProcedure(externalAction.id, externalAction.wait_repeat_in_ms, externalAction.name, externalAction.body)}}>
                  {externalAction.label}
                </Button>
              </Tooltip>
              : null
            ) 
          })}

          <Form {...layoutpage} layout="horizontal">
                { tableColumns && tableColumns.map((column) => {
                  //console.log("recordData: " + recordData);
                  let defaultValue = column.default_value ? column.default_value : ""; // default value from app specification, otherwise just empty
                  //console.log("column.default_value: " + column.default_value + " - using: " + defaultValue);
                  let dataValue = (recordData ? recordData[column.column_name] : defaultValue); // get record data of the current column or set to default value
                  if(dataValue === undefined ) dataValue = defaultValue; // somehow dtaavalue stays undefined when trying to set defaultvalue above. check here and do it again
                  console.log("dataValue: " + dataValue);
                  if (typeof dataValue === 'function') { dataValue = ""; console.log('typeof dataValue === function'); } // if column names are keywords like "sort" then it returns a function - here we get rid of it, otherwise it causes an error later on
                  //console.log("column: " + column.column_name + " | value: " + dataValue);
                  //const dataValue = recordData[column.column_name]; // get record data of the current column or set to nothing

                  return (
                    ((type == 'new' || recordData ) && !column.showsummaryonly) ? // only show if type is "new" or the data record could be retrieved (for "editing" a record or creating a "duplicate") AND if it is not only displayed on summary page (list view)
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