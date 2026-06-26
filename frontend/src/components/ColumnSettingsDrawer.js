import React, { useState, useRef } from 'react';
import { Drawer, Checkbox, Button, Tooltip } from 'antd';
import { HolderOutlined, EyeOutlined } from '@ant-design/icons';

const ColumnSettingsDrawer = ({ open, onClose, tableColumns, colSettings, onChange }) => {
  const [items, setItems] = useState(colSettings);
  const dragIndex = useRef(null);

  // sync wenn colSettings von außen wechselt (z.B. nach Reset)
  React.useEffect(() => { setItems(colSettings); }, [colSettings]);

  const getLabel = (key) => tableColumns.find(c => c.column_name === key)?.column_label || key;

  const toggleVisible = (key) => {
    const next = items.map(i => i.key === key ? { ...i, visible: !i.visible } : i);
    setItems(next);
    onChange(next);
  };

  const showAll = () => {
    const next = items.map(i => ({ ...i, visible: true }));
    setItems(next);
    onChange(next);
  };

  // HTML5 Drag & Drop für Reihenfolge
  const onDragStart = (e, idx) => {
    dragIndex.current = idx;
    e.dataTransfer.effectAllowed = 'move';
  };

  const onDragOver = (e, idx) => {
    e.preventDefault();
    if (dragIndex.current === idx) return;
    const next = [...items];
    const [moved] = next.splice(dragIndex.current, 1);
    next.splice(idx, 0, moved);
    dragIndex.current = idx;
    setItems(next);
  };

  const onDragEnd = () => {
    dragIndex.current = null;
    onChange(items);
  };

  const allVisible = items.every(i => i.visible);

  return (
    <Drawer
      title="Spalten"
      placement="right"
      width={300}
      open={open}
      onClose={onClose}
      extra={
        !allVisible && (
          <Tooltip title="Alle einblenden">
            <Button size="small" icon={<EyeOutlined />} onClick={showAll} />
          </Tooltip>
        )
      }
    >
      <div style={{ userSelect: 'none' }}>
        {items.map((item, idx) => (
          <div
            key={item.key}
            draggable
            onDragStart={e => onDragStart(e, idx)}
            onDragOver={e => onDragOver(e, idx)}
            onDragEnd={onDragEnd}
            style={{
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '6px 4px', cursor: 'grab',
              borderBottom: '1px solid #f0f0f0',
            }}
          >
            <HolderOutlined style={{ color: '#bbb', flexShrink: 0 }} />
            <Checkbox
              checked={item.visible}
              onChange={() => toggleVisible(item.key)}
            >
              <span style={{ color: item.visible ? undefined : '#bbb' }}>
                {getLabel(item.key)}
              </span>
            </Checkbox>
          </div>
        ))}
      </div>
    </Drawer>
  );
};

export default ColumnSettingsDrawer;
