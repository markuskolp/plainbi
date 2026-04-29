import { useState } from "react";
import ReactMarkdown from 'react-markdown';
import { Input } from "antd";
const { TextArea } = Input;

const MarkdownEditor = ({ name, defaultValue, onChange }) => {
  const [markdown, setMarkdown] = useState(defaultValue || '');

  const handleChange = (e) => {
    setMarkdown(e.target.value);
    onChange({ target: { name, value: e.target.value } });
  };

  return (
    <div className='markdowncontainer'>
      <div className='markdowncontainer_editor'>
        <TextArea rows={6} onChange={handleChange} placeholder="Für die Vorschau, bitte einen Txt eingeben." defaultValue={defaultValue} name={name} />
      </div>
      <div className='markdowncontainer_result'>
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </div>
    </div>
  );
};

export default MarkdownEditor;
