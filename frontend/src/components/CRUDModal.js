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

const CRUDModal = ({ tableColumns, handleSave, handleCancel, type, tableName, pk, versioned, isRepo }) => {
    
  const [loading, setLoading] = useState(true);
  const [recordData, setRecordData] = useState([]);
  let api = "/api/crud/";
  api = isRepo === 'true' ? "/api/repo/" : "/api/crud/"; // switch between repository tables and other datasources

  useEffect(() => {
    type == 'edit' ? getRecordData(tableName, pk) : setRecordData(null);
  }, [type, tableName, pk]);

  // getRecordData
  const getRecordData = async (tableName) => {
    setRecordData(null);
    //await Axios.get("/api/crud/"+tableName+"/"+pk).then(
    await Axios.get(api+tableName+"/"+pk+(versioned ? "?v" : "")).then(
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

  /*{  
    headers: { 
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    */

  // updateTableRow
  const updateTableRow = async (tableName, record, pk) => {
    setLoading(true);
    //await Axios.put("/api/crud/"+tableName+"/"+pk, record).then( 
    await Axios.put(api+tableName+"/"+pk+(versioned ? "?v" : ""), record).then(  
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
    const addTableRow = async (tableName, record, pk) => {
      setLoading(true);
      //await Axios.post("/api/crud/"+tableName, record).then( 
      await Axios.post(api+tableName+(versioned ? "?v" : ""), record).then( 
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
  

  const handleOk = () => {
    // add or update to API
    // TODO: check if all required fields are filled (except fields with increment)
    type === 'edit' ? updateTableRow(tableName, recordData, pk) : addTableRow(tableName, recordData, pk);
  };

  const layout = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 }
  };
  const layoutpage = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 }
  };


  const handleChange = (event) =>{
    const {name, value} = event.target;
    console.log("handleChange - name: " + name + " / value: " + value);
    setRecordData({...recordData, [name]: value}); 
  }

  return (
    <React.Fragment>
      <Modal
            title={name}
            open={true}
            onOk={handleOk}
            onCancel={handleCancel}
            centered
            width={1000}
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

                  const dataValue = (recordData ? recordData[column.column_name] : ""); // get record data of the current column or set to nothing
                  //const dataValue = recordData[column.column_name]; // get record data of the current column or set to nothing

                  return (
                    (type == 'new' || recordData ) ? // only show if type is "new" or the data record could be retrieved (for "editing")
                    <CRUDFormItem name={column.column_name} label={column.column_label} required={column.required} editable={column.editable} lookupid={column.lookup} ui={column.ui} defaultValue={dataValue} handleChange={handleChange}/>
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