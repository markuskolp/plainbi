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

const CRUDModal = ({ tableColumns, handleClose, type, tableName, pk }) => {
    
  const [loading, setLoading] = useState(true);
  const [recordData, setRecordData] = useState([]);

  useEffect(() => {
    type == 'edit' ? getRecordData(tableName, pk) : setRecordData(null);
  }, [type, tableName, pk]);

  // getRecordData
  const getRecordData = async (tableName) => {
    setRecordData(null);
    await Axios.get("/api/crud/"+tableName+"/"+pk).then(
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

  // updateTableRow
  const updateTableRow = async (tableName, record, pk) => {
    setLoading(true);
    await Axios.put("/api/crud/"+tableName+"/"+pk, {  
        headers: { 
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        data: record
      }).then( 
      (res) => {
        getRecordData(tableName, pk);
        message.success('Erfolgreich gespeichert.');
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
      await Axios.post("/api/crud/"+tableName, {  
          headers: { 
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          data: record          
        }).then( 
        (res) => {
          getRecordData(tableName, pk);
          message.success('Erfolgreich gespeichert.');
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
    handleClose();
  };

  const layout = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 }
  };
  const layoutpage = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 }
  };

  const options = {
    autoIndent: 'full',
    contextmenu: true,
    //fontFamily: 'monospace',
    //fontSize: 13,
    //lineHeight: 24,
    hideCursorInOverviewRuler: true,
    matchBrackets: 'always',
    minimap: {
      enabled: false,
    },
    scrollbar: {
      horizontalSliderSize: 2,
      verticalSliderSize: 10,
    },
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    automaticLayout: true,
  }; 


  const handleChange =(event) =>{
    const {name, value} = event.target;
    console.log("handleChange - name: " + name + " / value: " + value);
    setRecordData({...recordData, [name]: value}); // TODO: updating existing fields doesn't work ?!
  }

  return (
    <React.Fragment>
      <Modal
            title={name}
            open={true}
            onOk={handleOk}
            onCancel={handleClose}
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
              <Button key="2" htmlType="button" onClick={handleClose} >Abbrechen</Button>,
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