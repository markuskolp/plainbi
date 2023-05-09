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

 const handleNumberInputChange = (value) => {
  const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
  console.log(emuEvent);
  handleChange(emuEvent); 
 }

const handleMonacoEditorChange = (value, e) => {
  const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
  console.log(emuEvent);
  handleChange(emuEvent); 
}

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
              <Form.Item
                name={name}
                label={label}
                rules={[{ required: (required === "true" ? true : false) }]}
              >
                {editable === "false" ? (
                  <Text>{defaultValue}</Text>
                ) : ui === "lookup" ? (
                  <SelectLookup name={name} lookupid={lookup} defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "hidden" ? (
                  ""
                ) : ui === "numberinput" ? (
                  <InputNumber name={name} defaultValue={defaultValue} onInput={(val) => handleNumberInputChange(val)} onStep={(val) => handleNumberInputChange(val)}/>
                ) : ui === "textarea_markdown" ? (
                  <MarkdownEditor name={name} defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "textarea" ? (
                  <TextArea name={name} rows={6} defaultValue={defaultValue} onChange={handleChange}/>
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
                    onChange={handleMonacoEditorChange}
                    name={name}
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
                    onChange={handleMonacoEditorChange}
                    name={name}
                    //editorDidMount={::this.editorDidMount}
                    />
                  </div>
                ) : ui === "password" ? (
                  <Input.Password name={name} defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "email" ? (
                  <Input name={name} defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "textinput" ? (
                  <Input name={name} defaultValue={defaultValue} onChange={handleChange}/> 
                ) : ui === "datepicker" ? (
                  defaultValue ?
                  <DatePicker defaultValue={dayjs(defaultValue,{dateFormat})} format={dateFormat} onChange={handleDatePickerChange} /> 
                  :
                  <DatePicker format={dateFormat} onChange={handleDatePickerChange} /> 
                ) : ui === "switch" ? (
                  <Switch name={name} defaultChecked={defaultValue} onChange={handleChange}/>
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
