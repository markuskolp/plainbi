import { useState, useEffect } from "react";
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
import { FullscreenOutlined } from '@ant-design/icons';
import SelectLookup from './SelectLookup';
import MarkdownEditor from './MarkdownEditor';
import CodeMirrorEditor from './CodeMirrorEditor';
import { isTrue } from '../utils/dataUtils';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Text } = Typography;

const CRUDFormItem = ({ type, name, label, required, isprimarykey, editable, lookupid, ui, defaultValue, onChange, tooltip, token, multiple, hasError }) => {
  const dateFormat = 'YYYY-MM-DD';
  const datetimeFormat = 'YYYY-MM-DD HH:mm';
  const [currentvalue, setCurrentvalue] = useState(defaultValue);
  const isMultiple = isTrue(multiple);

  const [cmValue, setCmValue] = useState(defaultValue ?? '');
  const [cmFullscreenValue, setCmFullscreenValue] = useState('');
  const [sqlFullscreen, setSqlFullscreen] = useState(false);

  // Sync editor value when record data arrives from API
  useEffect(() => {
    setCmValue(defaultValue ?? '');
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

  const handleCmChange = (value) => {
    setCmValue(value);
    onChange(name, value);
  };

  const handleSwitchChange = (checked) => {
    onChange(name, checked);
  };

  const formatJson = () => {
    try {
      const formatted = JSON.stringify(JSON.parse(cmValue), null, 2);
      setCmValue(formatted);
      onChange(name, formatted);
      message.success('JSON formatiert.');
    } catch (e) {
      message.error('Ungültiges JSON: ' + e.message);
    }
  };

  const validateJson = () => {
    try {
      JSON.parse(cmValue);
      message.success('JSON ist gültig.');
    } catch (e) {
      message.error('Ungültiges JSON: ' + e.message);
    }
  };

  const openSqlFullscreen = () => {
    setCmFullscreenValue(cmValue);
    setSqlFullscreen(true);
  };

  const applySqlFullscreen = () => {
    setCmValue(cmFullscreenValue);
    onChange(name, cmFullscreenValue);
    setSqlFullscreen(false);
  };

  const isReadOnly = !isTrue(editable) || (isTrue(isprimarykey) && type !== "new" && type !== "duplicate");
  const isCodeMirror = ui === 'textarea_sql' || ui === 'textarea_json';

  if (ui === "hidden") return null;

  const renderField = () => {
    if (isReadOnly) {
      if (ui === "lookupn")
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} allowNewValues="true" multiple={isMultiple} />;
      if (ui === "lookup")
        return <SelectLookup name={name} lookupid={lookupid} defaultValue={defaultValue} onChange={handleChange} disabled="true" token={token} multiple={isMultiple} />;
      if (ui === "textarea_sql" || ui === "textarea_json")
        return (
          <Space direction="vertical" style={{ width: "100%" }}>
            <Button size="small" icon={<FullscreenOutlined />} onClick={openSqlFullscreen}>Vollbild</Button>
            <div style={{ border: '1px solid #d9d9d9', borderRadius: 6, overflow: 'hidden' }}>
              <CodeMirrorEditor value={cmValue} language={ui === "textarea_json" ? "json" : "sql"} readOnly height={300} />
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
              <CodeMirrorEditor value={cmValue} onChange={handleCmChange} language="sql" height={300} />
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
              <CodeMirrorEditor value={cmValue} onChange={handleCmChange} language="json" height={300} />
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

  return (
    <>
      <Form.Item
        name={isCodeMirror ? undefined : name}
        label={label}
        rules={isCodeMirror ? [] : [{ required: isTrue(required) }]}
        tooltip={tooltip}
        validateStatus={hasError ? "error" : ""}
        help={hasError ? "Pflichtfeld" : undefined}
      >
        {renderField()}
      </Form.Item>
      {isCodeMirror && (
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
          <div style={{ height: '100%', overflow: 'hidden' }}>
            <CodeMirrorEditor
              value={cmFullscreenValue}
              onChange={setCmFullscreenValue}
              language={ui === "textarea_json" ? "json" : "sql"}
              readOnly={isReadOnly}
              height="100%"
            />
          </div>
        </Modal>
      )}
    </>
  );
};

export default CRUDFormItem;
