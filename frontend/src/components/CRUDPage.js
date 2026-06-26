import React from 'react';
import { useState, useEffect, useCallback, useMemo } from "react";
import LoadingMessage from "./LoadingMessage";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import {
  Button, Typography, Input, Space, Popconfirm,
  message, Tooltip, Breadcrumb, Alert, Tag
} from "antd";
import { Resizable } from 'react-resizable';
import 'react-resizable/css/styles.css';
import Table from "./Table";
import { Sorter } from "../utils/sorter";
import { CaretUpFilled, CaretDownFilled } from '@ant-design/icons';
import { EditOutlined, DeleteOutlined, CopyOutlined, DownloadOutlined, UnorderedListOutlined, CalendarOutlined } from "@ant-design/icons";
import ColumnSettingsDrawer from "./ColumnSettingsDrawer";
import dayjs from 'dayjs';
import CRUDModal from "./CRUDModal";
import TableModal from "./TableModal";
import CRUDToolbar from "./CRUDToolbar";
import CRUDCalendar, { parseDateString } from "./CRUDCalendar";
import ColumnFilterDropdown from "./ColumnFilterDropdown";
import { useSearchParams } from 'react-router-dom';
import Axios from 'axios';
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData, isTrue } from "../utils/dataUtils";
import { getPKForURL, getPKParamForURL, getColsParamForURL } from "../utils/pkUtils";

const { Link } = Typography;

const ResizableTitle = ({ onResize, width, ...restProps }) => {
  if (!width) return <th {...restProps} />;
  return (
    <Resizable
      width={width}
      height={0}
      onResize={onResize}
      draggableOpts={{ enableUserSelectHack: false }}
      handle={
        <span
          style={{
            position: 'absolute', right: -4, top: 0, bottom: 0,
            width: 8, cursor: 'col-resize', zIndex: 10,
          }}
          onClick={e => e.stopPropagation()}
        />
      }
    >
      <th {...restProps} style={{ ...(restProps.style || {}), position: 'relative', overflow: 'visible' }} />
    </Resizable>
  );
};

const CRUDPage = ({ name, tableName, tableForList, tableColumns, pkColumns, userColumn, defaultOrderBy, allowedActions, versioned, datasource, isRepo, token, sequence, breadcrumbItems, externalActions, conditionalRowFormats, detailPages }) => {

  const { loading, setLoading, error, errorMessage, errorDetail, setApiError } = useApiState(true);

  const [tableData, setTableData] = useState([]);
  const [calendarData, setCalendarData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showTableModal, setShowTableModal] = useState(false);
  const [tableModalData, setTableModalData] = useState([]);
  const [tableModalColumns, setTableModalColumns] = useState([]);
  const [username, setUsername] = useState("plainbi");
  const [view, setView] = useState('table');
  const [currentPK, setCurrentPK] = useState();
  const [modalMode, setModalMode] = useState("new");
  const colStorageKey   = 'plainbi_cols_'  + window.location.pathname + '/' + tableName;
  const stateStorageKey = 'plainbi_state_' + window.location.pathname + '/' + tableName;

  const _savedState = (() => { try { return JSON.parse(localStorage.getItem(stateStorageKey)) || {}; } catch (_) { return {}; } })();

  const [offset, setOffset] = useState(0);
  const [limit, setLimit] = useState(20);
  const [order, setOrder] = useState(_savedState.order || "");
  const [defaultOrderInactive, setDefaultOrderInactive] = useState(!!_savedState.order);
  const [totalCount, setTotalCount] = useState();
  const [filter, setFilter] = useState(_savedState.filter || "");
  const [columnFilters, setColumnFilters] = useState(_savedState.columnFilters || {});
  const [tableParamChanged, setTableParamChanged] = useState(false);
  const [externalActionTimeout, setExternalActionTimeout] = useState(null);
  const [filteredTableData, setFilteredTableData] = useState(null);
  const [searchParams] = useSearchParams();
  const [colDrawerOpen, setColDrawerOpen] = useState(false);
  const [tableKey, setTableKey] = useState(0);

  const defaultColSettings = useCallback(() =>
    tableColumns
      .filter(c => !c.showdetailsonly)
      .map(c => ({ key: c.column_name, visible: true, width: 150 }))
  , [tableColumns]);

  const handleReset = useCallback(() => {
    const defaults = defaultColSettings();
    setColSettings(defaults);
    localStorage.removeItem(colStorageKey);
    setFilter('');
    setColumnFilters({});
    setOrder('');
    setDefaultOrderInactive(false);
    localStorage.removeItem(stateStorageKey);
    setOffset(0);
    setTableKey(prev => prev + 1);
    setTableParamChanged(prev => !prev);
  }, [defaultColSettings, colStorageKey, stateStorageKey]);

  const [colSettings, setColSettings] = useState(() => {
    try {
      const saved = localStorage.getItem(colStorageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        const defaults = tableColumns.filter(c => !c.showdetailsonly).map(c => c.column_name);
        const merged = parsed.filter(s => defaults.includes(s.key));
        defaults.forEach(k => { if (!merged.find(s => s.key === k)) merged.push({ key: k, visible: true, width: 150 }); });
        return merged;
      }
    } catch (_) {}
    return tableColumns.filter(c => !c.showdetailsonly).map(c => ({ key: c.column_name, visible: true, width: 150 }));
  });

  const parsedSort = useMemo(() => {
    if (!order) return {};
    const trimmed = order.trim();
    const isDesc = trimmed.endsWith(' desc');
    const col = isDesc ? trimmed.slice(0, -5) : trimmed.split(',')[0];
    return { [col]: isDesc ? 'descend' : 'ascend' };
  }, [order]);

  const isDirty = useMemo(() => {
    if (filter) return true;
    if (Object.keys(columnFilters).length > 0) return true;
    if (order) return true;
    const defaults = defaultColSettings();
    if (colSettings.length !== defaults.length) return true;
    return colSettings.some((s, i) => s.key !== defaults[i].key || !s.visible || s.width !== 150);
  }, [filter, columnFilters, order, colSettings, defaultColSettings]);

  let { pk } = useParams();
  let record_pk = (pk ? pk.toString() : null);
  let recordForPKLoaded = false;

  const calendarFields = tableColumns
    .filter(col => col.hasOwnProperty("calendar_field"))
    .map(col => ({ column_name: col.column_name, calendar_field: col.calendar_field }));

  const navigate = useNavigate();
  const location = useLocation();
  const { pathname } = location;
  const parentpath = pathname.substring(0, pathname.lastIndexOf('/'));

  const api = isTrue(isRepo) ? "/api/repo/" : "/api/crud/" + (datasource ? datasource + '/' : '');

  // ─── Initialisierung ─────────────────────────────────────────────────────────

  useEffect(() => {
    localStorage.setItem(stateStorageKey, JSON.stringify({ filter, columnFilters, order }));
  }, [filter, columnFilters, order]);

  useEffect(() => {
    getTableData(tableName);
    apiClient.get("/api/profile").then((res) => setUsername(res.data.username)).catch(() => {});
    if (record_pk && allowedActions.includes("update") && !recordForPKLoaded) getPKRecordOpenModal(tableName);
  }, [tableName, tableParamChanged]);

  useEffect(() => { getTableData(tableName); }, [view]);

  // ─── API Calls ───────────────────────────────────────────────────────────────

  const getTableData = async (tableName) => {
    setLoading(true);
    setTableData(null);

    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    queryParams.append("offset", offset);
    queryParams.append("limit", view == 'calendar' ? 10000 : limit);

    if (order && order.length > 0) {
      queryParams.append("order_by", order);
    } else if (defaultOrderBy && defaultOrderBy.length > 0 && !defaultOrderInactive) {
      const _order = defaultOrderBy.map((col) => {
        const dir = (col.direction == "descend" || col.direction == "desc") ? " desc" : "";
        return col.column_name + dir;
      }).join(",");
      queryParams.append("order_by", _order);
    }

    if (filter && filter.length > 0) queryParams.append("q", filter);
    const filterParts = [];
    const _searchParams = searchParams.toString().replaceAll("&", ",").replaceAll("=", ":");
    if (_searchParams) filterParts.push(_searchParams);
    const _colFilters = Object.entries(columnFilters).map(([col, val]) => `${col}~${val}`).join(",");
    if (_colFilters) filterParts.push(_colFilters);
    if (filterParts.length > 0) queryParams.append("filter", filterParts.join(","));
    queryParams.append("cols", getColsParamForURL(tableColumns, pkColumns));

    let endpoint = api + tableName + '?' + queryParams;
    if (tableForList && tableForList.length > 0) {
      queryParams.delete("v");
      endpoint = api + tableForList + '?' + queryParams;
    }

    apiClient.get(endpoint)
      .then((res) => {
        setTotalCount(res.data.length === 0 || res.data.length === undefined ? res.data.total_count : res.total_count);
        const resData = extractResponseData(res);
        setTableData(resData);
        try {
          setCalendarData(resData.map(row => {
            const result = {};
            calendarFields.forEach(field => {
              result[field.calendar_field] = ["start"].includes(field.calendar_field)
                ? parseDateString(row[field.column_name], 0)
                : ["end"].includes(field.calendar_field)
                  ? parseDateString(row[field.column_name], 1)
                  : row[field.column_name];
            });
            return result;
          }));
        } catch (er) {}
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));
  };

  const getPKRecordOpenModal = async (tableName) => {
    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    queryParams.append("filter", pkColumns + ":" + record_pk);
    apiClient.get(api + tableName + '?' + queryParams)
      .then((res) => {
        const resData = extractResponseData(res);
        if (resData && resData.length > 0) { showEditModal(resData[0]); recordForPKLoaded = true; }
        else setApiError('Es gab einen Fehler mit der aufgerufenen URL.', { response: { data: { detail: 'Eintrag nicht gefunden: ' + record_pk } } });
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));
  };

  const getBlobData = async (tableName, _format) => {
    const now = new Date();
    const dt = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().substring(0, 19);
    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    if (order && order.length > 0) queryParams.append("order_by", order);
    if (filter && filter.length > 0) queryParams.append("q", filter);
    const blobFilterParts = [];
    const _blobSearchParams = searchParams.toString().replaceAll("&", ",").replaceAll("=", ":");
    if (_blobSearchParams) blobFilterParts.push(_blobSearchParams);
    const _blobColFilters = Object.entries(columnFilters).map(([col, val]) => `${col}~${val}`).join(",");
    if (_blobColFilters) blobFilterParts.push(_blobColFilters);
    if (blobFilterParts.length > 0) queryParams.append("filter", blobFilterParts.join(","));
    queryParams.append("cols", getColsParamForURL(tableColumns, pkColumns));
    queryParams.append("format", _format);
    const htmlCols = tableColumns.filter(c => c.ui === 'html').map(c => c.column_name);
    if (htmlCols.length > 0) queryParams.append("html_cols", htmlCols.join(","));

    let endpoint = api + tableName + '?' + queryParams;
    if (tableForList && tableForList.length > 0) {
      queryParams.delete("v");
      endpoint = api + tableForList + '?' + queryParams;
    }

    apiClient.get(endpoint, { responseType: 'blob' })
      .then((res) => {
        const _filename = 'export_' + tableName + "_" + dt + "." + _format.toLowerCase();
        const href = URL.createObjectURL(res.data);
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', _filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
        message.success("Excel heruntergeladen - Downloads > " + _filename);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Download als ' + _format, err));
  };

  const getDsdbExport = async (_type, _id, _filename) => {
    if (_type != 'application' && _type != 'lookup') { message.error("kein valider Typ: " + _type); return; }
    apiClient.get("/api/repo/" + _type + "/" + _id + "/dsdb", { responseType: 'blob' })
      .then((res) => {
        const href = URL.createObjectURL(res.data);
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', _filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
        message.success(".dsdb heruntergeladen - Downloads > " + _filename);
      })
      .catch(() => message.error('Fehler beim Laden der Daten'));
  };

  const removeTableRow = async (tableName, record, pk) => {
    setLoading(true);
    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    queryParams.append("pk", getPKParamForURL(pkColumns));
    if (userColumn) queryParams.append("usercol", userColumn);
    apiClient.delete(api + tableName + '/' + pk + '?' + queryParams, { data: { record } })
      .then(() => { getTableData(tableName); message.success('Erfolgreich gelöscht.'); })
      .catch((err) => setApiError('Es gab einen Fehler beim Löschen', err));
  };

  // ─── Externe Aktionen ────────────────────────────────────────────────────────

  const callStoredProcedure = (_id, wait_repeat_in_ms = 1000, name, body) => {
    if (externalActionTimeout) {
      message.info("Bitte " + wait_repeat_in_ms / 1000 + "s warten.");
    } else {
      message.info("Aktion wird ausgelöst");
      body = body.replaceAll('${username}', username);
      apiClient.post('/api/exec/' + (datasource ? datasource + '/' : '') + name, body, { headers: { 'Content-Type': 'application/json;charset=utf-8', 'Access-Control-Allow-Origin': '*' } })
        .then((res) => {
          const d = res.data.error === undefined ? res : res.data;
          d.error ? message.error(JSON.stringify(d.error)) : message.success('Erfolgreich ausgelöst.');
        })
        .catch(() => message.error('Fehler beim Auslösen der Aktion'));
      setExternalActionTimeout(setTimeout(() => setExternalActionTimeout(null), wait_repeat_in_ms));
    }
  };

  const callRestAPI = (_id, wait_repeat_in_ms = 1000, url, body, token) => {
    if (externalActionTimeout) {
      message.info("Bitte " + wait_repeat_in_ms / 1000 + "s warten.");
    } else {
      message.info("Aktion wird ausgelöst");
      body = body.replaceAll('${username}', username);
      const headers = { 'Content-Type': 'application/json;charset=utf-8' };
      if (token) {
        const t = token.replaceAll('${username}', username);
        headers['Authorization'] = t.startsWith('Bearer ') ? t : 'Bearer ' + t;
      }
      Axios.post(url, body, { headers })
        .then((res) => {
          const d = res.data.error === undefined ? res : res.data;
          d.error ? message.error(JSON.stringify(d.error)) : message.success('Erfolgreich ausgelöst.');
        })
        .catch(() => message.error('Fehler beim Auslösen der Aktion'));
      setExternalActionTimeout(setTimeout(() => setExternalActionTimeout(null), wait_repeat_in_ms));
    }
  };

  // ─── Tabellen-Steuerung ──────────────────────────────────────────────────────

  const handleChange = (pagination, filters, sorter) => {
    const newOffset = pagination.current * pagination.pageSize - pagination.pageSize;
    const newLimit = pagination.pageSize;
    setOffset(newOffset);
    setLimit(newLimit);
    // Sortierung nur ändern wenn User explizit eine Spalte geklickt hat.
    // Bei reinem Seitenwechsel ist sorter = {} → order nicht überschreiben.
    if (sorter.hasOwnProperty("column")) {
      setDefaultOrderInactive(true);
      setOrder(sorter.order ? sorter.field + (sorter.order === "descend" ? " desc" : "") : "");
    } else if (Array.isArray(sorter) && sorter.length > 0) {
      setDefaultOrderInactive(true);
      setOrder(sorter.map(s => s.field + (s.order === "descend" ? " desc" : "")).join(","));
    } else if (Array.isArray(sorter) && sorter.length === 0) {
      setOrder("");
    }
    setTableParamChanged(!tableParamChanged);
  };

  const searchData = (value) => { setFilter(value); setTableParamChanged(prev => !prev); };

  const applyColumnFilter = (col, val) => {
    setColumnFilters(prev => ({ ...prev, [col]: val }));
    setOffset(0);
    setTableParamChanged(prev => !prev);
  };

  const removeColumnFilter = (col) => {
    setColumnFilters(prev => { const n = { ...prev }; delete n[col]; return n; });
    setOffset(0);
    setTableParamChanged(prev => !prev);
  };

  const clearAllColumnFilters = () => {
    setColumnFilters({});
    setOffset(0);
    setTableParamChanged(prev => !prev);
  };



  // ─── Modal-Steuerung ─────────────────────────────────────────────────────────

  const handelPkModalNavigation = () => {
    if (record_pk && allowedActions.includes("update")) navigate(parentpath);
  };

  const showEditModal = (record) => { setCurrentPK(getPKForURL(record, pkColumns, isRepo)); setModalMode("edit"); setShowModal(true); };
  const showCreateModal = () => { setCurrentPK(null); setModalMode("new"); setShowModal(true); };
  const showDuplicateModal = (record) => { setCurrentPK(getPKForURL(record, pkColumns, isRepo)); setModalMode("duplicate"); setShowModal(true); };
  const closeModal = () => { setShowModal(false); handelPkModalNavigation(); };
  const closeAndRefreshModal = () => { setShowModal(false); handelPkModalNavigation(); getTableData(tableName); };
  const deleteConfirm = (record) => removeTableRow(tableName, record, getPKForURL(record, pkColumns, isRepo));
  const downloadDsdb = (record) => getDsdbExport(tableName, record.id, record.alias.toLowerCase() + '.dsdb');

  const openTableModal = (tableName, jsonData) => {
    try {
      const parsed = JSON.parse(jsonData);
      setTableModalData(parsed);
      setTableModalColumns(Object.keys(parsed[0]).map((col) => ({ title: col, dataIndex: col, key: col })));
      setShowTableModal(true);
    } catch (er) { message.error("Fehler beim Anzeigen der Daten"); }
  };
  const closeTableModal = () => { setTableModalData([]); setTableModalColumns([]); setShowTableModal(false); };

  // ─── Spalten-Rendering ───────────────────────────────────────────────────────

  const renderSortIcon = (column_name) => {
    const dir = parsedSort[column_name];
    if (dir) return dir === 'descend'
      ? <CaretDownFilled style={{ fontSize: '14px' }} />
      : <CaretUpFilled style={{ fontSize: '14px' }} />;
    const defaultSorted = !defaultOrderInactive && defaultOrderBy?.find((col) => col.column_name === column_name);
    if (defaultSorted) return (defaultSorted.direction === 'descend' || defaultSorted.direction === 'desc')
      ? <CaretDownFilled style={{ fontSize: '14px' }} />
      : <CaretUpFilled style={{ fontSize: '14px' }} />;
    return <CaretUpFilled className="inactive" style={{ fontSize: '14px' }} />;
  };

  const columnTitle = (label, column_name) => () => (
    <div class="th-div-custom">
      <span class="th-div-custom-title">{label}</span>
      <span>{renderSortIcon(column_name)}</span>
    </div>
  );

  const getColumn = (column_label, column_name, datatype, ui) => ({
    title: columnTitle(column_label, column_name),
    dataIndex: column_name,
    sorter: { compare: Sorter.DEFAULT },
    ellipsis: { showTitle: false },
    render: (text) => (
      <Tooltip placement="topLeft" title={(ui === "html" || ui === "modal_json_to_table") && text ? '' : text}>
        {(datatype === "datetime" && text) ? dayjs(text).format("YYYY-MM-DD HH:mm:ss") : (
          (ui === "html" && text) ? <div dangerouslySetInnerHTML={{ __html: text }} /> : (
            (ui === "modal_json_to_table" && text)
              ? <Button onClick={() => openTableModal(tableName, text)} size="small">...</Button>
              : text
          )
        )}
      </Tooltip>
    ),
    key: column_name,
    width: 100
  });

  const getColumnAction = (deleteAllowed, updateAllowed, duplicateAllowed, exportdsdbAllowed) => ({
    title: " ", key: "action", width: 100, fixed: "right",
    render: (_, record) => (
      <Space>
        {deleteAllowed && pkColumns &&
          <Popconfirm title="Löschen" description="Wirklich löschen?" onConfirm={() => deleteConfirm(record)} okText="Ja" cancelText="Nein">
            <DeleteOutlined style={{ fontSize: "18px" }} />
          </Popconfirm>}
        {updateAllowed && pkColumns &&
          <Link title="Editieren" onClick={() => showEditModal(record)}><EditOutlined style={{ fontSize: "18px" }} /></Link>}
        {duplicateAllowed && pkColumns &&
          <Link title="Duplizieren" onClick={() => showDuplicateModal(record)}><CopyOutlined style={{ fontSize: "18px" }} /></Link>}
        {exportdsdbAllowed && pkColumns &&
          <Link title="als .dsdb exportieren" onClick={() => downloadDsdb(record)}><DownloadOutlined style={{ fontSize: "18px" }} /></Link>}
      </Space>
    )
  });

  // ─── Bedingte Zeilformatierung ───────────────────────────────────────────────

  const checkFunctions = {
    "eq": (a, b) => a === b, "neq": (a, b) => a !== b,
    "gt": (a, b) => parseFloat(a) > parseFloat(b), "ge": (a, b) => parseFloat(a) >= parseFloat(b),
    "lt": (a, b) => parseFloat(a) < parseFloat(b), "le": (a, b) => parseFloat(a) <= parseFloat(b)
  };

  const onRow = (record) => {
    if (conditionalRowFormats && conditionalRowFormats.length) {
      for (const { column_name, operator, value, style } of conditionalRowFormats) {
        const _inputValue = Object.entries(record).find(([k]) => k === column_name)?.[1];
        if (checkFunctions[operator](_inputValue, value)) return { style };
      }
    }
  };

  // ─── Spaltenbreite (ResizableTitle) ─────────────────────────────────────────

  const handleColResize = (key) => (_, { size }) => {
    const next = colSettings.map(s => s.key === key ? { ...s, width: size.width } : s);
    setColSettings(next);
    localStorage.setItem(colStorageKey, JSON.stringify(next));
  };

  // ─── Render ───────────────────────────────────────────────────────────────────

  const buildColumns = () => {
    const colMap = Object.fromEntries(tableColumns.map(c => [c.column_name, c]));
    return colSettings
      .filter(s => s.visible && colMap[s.key])
      .map(s => {
        const col = colMap[s.key];
        return {
          ...getColumn(col.column_label, col.column_name, col.datatype, col.ui),
          width: s.width,
          sortOrder: parsedSort[s.key],
          sortIcon: () => null,
          onHeaderCell: (column) => ({ width: column.width, onResize: handleColResize(s.key) }),
          filterDropdown: ({ confirm, clearFilters }) => (
            <ColumnFilterDropdown
              confirm={confirm}
              clearFilters={clearFilters}
              datasource={datasource || "0"}
              tableName={tableForList || tableName}
              columnName={col.column_name}
              ui={col.ui}
              currentValue={columnFilters[col.column_name] || ""}
              onFilter={(val) => applyColumnFilter(col.column_name, val)}
              onReset={() => removeColumnFilter(col.column_name)}
            />
          ),
          filteredValue: columnFilters[col.column_name]
            ? [columnFilters[col.column_name]]
            : searchParams.get(col.column_name)
              ? [searchParams.get(col.column_name)]
              : null,
        };
      })
      .concat(
        (allowedActions.includes("delete") || allowedActions.includes("update") || allowedActions.includes("duplicate") || allowedActions.includes("export_dsdb"))
          ? getColumnAction(allowedActions.includes("delete"), allowedActions.includes("update"), allowedActions.includes("duplicate"), allowedActions.includes("export_dsdb"))
          : []
      );
  };

  return (
    <React.Fragment>
      <CRUDToolbar
        allowedActions={allowedActions}
        externalActions={externalActions}
        onNew={showCreateModal}
        onDownload={(fmt) => getBlobData(tableName, fmt)}
        callRestAPI={callRestAPI}
        callStoredProcedure={callStoredProcedure}
        onColumnSettings={() => setColDrawerOpen(true)}
        onReset={handleReset}
        isDirty={isDirty}
        filter={filter}
        onSearch={searchData}
        breadcrumbItems={breadcrumbItems}
        view={view}
        onViewChange={setView}
      />

      <React.Fragment>

          {(Object.keys(columnFilters).length > 0 || [...searchParams.keys()].length > 0) && (
            <Space wrap style={{ marginBottom: 8 }}>
              {[...searchParams.entries()].map(([key, val]) => {
                const label = tableColumns.find(c => c.column_name === key)?.column_label || key;
                return (
                  <Tag key={`url-${key}`} closable color="blue" onClose={() => {
                    const next = new URLSearchParams(searchParams);
                    next.delete(key);
                    navigate(pathname + (next.toString() ? '?' + next.toString() : ''));
                    setTableParamChanged(prev => !prev);
                  }}>
                    {label}: {val}
                  </Tag>
                );
              })}
              {Object.entries(columnFilters).map(([col, val]) => {
                const label = tableColumns.find(c => c.column_name === col)?.column_label || col;
                return (
                  <Tag key={col} closable onClose={() => removeColumnFilter(col)}>
                    {label}: {val}
                  </Tag>
                );
              })}
              {(Object.keys(columnFilters).length > 0) &&
                <Button type="link" size="small" onClick={clearAllColumnFilters} style={{ padding: 0 }}>Alle löschen</Button>
              }
            </Space>
          )}

          {error && <Alert message={errorMessage} description={errorDetail} type="error" showIcon />}

          {!error && (
            view === 'calendar' && allowedActions.includes("view_calendar") ? (
              <CRUDCalendar loading={loading} calendarData={calendarData} />
            ) : (
              <Table
                key={tableKey}
                size="small"
                columns={buildColumns()}
                components={{ header: { cell: ResizableTitle } }}
                dataSource={filteredTableData ?? tableData}
                pagination={{ defaultPageSize: 20, total: totalCount, hideOnSinglePage: true, showTotal: (total) => `Gesamt: ${total}` }}
                scroll={{ y: 'calc(100vh - 400px)', x: 'max-content' }}
                tableLayout="fixed"
                loading={loading}
                onChange={handleChange}
                onRow={onRow}
              />
            )
          )}
        </React.Fragment>

      <ColumnSettingsDrawer
        open={colDrawerOpen}
        onClose={() => setColDrawerOpen(false)}
        tableColumns={tableColumns}
        colSettings={colSettings}
        onChange={(next) => {
          setColSettings(next);
          localStorage.setItem(colStorageKey, JSON.stringify(next));
        }}
      />

      {showModal &&
        <CRUDModal tableColumns={tableColumns} handleCancel={closeModal} handleSave={closeAndRefreshModal} type={modalMode} tableName={tableName} pk={currentPK} pkColumns={pkColumns} userColumn={userColumn} versioned={versioned} datasource={datasource} isRepo={isRepo} token={token} sequence={sequence} externalActions={externalActions} detailPages={detailPages} />
      }
      {showTableModal &&
        <TableModal modalName="" tableColumns={tableModalColumns} tableData={tableModalData} handleClose={closeTableModal} />
      }
    </React.Fragment>
  );
};

export default CRUDPage;
