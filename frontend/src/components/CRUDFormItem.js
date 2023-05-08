import React from "react";
import { useState, useEffect } from "react";
import {
  Typography,
  Layout,
  Switch,
  Form,
  Input,
  InputNumber,
  DatePicker,
} from "antd";
import MonacoEditor from 'react-monaco-editor';
import SelectLookup from './SelectLookup';
import MarkdownEditor from './MarkdownEditor';
import dayjs from 'dayjs';
const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Text, Link } = Typography;


const CRUDFormItem = ({ name, label, required, editable, lookupid, ui, defaultValue }) => {

  const dateFormat = 'YYYY-MM-DD';

  return (                    
            <React.Fragment>
              <Form.Item
                name={name}
                label={label}
                rules={[{ required: (required === "true" ? true : false) }]}
              >
                {!editable ? (
                  <Text>{defaultValue}</Text>
                ) : ui === "lookup" ? (
                  <SelectLookup lookupid={lookup} defaultValue={defaultValue}/>
                ) : ui === "hidden" ? (
                  ""
                ) : ui === "numberinput" ? (
                  <InputNumber defaultValue={defaultValue}/>
                ) : ui === "textarea_markdown" ? (
                  <MarkdownEditor defaultValue={defaultValue} />
                ) : ui === "textarea" ? (
                  <TextArea rows={6} defaultValue={defaultValue}/>
                ) : ui === "textarea_sql" ? (
                  <div class="monaco-editor-wrapper">
                    <MonacoEditor
                    //width="800"
                    height="300"
                    language="sql"
                    theme="vs-light"
                    value={defaultValue}
                    options={options}
                    //onChange={::this.onChange}
                    //editorDidMount={::this.editorDidMount}
                    />
                  </div>
                ) : ui === "textarea_json" ? (
                  <div class="monaco-editor-wrapper">
                    <MonacoEditor
                    //width="800"
                    height="300"
                    language="json"
                    theme="vs-light"
                    value={defaultValue}
                    options={options}
                    //onChange={::this.onChange}
                    //editorDidMount={::this.editorDidMount}
                    />
                  </div>
                ) : ui === "password" ? (
                  <Input.Password defaultValue={defaultValue}/>
                ) : ui === "email" ? (
                  <Input defaultValue={defaultValue}/>
                ) : ui === "textinput" ? (
                  <Input defaultValue={defaultValue}/> 
                ) : ui === "datepicker" ? (
                  defaultValue ?
                  <DatePicker defaultValue={dayjs(defaultValue,{dateFormat})} format={dateFormat}  />
                  :
                  <DatePicker format={dateFormat}  />
                ) : ui === "switch" ? (
                  <Switch defaultChecked={defaultValue}/>
                ) : ui === "label" ? (
                  <Text>{defaultValue}</Text>
                ) : (
                  <Text>{defaultValue}</Text>
                )}
              </Form.Item>
            </React.Fragment>
            
    )

};

export default CRUDFormItem;
