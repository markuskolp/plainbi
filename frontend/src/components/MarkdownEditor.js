import React from "react";
import { useState } from "react";
import ReactMarkdown from 'react-markdown';
import { Input } from "antd";
const { TextArea } = Input;

//TODO: set initial value
//TODO: handle callback (change of value in textarea)

const MarkdownEditor = ({ name, defaultValue, callback, onChange }) => {

  const [markdown, setMarkdown] = useState('');

  const handleChange = (e) => {
    setMarkdown(e.target.value);
    const emuEvent = { "target": { "name": name, "value": e.target.value}} // emulate event.target.name/.value object
    console.log("MarkdownEditor - Textarea change: " + JSON.stringify(emuEvent));
    onChange(emuEvent); 
  };
  

  return (
        <div class='markdowncontainer'>
          <div class='markdowncontainer_editor'>
            <TextArea rows={6} 
              onChange={handleChange}
              placeholder="Für die Vorschau, bitte einen Txt eingeben."
              defaultValue={defaultValue}
              name={name}
            />
          </div>
          <div class='markdowncontainer_result'>
            <ReactMarkdown children={markdown}
            /> 
          </div>
        </div>
    )

};

export default MarkdownEditor;