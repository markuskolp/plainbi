import React from "react";
import { useState } from "react";
import ReactMarkdown from 'react-markdown';
import { Input } from "antd";
const { TextArea } = Input;

//TODO: set initial value
//TODO: handle callback (change of value in textarea)

const MarkdownEditor = ({ initialValue, callback }) => {

  const [markdown, setMarkdown] = useState('');

  const onChange = (e) => {
    console.log('MarkdownEditor - Textarea change:', e.target.value);
    setMarkdown(e.target.value);
  };

  return (
        <div class='markdowncontainer'>
          <div class='markdowncontainer_editor'>
            <TextArea rows={6} 
              onChange={onChange}
              placeholder="Für die Vorschau, bitte einen Txt eingeben."
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
