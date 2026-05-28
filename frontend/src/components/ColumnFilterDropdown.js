import React, { useState, useEffect, useRef } from "react";
import { Input, Button, Spin } from "antd";
import apiClient from "../utils/apiClient";

const DISTINCT_LIMIT = 50;

const stripHtml = (val) => {
  if (!val || typeof val !== 'string') return val;
  try {
    return new DOMParser().parseFromString(val, 'text/html').body.textContent || '';
  } catch {
    return val.replace(/<[^>]*>/g, '');
  }
};

const ColumnFilterDropdown = ({ confirm, clearFilters, datasource, tableName, columnName, ui, currentValue, onFilter, onReset, urlBase, extraParams }) => {
  const [inputValue, setInputValue] = useState(currentValue || "");
  const [values, setValues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const searchTimeout = useRef(null);
  const currentOffset = useRef(0);
  const currentSearch = useRef("");

  useEffect(() => { if (urlBase || (datasource && tableName && columnName)) fetchValues("", false); }, []);

  const buildUrl = (q, offset) => {
    const params = new URLSearchParams({ limit: DISTINCT_LIMIT });
    if (q) params.append("q", q);
    if (offset > 0) params.append("offset", offset);
    if (urlBase) {
      if (extraParams) {
        Object.entries(extraParams).forEach(([k, v]) => {
          if (v !== null && v !== undefined && v !== "") params.append(k, v);
        });
      }
      return `${urlBase}?${params}`;
    }
    return `/api/distinctvalues/${datasource}/${tableName}/${columnName}?${params}`;
  };

  const fetchValues = (q, append) => {
    const offset = append ? currentOffset.current : 0;
    if (append) setLoadingMore(true); else setLoading(true);
    apiClient.get(buildUrl(q, offset))
      .then(res => {
        const data = res.data?.data || [];
        setHasMore(data.length === DISTINCT_LIMIT);
        const processed = ui === 'html'
          ? [...new Set(data.map(v => stripHtml(v)).filter(v => v !== null && v !== ''))]
          : data;
        if (append) {
          setValues(prev => [...prev, ...processed]);
          currentOffset.current += DISTINCT_LIMIT;
        } else {
          setValues(processed);
          currentOffset.current = DISTINCT_LIMIT;
          currentSearch.current = q;
        }
      })
      .finally(() => { setLoading(false); setLoadingMore(false); });
  };

  const onInputChange = (e) => {
    const val = e.target.value;
    setInputValue(val);
    if (!(urlBase || (datasource && tableName && columnName))) return;
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => fetchValues(val, false), 300);
  };

  const applyFilter = (value) => {
    if (!value) return;
    onFilter(value);
    confirm();
  };

  const resetFilter = () => {
    setInputValue("");
    fetchValues("", false);
    onReset();
    clearFilters && clearFilters();
    confirm();
  };

  const onScroll = (e) => {
    const { target } = e;
    if (!loadingMore && hasMore && target.scrollTop + target.offsetHeight >= target.scrollHeight - 50) {
      fetchValues(currentSearch.current, true);
    }
  };

  return (
    <div style={{ padding: 8, width: 240 }}>
      <Input
        placeholder="Suchen oder eingeben..."
        value={inputValue}
        onChange={onInputChange}
        onPressEnter={() => applyFilter(inputValue)}
        allowClear
        style={{ marginBottom: 8 }}
      />
      {loading ? (
        <div style={{ textAlign: 'center', padding: 8 }}><Spin size="small" /></div>
      ) : (
        <div style={{ maxHeight: 200, overflowY: 'auto', borderTop: '1px solid #f0f0f0' }} onScroll={onScroll}>
          {values.map((val, i) => (
            <div
              key={i}
              style={{ padding: '4px 8px', cursor: 'pointer', fontSize: 13 }}
              onMouseEnter={e => e.currentTarget.style.background = '#f5f5f5'}
              onMouseLeave={e => e.currentTarget.style.background = ''}
              onClick={() => { setInputValue(String(val ?? "")); applyFilter(String(val ?? "")); }}
            >
              {val ?? "(leer)"}
            </div>
          ))}
          {loadingMore && <div style={{ textAlign: 'center', padding: 4 }}><Spin size="small" /></div>}
          {!loading && values.length === 0 && (
            <div style={{ padding: '4px 8px', color: '#999', fontSize: 13 }}>Keine Werte</div>
          )}
        </div>
      )}
      <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
        <Button size="small" onClick={resetFilter}>Zurücksetzen</Button>
        <Button size="small" type="primary" onClick={() => applyFilter(inputValue)} disabled={!inputValue}>Übernehmen</Button>
      </div>
    </div>
  );
};

export default ColumnFilterDropdown;
