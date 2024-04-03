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
  Space
} from "antd";
import MonacoEditor from 'react-monaco-editor';
import SelectLookup from './SelectLookup';
import MarkdownEditor from './MarkdownEditor';
import dayjs from 'dayjs';
import ImageUpload from "./ImageUpload";
const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Text, Link } = Typography;


const CRUDFormItem = ({ type, name, label, required, isprimarykey, editable, lookupid, ui, defaultValue, onChange, tooltip, token, multiple }) => {

  const dateFormat = 'YYYY-MM-DD';
  const [currentvalue, setCurrentvalue] = useState(defaultValue);

  const handleChange = (e) => {
    //const emuEvent = { "target": { "key": e.target.name, "value": e.target.value}} // emulate event.target.name/.value object
    //console.log(emuEvent);
    //onChange("name", "aa"); 
    setCurrentvalue(e.target.value);
    onChange(e.target.name, e.target.value); 
   }

   const handleDatePickerChange = (date, dateString) => {
    //console.log("handleDatePickerChange - name: " + name + " / value: " + dateString);
    //const emuEvent = { "target": { "name": name, "value": dateString}} // emulate event.target.name/.value object
    //console.log(emuEvent);
    onChange(name, dateString); 
 }

 const handleNumberInputChange = (value) => {
  //const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
  //console.log(emuEvent);
  onChange(name, value); 
 }

 /*
 const handleMarkdownChange = (value) => {
  const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
  console.log(emuEvent);
  onChange(emuEvent); 
 }

 const handleTextAreaChange = (value) => {
  const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
  console.log(emuEvent);
  onChange(emuEvent); 
 }
 */

const handleMonacoEditorChange = (value,e) => {
  //const emuEvent = { "target": { "name": name, "value": value}} // emulate event.target.name/.value object
  //console.log(emuEvent);
  //onChange("sql_query", "ss"); 
  onChange(name, value); 
}

const handleSwitchChange = (checked, e) => {
  //const emuEvent = { "target": { "name": name, "value": checked}} // emulate event.target.name/.value object
  //console.log(emuEvent);
  onChange(name, checked); 
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
                tooltip={tooltip}
              >
                {
                  ((editable.toString() === "false" || (isprimarykey.toString() === "true") && type != "new") && ui === "lookupn") ? (
                  <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} allowNewValues="true" multiple={(multiple === "true" ? true : false)}/>
                ) : ((editable.toString() === "false" || (isprimarykey.toString() === "true") && type != "new") && ui === "lookup") ? (
                  <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} multiple={(multiple === "true" ? true : false)}/>
                ) : (editable.toString() === "false" || (isprimarykey.toString() === "true") && type != "new") ? (
                  <Text>{defaultValue}</Text>
                ) : ui === "lookupn" ? (
                  <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} token={token} allowNewValues="true" multiple={(multiple === "true" ? true : false)}/>
                ) : ui === "lookup" ? (
                  <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} token={token} multiple={(multiple === "true" ? true : false)}/>
                ) : ui === "hidden" ? (
                  ""
                ) : ui === "numberinput" ? (
                  <InputNumber name={name} defaultValue={defaultValue} onInput={(val) => handleNumberInputChange(val)} onStep={(val) => handleNumberInputChange(val)}/>
                ) : ui === "textarea_markdown" ? (
                  <MarkdownEditor name={name} defaultValue={defaultValue} onChange={handleChange}/>
                ) : ui === "textarea_base64" ? (
                  <Space direction="vertical" style={{width:"100%"}} >
                    <TextArea name={name} rows={6} defaultValue={defaultValue} onChange={handleChange}/> 
                    <img src={`data:image/png;base64,${currentvalue}`} />
                    { /*<ImageUpload /> */ }
                  </Space>
                ) : ui === "textarea" ? (
                  <TextArea name={name} rows={6} defaultValue={defaultValue} onChange={handleChange}/> //((e) => handleTextAreaChange(e.target.value))}/>
                ) : ui === "textarea_sql" ? (
                  <div className="monaco-editor-wrapper">
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
                  <div className="monaco-editor-wrapper">
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
                ) : ui === "password_nomem" ? (
                  <Input.Password name={name} defaultValue={defaultValue} onChange={handleChange} autocomplete="off"/>
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
                  <Switch name={name} defaultChecked={defaultValue} onChange={handleSwitchChange}/>
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
