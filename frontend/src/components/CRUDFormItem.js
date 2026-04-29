import { useState, useEffect, useRef } from "react";
import {
  Typography,
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

const { TextArea } = Input;
const { Text } = Typography;

const monacoOptions = {
  autoIndent: 'full',
  contextmenu: true,
  hideCursorInOverviewRuler: true,
  matchBrackets: 'always',
  minimap: { enabled: false },
  scrollbar: { horizontalSliderSize: 2, verticalSliderSize: 10 },
  selectOnLineNumbers: true,
  roundedSelection: false,
  readOnly: false,
  cursorStyle: 'line',
  automaticLayout: true,
};

const CRUDFormItem = ({ type, name, label, required, isprimarykey, editable, lookupid, ui, defaultValue, onChange, tooltip, token, multiple }) => {
  const dateFormat = 'YYYY-MM-DD';
  const datetimeFormat = 'YYYY-MM-DD HH:mm';
  const [currentvalue, setCurrentvalue] = useState(defaultValue);
  const isMultiple = multiple === "true";
  const editorRef = useRef(null);
  const isExternalUpdate = useRef(false);

  // Sync Monaco editor when real record data arrives (loading starts with defaultValue="")
  useEffect(() => {
    if (!editorRef.current) return;
    const incoming = defaultValue ?? '';
    if (editorRef.current.getValue() !== incoming) {
      isExternalUpdate.current = true;
      editorRef.current.setValue(incoming);
      isExternalUpdate.current = false;
    }
  }, [defaultValue]);

  const handleChange = (e) => {
    setCurrentvalue(e.target.value);
    onChange(e.target.name, e.target.value);
  };

  const handleDatePickerChange = (_date, dateString) => {
    onChange(name, dateString);
  };

  const handleNumberInputChange = (value) => {
    onChange(name, value);
  };

  const handleMonacoEditorChange = (value) => {
    if (isExternalUpdate.current) return;
    onChange(name, value);
  };

  const handleSwitchChange = (checked) => {
    onChange(name, checked);
  };

  const isReadOnly = editable.toString() === "false" || ((isprimarykey.toString() === "true") && type !== "new" && type !== "duplicate");

  const renderField = () => {
    if (isReadOnly) {
      if (ui === "lookupn")
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} allowNewValues="true" multiple={isMultiple} />;
      if (ui === "lookup")
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} multiple={isMultiple} />;
      return <Text>{defaultValue}</Text>;
    }

    switch (ui) {
      case "lookupn":
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} token={token} allowNewValues="true" multiple={isMultiple} />;
      case "lookup":
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} token={token} multiple={isMultiple} />;
      case "hidden":
        return "";
      case "numberinput":
        return <InputNumber name={name} defaultValue={defaultValue} onChange={handleNumberInputChange} />;
      case "textarea_markdown":
        return <MarkdownEditor name={name} defaultValue={defaultValue} onChange={handleChange} />;
      case "textarea_base64":
        return (
          <Space direction="vertical" style={{ width: "100%" }}>
            <TextArea name={name} rows={6} defaultValue={defaultValue} onChange={handleChange} />
            <img src={`data:image/png;base64,${currentvalue}`} alt="" />
          </Space>
        );
      case "textarea":
        return <TextArea name={name} rows={6} defaultValue={defaultValue} onChange={handleChange} />;
      case "textarea_sql":
        return (
          <div className="monaco-editor-wrapper">
            <MonacoEditor height="300" language="sql" theme="vs-light" options={monacoOptions} onChange={handleMonacoEditorChange}
              editorDidMount={(editor) => { editorRef.current = editor; isExternalUpdate.current = true; editor.setValue(defaultValue ?? ''); isExternalUpdate.current = false; }} />
          </div>
        );
      case "textarea_json":
        return (
          <div className="monaco-editor-wrapper">
            <MonacoEditor height="300" language="json" theme="vs-light" options={monacoOptions} onChange={handleMonacoEditorChange}
              editorDidMount={(editor) => { editorRef.current = editor; isExternalUpdate.current = true; editor.setValue(defaultValue ?? ''); isExternalUpdate.current = false; }} />
          </div>
        );
      case "password_nomem":
        return <Input.Password name={name} defaultValue={defaultValue} onChange={handleChange} autoComplete="off" />;
      case "password":
        return <Input.Password name={name} defaultValue={defaultValue} onChange={handleChange} />;
      case "email":
      case "textinput":
        return <Input name={name} defaultValue={defaultValue} onChange={handleChange} />;
      case "datepicker":
        return defaultValue
          ? <DatePicker defaultValue={dayjs(defaultValue, dateFormat)} format={dateFormat} onChange={handleDatePickerChange} />
          : <DatePicker format={dateFormat} onChange={handleDatePickerChange} />;
      case "datetimepicker":
        return defaultValue
          ? <DatePicker showTime={{ format: "HH:mm" }} defaultValue={dayjs(defaultValue, datetimeFormat)} format={datetimeFormat} onChange={handleDatePickerChange} />
          : <DatePicker showTime={{ format: "HH:mm" }} format={datetimeFormat} onChange={handleDatePickerChange} />;
      case "switch":
        return <Switch name={name} defaultChecked={defaultValue} onChange={handleSwitchChange} />;
      default:
        return <Text>{defaultValue}</Text>;
    }
  };

  return (
    <Form.Item
      name={name}
      label={label}
      rules={[{ required: required === "true" }]}
      tooltip={tooltip}
    >
      {renderField()}
    </Form.Item>
  );
};

export default CRUDFormItem;
