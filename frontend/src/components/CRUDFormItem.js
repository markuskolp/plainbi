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


const CRUDFormItem = ({ name, label, required, editable, lookupid, ui, defaultValue, handleChange }) => {

  const dateFormat = 'YYYY-MM-DD';

  const handleDatePickerChange = (date, dateString) => {
    //console.log("handleDatePickerChange - name: " + name + " / value: " + dateString);
    const emuEvent = { "target": { "name": name, "value": dateString}} // emulate event.target.name/.value object
    console.log(emuEvent);
    handleChange(emuEvent); 
 }

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
                  <SelectLookup lookupid={lookup} defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "hidden" ? (
                  ""
                ) : ui === "numberinput" ? (
                  <InputNumber defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "textarea_markdown" ? (
                  <MarkdownEditor defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "textarea" ? (
                  <TextArea rows={6} defaultValue={defaultValue} onChange={handleChange}/>
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
                    onChange={handleChange}
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
                    onChange={handleChange}
                    //editorDidMount={::this.editorDidMount}
                    />
                  </div>
                ) : ui === "password" ? (
                  <Input.Password defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "email" ? (
                  <Input defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "textinput" ? (
                  <Input defaultValue={defaultValue} onChange={handleChange}/> 
                ) : ui === "datepicker" ? (
                  defaultValue ?
                  <DatePicker defaultValue={dayjs(defaultValue,{dateFormat})} format={dateFormat} onChange={handleDatePickerChange} /> 
                  :
                  <DatePicker format={dateFormat} onChange={handleDatePickerChange} /> 
                ) : ui === "switch" ? (
                  <Switch defaultChecked={defaultValue} onChange={handleChange}/>
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
