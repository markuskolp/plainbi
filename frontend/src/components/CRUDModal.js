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
import SelectLookup from './SelectLookup';
import MarkdownEditor from './MarkdownEditor';
const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Text, Link } = Typography;

const CRUDModal = ({ tableColumns, handleClose }) => {
    
  const [loading, setLoading] = useState(true);

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
                          <SelectLookup lookupid={column.lookup}/>
                        ) : column.ui === "hidden" ? (
                          ""
                        ) : column.ui === "numberinput" ? (
                          <InputNumber />
                        ) : column.ui === "textarea_markdown" ? (
                          <MarkdownEditor />
                        ) : column.ui === "textarea" ? (
                          <TextArea rows={6} />
                        ) : column.ui === "textarea_sql" ? (
                          <div class="monaco-editor-wrapper">
                            <MonacoEditor
                            //width="800"
                            height="300"
                            language="sql"
                            theme="vs-light"
                            //value={code}
                            options={options}
                            //onChange={::this.onChange}
                            //editorDidMount={::this.editorDidMount}
                            />
                          </div>
                        ) : column.ui === "textarea_json" ? (
                          <div class="monaco-editor-wrapper">
                            <MonacoEditor
                            //width="800"
                            height="300"
                            language="json"
                            theme="vs-light"
                            //value={code}
                            options={options}
                            //onChange={::this.onChange}
                            //editorDidMount={::this.editorDidMount}
                            />
                          </div>
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

      //import remarkGfm from 'remark-gfm';
      //remarkPlugins={[remarkGfm]} />