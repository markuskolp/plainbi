import React from 'react';
import { useState, useEffect } from "react";
import LoadingMessage from "./LoadingMessage";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import {
  Button, Typography, Input, Space, Popconfirm,
  message, Tooltip, Breadcrumb, Alert
} from "antd";
import Table from "./Table";
import { Sorter } from "../utils/sorter";
import { CaretUpFilled, CaretDownFilled } from '@ant-design/icons';
import { EditOutlined, DeleteOutlined, CopyOutlined, DownloadOutlined, UnorderedListOutlined, CalendarOutlined } from "@ant-design/icons";
import dayjs from 'dayjs';
import CRUDModal from "./CRUDModal";
import TableModal from "./TableModal";
import CRUDToolbar from "./CRUDToolbar";
import CRUDCalendar, { parseDateString } from "./CRUDCalendar";
import { useSearchParams } from 'react-router-dom';
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData } from "../utils/dataUtils";
import { getPKForURL, getPKParamForURL, getColsParamForURL } from "../utils/pkUtils";

const { Link, Text } = Typography;

const CRUDPage = ({ name, tableName, tableForList, tableColumns, pkColumns, userColumn, defaultOrderBy, allowedActions, versioned, datasource, isRepo, lookups, token, sequence, breadcrumbItems, removeToken, externalActions, conditionalRowFormats }) => {

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
  const [offset, setOffset] = useState(0);
  const [limit, setLimit] = useState(20);
  const [order, setOrder] = useState("");
  const [defaultOrderInactive, setDefaultOrderInactive] = useState(false);
  const [totalCount, setTotalCount] = useState();
  const [filter, setFilter] = useState();
  const [tableParamChanged, setTableParamChanged] = useState(false);
  const [typingTimeout, setTypingTimeout] = useState(null);
  const [externalActionTimeout, setExternalActionTimeout] = useState(null);
  const [activateLookups, setActivateLookups] = useState(true);
  const [lookupData, setLookupData] = useState([]);
  const [filteredTableData, setFilteredTableData] = useState(null);
  const [searchParams] = useSearchParams();

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

  const api = isRepo === 'true' ? "/api/repo/" : "/api/crud/" + (datasource ? datasource + '/' : '');

  // ─── Initialisierung ─────────────────────────────────────────────────────────

  useEffect(() => {
    getTableData(tableName);
    apiClient.get("/api/profile").then((res) => setUsername(res.data.username)).catch(() => {});
    if (record_pk && allowedActions.includes("update") && !recordForPKLoaded) getPKRecordOpenModal(tableName);
    if (lookups) getLookupDataAll();
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
    const _searchParams = searchParams.toString().replaceAll("&", ",").replaceAll("=", ":");
    if (_searchParams && _searchParams.length > 0) queryParams.append("filter", _searchParams);
    queryParams.append("cols", getColsParamForURL(tableColumns, pkColumns));

    let endpoint = api + tableName + '?' + queryParams;
    if (tableForList && tableForList.length > 0) {
      setActivateLookups(false);
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
    const dt = new Date().toISOString().substring(0, 19);
    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    if (order && order.length > 0) queryParams.append("order_by", order);
    if (filter && filter.length > 0) queryParams.append("q", filter);
    const _searchParams = searchParams.toString().replaceAll("&", ",").replaceAll("=", ":");
    if (_searchParams && _searchParams.length > 0) queryParams.append("filter", _searchParams);
    queryParams.append("cols", getColsParamForURL(tableColumns, pkColumns));
    queryParams.append("format", _format);

    let endpoint = api + tableName + '?' + queryParams;
    if (tableForList && tableForList.length > 0) {
      setActivateLookups(false);
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

  const getLookupData = (lookupid) => apiClient.get("/api/repo/lookup/" + lookupid + "/data")
    .then((res) => ({ lookup: lookupid, lookupdata: extractResponseData(res) }))
    .catch((err) => setApiError('Fehler beim Laden der Lookup-Werte', err));

  const getLookupDataAll = () => {
    try { Promise.all(lookups.map(getLookupData)).then((data) => setLookupData(data)); }
    catch (error) { message.error('Fehler beim Laden der Lookup Werte.'); }
  };

  // ─── Externe Aktionen ────────────────────────────────────────────────────────

  const callStoredProcedure = (_id, wait_repeat_in_ms = 1000, name, body) => {
    if (externalActionTimeout) {
      message.info("Bitte " + wait_repeat_in_ms / 1000 + "s warten.");
    } else {
      message.info("Aktion wird ausgelöst");
      body = body.replaceAll('${username}', username);
      apiClient.post('/api/exec/' + (datasource ? datasource + '/' : '') + name, body)
        .then((res) => {
          const d = res.data.error === undefined ? res : res.data;
          d.error ? message.error(JSON.stringify(d.error)) : message.success('Erfolgreich ausgelöst.');
        })
        .catch(() => message.error('Fehler beim Auslösen der Aktion'));
      setExternalActionTimeout(setTimeout(() => setExternalActionTimeout(null), wait_repeat_in_ms));
    }
  };

  const callRestAPI = (_id, wait_repeat_in_ms = 1000, url, body) => {
    if (externalActionTimeout) {
      message.info("Bitte " + wait_repeat_in_ms / 1000 + "s warten.");
    } else {
      message.info("Aktion wird ausgelöst");
      body = body.replaceAll('${username}', username);
      apiClient.post(url, body)
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
    let newOrder = "";
    if (sorter.hasOwnProperty("column") && !sorter.length && sorter.order)
      newOrder = sorter.field + (sorter.order == "descend" ? " desc" : "");
    if (sorter.length > 1) {
      newOrder = sorter.map((s) => s.field + (s.order == "descend" ? " desc" : "")).join(",");
    }
    setOffset(newOffset);
    setLimit(newLimit);
    setOrder(newOrder);
    setTableParamChanged(!tableParamChanged);
  };

  const searchData = (value) => { setFilter(value); setTableParamChanged(!tableParamChanged); };

  const searchDataWithTimeout = (value) => {
    if (typingTimeout) clearTimeout(typingTimeout);
    setTypingTimeout(setTimeout(() => {
      setFilter(value);
      setOffset(0);
      setTableParamChanged(!tableParamChanged);
    }, 600));
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

  const getLookupValue = (lookupreturnid, lookupid) => {
    try {
      const rel = lookupData.filter((row) => row.lookup == lookupid)[0];
      const found = rel.lookupdata.find((r) => r.r == lookupreturnid);
      return found ? found.d : lookupreturnid;
    } catch (e) { return lookupreturnid; }
  };

  const renderSortIcon = (sortColumns, column_name) => {
    const sorted = sortColumns?.find(({ column }) => column.key === column_name);
    const defaultSorted = defaultOrderBy?.find((col) => col.column_name === column_name);
    let dir = "";
    if (sorted) { setDefaultOrderInactive(true); dir = sorted.order; }
    else if (defaultSorted && !defaultOrderInactive) dir = defaultSorted.direction || "ascend";
    if (!dir) return <CaretUpFilled className="inactive" style={{ fontSize: '14px' }} />;
    return (dir === "ascend" || dir === "asc")
      ? <CaretUpFilled style={{ fontSize: '14px' }} />
      : <CaretDownFilled style={{ fontSize: '14px' }} />;
  };

  const columnTitle = (label, column_name) => ({ sortColumns }) => (
    <div class="th-div-custom">
      <span class="th-div-custom-title">{label}</span>
      <span>{renderSortIcon(sortColumns, column_name)}</span>
    </div>
  );

  const getColumn = (column_label, column_name, datatype, ui) => ({
    title: columnTitle(column_label, column_name),
    dataIndex: column_name,
    sorter: { compare: Sorter.DEFAULT, multiple: 3 },
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

  const getLookupColumn = (column_label, column_name, lookupid) => ({
    title: columnTitle(column_label, column_name),
    dataIndex: column_name,
    sorter: { compare: Sorter.DEFAULT, multiple: 3 },
    key: column_name,
    width: 100,
    ellipsis: { showTitle: false },
    render: (text) => (
      <Tooltip placement="topLeft" title={getLookupValue(text, lookupid)}>
        <Text>{getLookupValue(text, lookupid)}</Text>
      </Tooltip>
    )
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

  // ─── Render ───────────────────────────────────────────────────────────────────

  const buildColumns = () => tableColumns
    .filter((col) => !col.showdetailsonly)
    .map((col) => (col.ui === "lookup" && activateLookups)
      ? getLookupColumn(col.column_label, col.column_name, col.lookup)
      : getColumn(col.column_label, col.column_name, col.datatype, col.ui)
    )
    .concat(
      (allowedActions.includes("delete") || allowedActions.includes("update") || allowedActions.includes("duplicate") || allowedActions.includes("export_dsdb"))
        ? getColumnAction(allowedActions.includes("delete"), allowedActions.includes("update"), allowedActions.includes("duplicate"), allowedActions.includes("export_dsdb"))
        : []
    );

  return (
    <React.Fragment>
      <CRUDToolbar
        allowedActions={allowedActions}
        externalActions={externalActions}
        onNew={showCreateModal}
        onDownload={(fmt) => getBlobData(tableName, fmt)}
        callRestAPI={callRestAPI}
        callStoredProcedure={callStoredProcedure}
      />

      {lookupData && (
        <React.Fragment>
          <Space style={{ marginBottom: 20, marginRight: 16, display: 'flex', justifyContent: 'space-between' }}>
            <Space direction="vertical">
              {breadcrumbItems ? <Breadcrumb items={breadcrumbItems} /> : ''}
              <Input.Search
                placeholder="Suche ..."
                onSearch={searchData}
                onChange={(e) => searchDataWithTimeout(e.target.value)}
                style={{ width: 500 }}
                allowClear
              />
            </Space>
            {allowedActions.includes("view_calendar") &&
              <Space>
                <Button type={view === 'table' ? 'primary' : 'default'} icon={<UnorderedListOutlined />} onClick={() => setView('table')} />
                <Button type={view === 'calendar' ? 'primary' : 'default'} icon={<CalendarOutlined />} onClick={() => setView('calendar')} />
              </Space>
            }
          </Space>

          {error && <Alert message={errorMessage} description={errorDetail} type="error" showIcon />}

          {!error && (
            view === 'calendar' && allowedActions.includes("view_calendar") ? (
              <CRUDCalendar loading={loading} calendarData={calendarData} />
            ) : (
              <Table
                size="small"
                columns={buildColumns()}
                dataSource={filteredTableData ?? tableData}
                pagination={{ defaultPageSize: 20, total: totalCount, hideOnSinglePage: true, showTotal: (total) => `Gesamt: ${total}` }}
                scroll={{ y: 'calc(100vh - 400px)', x: 'max-content' }}
                tableLayout="auto"
                loading={loading}
                onChange={handleChange}
                onRow={onRow}
              />
            )
          )}
        </React.Fragment>
      )}

      {showModal &&
        <CRUDModal tableColumns={tableColumns} handleCancel={closeModal} handleSave={closeAndRefreshModal} type={modalMode} tableName={tableName} pk={currentPK} pkColumns={pkColumns} userColumn={userColumn} versioned={versioned} datasource={datasource} isRepo={isRepo} token={token} sequence={sequence} externalActions={externalActions} />
      }
      {showTableModal &&
        <TableModal modalName="" tableColumns={tableModalColumns} tableData={tableModalData} handleClose={closeTableModal} />
      }
    </React.Fragment>
  );
};

export default CRUDPage;
