import { useState, useEffect, useRef } from "react";
import {
  Typography,
  Switch,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Space,
  Button,
  message
} from "antd";
import Editor from '@monaco-editor/react';
import { ExpandOutlined, CompressOutlined } from '@ant-design/icons';
import SelectLookup from './SelectLookup';
import MarkdownEditor from './MarkdownEditor';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Text } = Typography;

const monacoOptionsReadOnly = {
  hideCursorInOverviewRuler: true,
  minimap: { enabled: false },
  scrollbar: { horizontalSliderSize: 2, verticalSliderSize: 10 },
  readOnly: true,
  automaticLayout: true,
  lineNumbers: 'on',
};

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
  const [editorExpanded, setEditorExpanded] = useState(false);
  const editorHeight = editorExpanded ? 600 : 300;

  // Force Monaco to recalculate positions after the Modal open animation completes
  useEffect(() => {
    const handler = () => editorRef.current?.layout();
    window.addEventListener('plainbi:modal-ready', handler);
    return () => window.removeEventListener('plainbi:modal-ready', handler);
  }, []);

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

  const formatJson = () => {
    if (!editorRef.current) return;
    try {
      const formatted = JSON.stringify(JSON.parse(editorRef.current.getValue()), null, 2);
      isExternalUpdate.current = true;
      editorRef.current.setValue(formatted);
      isExternalUpdate.current = false;
      onChange(name, formatted);
      message.success('JSON formatiert.');
    } catch (e) {
      message.error('Ungültiges JSON: ' + e.message);
    }
  };

  const validateJson = () => {
    if (!editorRef.current) return;
    try {
      JSON.parse(editorRef.current.getValue());
      message.success('JSON ist gültig.');
    } catch (e) {
      message.error('Ungültiges JSON: ' + e.message);
    }
  };

  const isReadOnly = editable.toString() === "false" || ((isprimarykey.toString() === "true") && type !== "new" && type !== "duplicate");

  const renderField = () => {
    if (isReadOnly) {
      if (ui === "lookupn")
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} allowNewValues="true" multiple={isMultiple} />;
      if (ui === "lookup")
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} multiple={isMultiple} />;
      if (ui === "textarea_sql")
        return (
          <Space direction="vertical" style={{ width: "100%" }}>
            <Button size="small" icon={editorExpanded ? <CompressOutlined /> : <ExpandOutlined />} onClick={() => setEditorExpanded(e => !e)}>
              {editorExpanded ? 'Verkleinern' : 'Vergrößern'}
            </Button>
            <Editor height={editorHeight} language="sql" theme="vs" options={monacoOptionsReadOnly}
              onMount={(editor) => { editorRef.current = editor; isExternalUpdate.current = true; editor.setValue(defaultValue ?? ''); isExternalUpdate.current = false; }} />
          </Space>
        );
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
          <Space direction="vertical" style={{ width: "100%" }}>
            <Button size="small" icon={editorExpanded ? <CompressOutlined /> : <ExpandOutlined />} onClick={() => setEditorExpanded(e => !e)}>
              {editorExpanded ? 'Verkleinern' : 'Vergrößern'}
            </Button>
            <Editor height={editorHeight} language="sql" theme="vs" options={monacoOptions} onChange={handleMonacoEditorChange}
              onMount={(editor) => { editorRef.current = editor; isExternalUpdate.current = true; editor.setValue(defaultValue ?? ''); isExternalUpdate.current = false; }} />
          </Space>
        );
      case "textarea_json":
        return (
          <Space direction="vertical" style={{ width: "100%" }}>
            <Space>
              <Button size="small" onClick={formatJson}>Formatieren</Button>
              <Button size="small" onClick={validateJson}>Validieren</Button>
              <Button size="small" icon={editorExpanded ? <CompressOutlined /> : <ExpandOutlined />} onClick={() => setEditorExpanded(e => !e)}>
                {editorExpanded ? 'Verkleinern' : 'Vergrößern'}
              </Button>
            </Space>
            <Editor height={editorHeight} language="json" theme="vs" options={monacoOptions} onChange={handleMonacoEditorChange}
              onMount={(editor) => { editorRef.current = editor; isExternalUpdate.current = true; editor.setValue(defaultValue ?? ''); isExternalUpdate.current = false; }} />
          </Space>
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
