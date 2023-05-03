import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import {
  Table,
  Button,
  Typography,
  Layout,
  Menu,
  Modal,
  Switch,
  Form,
  Input,
  Select,
  InputNumber,
  DatePicker,
  Space,
  Popconfirm,
  message
} from "antd";
import MonacoEditor from 'react-monaco-editor';
const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Text, Link } = Typography;

const CRUDModal = ({ tableColumns, handleClose }) => {
    
  const [loading, setLoading] = useState(true);
  const [lookupData, setLookupData] = useState([]);

  /*
    const [columnItems, setColumnItems] = useState([]);
    const [columnItemsForSummary, setColumnItemsForSummary] = useState([]);
    */

  useEffect(() => {

    tableColumns.map((column) => {
            if (column.ui === "lookup" ) {
              console.log(column.column_name + ' ' + column.ui + ' ' + column.lookup);
              getLookupData(column.lookup);
            }
    }
    );
    
   //console.log("test: " + getLookup("output_format"));
    
  }, [tableColumns]);

  const getLookupData = async (lookupid) => {
    //    async function getLookupData(lookupid) {
        console.log('fetching lookup', lookupid);
        await Axios.get("/api/data/lookup/"+lookupid+".json").then(
          (res) => {
            console.log("lookupData: " + JSON.stringify(res));
            setLookupData( res.data.map((row) => ({
                value: row.r,
                label: row.d
              }))
            );
            /*
            setLookupData( {
              id: lookupid,
              values: 
              res.data.map((row) => ({
                value: row.r,
                label: row.d
              }))
            }
            );
            */
            
            setLoading(false);
            console.log("lookupData: " + JSON.stringify(lookupData));
          }
        )
      };

      /*
    const getLookup = async (lookupid) =>  {
      console.log("getLookup: " + lookupid);
      await Axios.get("/api/data/lookup/"+lookupid+".json").then(
        (res) => {
          console.log("getLookup: " + JSON.stringify(res.data));
          return res.data.map((row) => ({
              value: row.r,
              label: row.d
            }))
        }
        )
    };
    */

  const handleOk = () => {
    // todo: add or update to API
    // if all ok, then close modal
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
                {tableColumns && tableColumns.map((column) => {
                  return (
                    <React.Fragment>
                      <Form.Item
                        name={column.column_name}
                        label={column.column_label}
                        rules={[{ required: column.required }]}
                      >
                        {!column.editable ? (
                          <Text>...</Text>
                        ) : column.ui === "lookup" ? (
                          <Select
                            placeholder="bitte auswählen ..."
                            allowClear
                            showSearch
                            options={lookupData}
                              /*[
                              {
                                value: "a",
                                label: ""
                              },
                              {
                                value: "b",
                                label: ""
                              },
                              {
                                value: "...",
                                label: "..."
                              }
                              ]
                          }*/
                          />
                        ) : column.ui === "hidden" ? (
                          ""
                        ) : column.ui === "numberinput" ? (
                          <InputNumber />
                        ) : column.ui === "textarea" ? (
                          <TextArea rows={6} />
                        ) : column.ui === "textarea_sql" ? (
                          <MonacoEditor
                            //width="800"
                            //height="600"
                            language="sql"
                            theme="vs-light"
                            //value={code}
                            //options={options}
                            //onChange={::this.onChange}
                            //editorDidMount={::this.editorDidMount}
                          />
                        ) : column.ui === "password" ? (
                          <Input.Password />
                        ) : column.ui === "email" ? (
                          <Input />
                        ) : column.ui === "textinput" ? (
                          <Input />
                        ) : column.ui === "datepicker" ? (
                          <DatePicker />
                        ) : column.ui === "switch" ? (
                          <Switch />
                        ) : (
                          <Text>?</Text>
                        )}
                      </Form.Item>
                    </React.Fragment>
                  );
                })}
              </Form>



          </Modal>

    </React.Fragment>
  );

};

export default CRUDModal;
