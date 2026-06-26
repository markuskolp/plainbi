import React, { useState, useEffect, useRef } from 'react';
import { Button, Input, Space, Breadcrumb, Tooltip } from 'antd';
import { PlusOutlined, DownloadOutlined, PauseOutlined, UndoOutlined,
         UnorderedListOutlined, CalendarOutlined } from "@ant-design/icons";

const CRUDToolbar = ({
  allowedActions, externalActions, onNew, onDownload, callRestAPI, callStoredProcedure,
  onColumnSettings, onReset, isDirty,
  filter, onSearch, breadcrumbItems,
  view, onViewChange,
}) => {
  const [localValue, setLocalValue] = useState(filter ?? '');
  const debounceRef = useRef(null);

  // Externer Reset oder Seitenwechsel: Input synchronisieren
  useEffect(() => { setLocalValue(filter ?? ''); }, [filter]);

  const handleChange = (e) => {
    const v = e.target.value;
    setLocalValue(v);
    // Clear-X löst onChange mit click-Event aus, onSearch übernimmt dann selbst
    if (e.nativeEvent?.type === 'click') return;
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => onSearch(v), 600);
  };

  const handleSearch = (v) => {
    clearTimeout(debounceRef.current);
    onSearch(v);
  };

  return (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
    <Space direction="vertical" size={4}>
      {breadcrumbItems && <Breadcrumb items={breadcrumbItems} />}
      <Input.Search
        placeholder="Suche ..."
        value={localValue}
        onSearch={handleSearch}
        onChange={handleChange}
        style={{ width: 400 }}
        allowClear
      />
    </Space>
    <Space>
      {allowedActions.includes("view_calendar") && <>
        <Button type={view === 'table' ? 'primary' : 'default'} icon={<UnorderedListOutlined />} onClick={() => onViewChange('table')} />
        <Button type={view === 'calendar' ? 'primary' : 'default'} icon={<CalendarOutlined />} onClick={() => onViewChange('calendar')} />
      </>}
      <Tooltip title="Spaltenauswahl und Reihenfolge">
        <Button icon={<PauseOutlined />} onClick={onColumnSettings}>Spalten</Button>
      </Tooltip>
      {isDirty && (
        <Tooltip title="Hiermit werden alle getroffenen Einstellungen zurückgesetzt (Suche, Filter, Sortierung, Spaltenauswahl, -reihenfolge, -breiten)">
          <Button icon={<UndoOutlined />} onClick={onReset} style={{ color: '#fa8c16', borderColor: '#fa8c16' }}>Zurücksetzen</Button>
        </Tooltip>
      )}
      {allowedActions.includes("export_excel") &&
        <Button icon={<DownloadOutlined />} onClick={() => onDownload("XLSX")}>Excel</Button>}
      {externalActions && externalActions.map((ea) => (
        ea.type === 'call_rest_api' && (ea.position === 'summary' || !ea.position) ?
          <Tooltip key={ea.id} title={ea.tooltip || ''}>
            <Button onClick={() => callRestAPI(ea.id, ea.wait_repeat_in_ms, ea.url, ea.body, ea.token)}>{ea.label}</Button>
          </Tooltip> : null
      ))}
      {externalActions && externalActions.map((ea) => (
        ea.type === 'call_stored_procedure' && (ea.position === 'summary' || !ea.position) ?
          <Tooltip key={ea.id} title={ea.tooltip || ''}>
            <Button onClick={() => callStoredProcedure(ea.id, ea.wait_repeat_in_ms, ea.name, ea.body)}>{ea.label}</Button>
          </Tooltip> : null
      ))}
      {allowedActions.includes("create") &&
        <Button onClick={onNew} type="primary" icon={<PlusOutlined />}>Neu</Button>}
    </Space>
  </div>
  );
};

export default CRUDToolbar;
