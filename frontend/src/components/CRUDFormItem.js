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
  Modal,
  message
} from "antd";
import Editor from '@monaco-editor/react';
import { FullscreenOutlined } from '@ant-design/icons';
import SelectLookup from './SelectLookup';
import MarkdownEditor from './MarkdownEditor';
import { isTrue } from '../utils/dataUtils';
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
  fixedOverflowWidgets: true,
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
  fixedOverflowWidgets: true,
};

const CRUDFormItem = ({ type, name, label, required, isprimarykey, editable, lookupid, ui, defaultValue, onChange, tooltip, token, multiple, hasError }) => {
  const dateFormat = 'YYYY-MM-DD';
  const datetimeFormat = 'YYYY-MM-DD HH:mm';
  const [currentvalue, setCurrentvalue] = useState(defaultValue);
  const isMultiple = isTrue(multiple);
  const editorRef = useRef(null);
  const isExternalUpdate = useRef(false);
  const [sqlFullscreen, setSqlFullscreen] = useState(false);
  const fullscreenEditorRef = useRef(null);
  const sqlCurrentValue = useRef(defaultValue ?? '');

  // Force Monaco to recalculate positions after the Modal open animation completes
  useEffect(() => {
    const handler = () => editorRef.current?.layout();
    window.addEventListener('plainbi:modal-ready', handler);
    return () => window.removeEventListener('plainbi:modal-ready', handler);
  }, []);

  // Sync fullscreen editor value on every open (onMount only fires on first open)
  useEffect(() => {
    if (sqlFullscreen && fullscreenEditorRef.current) {
      fullscreenEditorRef.current.setValue(sqlCurrentValue.current);
    }
  }, [sqlFullscreen]);

  // Sync Monaco editor when real record data arrives (loading starts with defaultValue="")
  useEffect(() => {
    if (!editorRef.current) return;
    const incoming = defaultValue ?? '';
    if (editorRef.current.getValue() !== incoming) {
      isExternalUpdate.current = true;
      editorRef.current.setValue(incoming);
      isExternalUpdate.current = false;
      sqlCurrentValue.current = incoming;
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
    sqlCurrentValue.current = value;
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
      sqlCurrentValue.current = formatted;
      onChange(name, formatted);
      message.success('JSON formatiert.');
    } catch (e) {
      message.error('Ungültiges JSON: ' + e.message);
    }
  };

  const openSqlFullscreen = () => setSqlFullscreen(true);

  const applySqlFullscreen = () => {
    if (fullscreenEditorRef.current && editorRef.current) {
      const value = fullscreenEditorRef.current.getValue();
      isExternalUpdate.current = true;
      editorRef.current.setValue(value);
      isExternalUpdate.current = false;
      onChange(name, value);
    }
    setSqlFullscreen(false);
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

  const isReadOnly = !isTrue(editable) || (isTrue(isprimarykey) && type !== "new" && type !== "duplicate");

  const renderField = () => {
    if (isReadOnly) {
      if (ui === "lookupn")
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} allowNewValues="true" multiple={isMultiple} />;
      if (ui === "lookup")
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} multiple={isMultiple} />;
      if (ui === "textarea_sql")
        return (
          <Space direction="vertical" style={{ width: "100%" }}>
            <Button size="small" icon={<FullscreenOutlined />} onClick={openSqlFullscreen}>Vollbild</Button>
            <div style={{ border: '1px solid #d9d9d9', borderRadius: 6, overflow: 'hidden' }}>
              <Editor height={300} language="sql" theme="vs" options={monacoOptionsReadOnly}
                onMount={(editor) => { editorRef.current = editor; isExternalUpdate.current = true; editor.setValue(defaultValue ?? ''); isExternalUpdate.current = false; }} />
            </div>
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
        return <InputNumber name={name} defaultValue={defaultValue} onChange={handleNumberInputChange}
          onKeyDown={(e) => {
            if (e.ctrlKey || e.metaKey) return;
            if (['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(e.key)) return;
            if (/[\d\-.,]/.test(e.key)) return;
            e.preventDefault();
          }}
        />;
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
            <Button size="small" icon={<FullscreenOutlined />} onClick={openSqlFullscreen}>Vollbild</Button>
            <div style={{ border: '1px solid #d9d9d9', borderRadius: 6, overflow: 'hidden' }}>
              <Editor height={300} language="sql" theme="vs" options={monacoOptions} onChange={handleMonacoEditorChange}
                onMount={(editor) => { editorRef.current = editor; isExternalUpdate.current = true; editor.setValue(defaultValue ?? ''); isExternalUpdate.current = false; sqlCurrentValue.current = defaultValue ?? ''; }} />
            </div>
          </Space>
        );
      case "textarea_json":
        return (
          <Space direction="vertical" style={{ width: "100%" }}>
            <Space>
              <Button size="small" onClick={formatJson}>Formatieren</Button>
              <Button size="small" onClick={validateJson}>Validieren</Button>
              <Button size="small" icon={<FullscreenOutlined />} onClick={openSqlFullscreen}>Vollbild</Button>
            </Space>
            <div style={{ border: '1px solid #d9d9d9', borderRadius: 6, overflow: 'hidden' }}>
              <Editor height={300} language="json" theme="vs" options={monacoOptions} onChange={handleMonacoEditorChange}
                onMount={(editor) => { editorRef.current = editor; isExternalUpdate.current = true; editor.setValue(defaultValue ?? ''); isExternalUpdate.current = false; sqlCurrentValue.current = defaultValue ?? ''; }} />
            </div>
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

  const isMonaco = ui === 'textarea_sql' || ui === 'textarea_json';

  if (ui === "hidden") return null;

  return (
    <>
      <Form.Item
        name={isMonaco ? undefined : name}
        label={label}
        rules={isMonaco ? [] : [{ required: isTrue(required) }]}
        tooltip={tooltip}
        validateStatus={hasError ? "error" : ""}
        help={hasError ? "Pflichtfeld" : undefined}
      >
        {renderField()}
      </Form.Item>
      {(ui === "textarea_sql" || ui === "textarea_json") && (
        <Modal
          open={sqlFullscreen}
          onCancel={() => setSqlFullscreen(false)}
          width="95vw"
          style={{ top: '2vh' }}
          styles={{ body: { height: 'calc(92vh - 110px)', padding: 0 } }}
          title={label}
          maskClosable={false}
          footer={isReadOnly ? [
            <Button key="close" onClick={() => setSqlFullscreen(false)}>Schließen</Button>
          ] : [
            <Button key="cancel" onClick={() => setSqlFullscreen(false)}>Abbrechen</Button>,
            <Button key="apply" type="primary" onClick={applySqlFullscreen}>OK</Button>
          ]}
        >
          <Editor
            height="100%"
            language={ui === "textarea_json" ? "json" : "sql"}
            theme="vs"
            options={isReadOnly ? monacoOptionsReadOnly : monacoOptions}
            onMount={(editor) => {
              fullscreenEditorRef.current = editor;
              editor.setValue(sqlCurrentValue.current);
            }}
          />
        </Modal>
      )}
    </>
  );
};

export default CRUDFormItem;
