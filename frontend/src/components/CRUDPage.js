import React from 'react'
import { useState, useEffect } from "react";
import LoadingMessage from "./LoadingMessage";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import {
  Button,
  Typography,
  Layout,
  Input,
  Space,
  Popconfirm,
  message,
  Tooltip,
  Breadcrumb, Alert
} from "antd";
import Table from "./Table";
import { Sorter } from "../utils/sorter";
import {
  CaretUpFilled,
  CaretDownFilled
} from '@ant-design/icons';
import { PageHeader } from "@ant-design/pro-layout";
import { EditOutlined, PlusOutlined, DeleteOutlined, CopyOutlined, DownloadOutlined, UnorderedListOutlined, CalendarOutlined } from "@ant-design/icons";
import dayjs from 'dayjs';
import CRUDModal from "./CRUDModal";
import TableModal from "./TableModal";
import { useSearchParams } from 'react-router-dom';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import moment from 'moment';
import 'moment/locale/de';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData } from "../utils/dataUtils";

const { Link, Text } = Typography;

/*
Enum datatype { text | number | date | datetime | boolean }
Enum ui { hidden | label | textinput | numberinput | datepicker | datetimepicker | lookup | lookupn |
          textarea | textarea_sql | textarea_markdown | switch | password | password_nomem | email |
          html | modal_json_to_table }
*/

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

  let api = isRepo === 'true' ? "/api/repo/" : "/api/crud/" + (datasource ? datasource + '/' : '');

  const [lookupData, setLookupData] = useState([]);
  const [filteredTableData, setFilteredTableData] = useState(null);

  function findIndexByKeyValue(arr, key, value) {
    return arr.reduce((index, obj, i) => (obj[key] == value ? i : index), -1);
  }

  useEffect(() => {
    getTableData(tableName);
    apiClient.get("/api/profile")
      .then((res) => setUsername(res.data.username))
      .catch(() => {});
    if (record_pk && allowedActions.includes("update") && !recordForPKLoaded) {
      getPKRecordOpenModal(tableName);
    }
    lookups ? getLookupDataAll() : "";
  }, [tableName, tableParamChanged]);

  useEffect(() => {
    getTableData(tableName);
  }, [view]);

  const callStoredProcedure = (_id, wait_repeat_in_ms = 1000, name, body) => {
    if (externalActionTimeout) {
      message.info("Sie müssen " + wait_repeat_in_ms / 1000 + " Sekunden warten, bevor die Aktion wiederholt werden darf.");
    } else {
      message.info("Aktion wird ausgelöst");
      body = body.replaceAll('${username}', username);
      const url = '/api/exec/' + (datasource ? datasource + '/' : '') + name;
      apiClient.post(url, body)
        .then((res) => {
          const resData = res.data.error === undefined ? res : res.data;
          resData.error ? message.error(JSON.stringify(resData.error)) : message.success('Erfolgreich ausgelöst.');
        })
        .catch(() => message.error('Es gab einen Fehler beim Auslösen der Aktion'));
      setExternalActionTimeout(setTimeout(() => setExternalActionTimeout(null), wait_repeat_in_ms));
    }
  };

  const callRestAPI = (_id, wait_repeat_in_ms = 1000, url, body) => {
    if (externalActionTimeout) {
      message.info("Sie müssen " + wait_repeat_in_ms / 1000 + " Sekunden warten, bevor die Aktion wiederholt werden darf.");
    } else {
      message.info("Aktion wird ausgelöst");
      body = body.replaceAll('${username}', username);
      apiClient.post(url, body)
        .then((res) => {
          const resData = res.data.error === undefined ? res : res.data;
          resData.error ? message.error(JSON.stringify(resData.error)) : message.success('Erfolgreich ausgelöst.');
        })
        .catch(() => message.error('Es gab einen Fehler beim Auslösen der Aktion'));
      setExternalActionTimeout(setTimeout(() => setExternalActionTimeout(null), wait_repeat_in_ms));
    }
  };

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
      let _order = defaultOrderBy.map((col) => {
        let dir = (col.direction == "descend" || col.direction == "desc") ? " desc" : "";
        return col.column_name + dir;
      }).join(",");
      queryParams.append("order_by", _order);
    }

    if (filter && filter.length > 0) queryParams.append("q", filter);

    let _searchParams = searchParams.toString().replaceAll("&", ",").replaceAll("=", ":");
    if (_searchParams && _searchParams.length > 0) queryParams.append("filter", _searchParams);

    queryParams.append("cols", getColsParamForURL(tableColumns));

    let endpoint = api + tableName + '?' + queryParams;
    if (tableForList && tableForList.length > 0) {
      setActivateLookups(false);
      queryParams.delete("v");
      endpoint = api + tableForList + '?' + queryParams;
    }

    apiClient.get(endpoint)
      .then((res) => {
        const tc = res.data.length === 0 || res.data.length === undefined ? res.data.total_count : res.total_count;
        setTotalCount(tc);
        const resData = extractResponseData(res);
        setTableData(resData);

        try {
          const extractedCalendarData = resData.map(row => {
            const result = {};
            calendarFields.forEach(field => {
              if (["start"].includes(field.calendar_field)) {
                result[field.calendar_field] = parseDateString(row[field.column_name], 0);
              } else if (["end"].includes(field.calendar_field)) {
                result[field.calendar_field] = parseDateString(row[field.column_name], 1);
              } else {
                result[field.calendar_field] = row[field.column_name];
              }
            });
            return result;
          });
          setCalendarData(extractedCalendarData);
        } catch (er) {}

        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));
  };

  const getPKRecordOpenModal = async (tableName) => {
    const queryParams = new URLSearchParams();
    queryParams.append("filter", pkColumns + ":" + record_pk);
    const endpoint = api + tableName + '?' + queryParams;

    apiClient.get(endpoint)
      .then((res) => {
        const resData = extractResponseData(res);
        if (resData && resData.length > 0) {
          showEditModal(resData[0]);
          recordForPKLoaded = true;
        } else {
          setLoading(false);
          setApiError('Es gab einen Fehler mit der aufgerufenen URL.', { response: { data: { detail: 'Ein Eintrag mit dieser ID existiert nicht: ' + record_pk } } });
        }
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));
  };

  const getBlobData = async (tableName, _format) => {
    const dt = new Date().toISOString().substring(0, 19);

    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    if (order && order.length > 0) queryParams.append("order_by", order);
    if (filter && filter.length > 0) queryParams.append("q", filter);
    let _searchParams = searchParams.toString().replaceAll("&", ",").replaceAll("=", ":");
    if (_searchParams && _searchParams.length > 0) queryParams.append("filter", _searchParams);
    queryParams.append("cols", getColsParamForURL(tableColumns));
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
        message.success("Excel erfolgreich heruntergeladen - siehe Downloads > " + _filename);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten als ' + _format, err));
  };

  const getDsdbExport = async (_type, _id, _filename) => {
    if (_type != 'application' && _type != 'lookup') {
      message.error("kein valider Typ für DSDB-Export: " + _type);
      return;
    }
    const blobUri = "/api/repo/" + _type + "/" + _id + "/dsdb";
    apiClient.get(blobUri, { responseType: 'blob' })
      .then((res) => {
        const href = URL.createObjectURL(res.data);
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', _filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
        message.success(".dsdb erfolgreich heruntergeladen - siehe Downloads > " + _filename);
      })
      .catch(() => message.error('Es gab einen Fehler beim Laden der Daten'));
  };

  const downloadDsdb = (record) => {
    getDsdbExport(tableName, record.id, record.alias.toLowerCase() + '.dsdb');
  };

  const handleChange = (pagination, filters, sorter) => {
    const offset = pagination.current * pagination.pageSize - pagination.pageSize;
    const limit = pagination.pageSize;
    var order = "";
    if (sorter.hasOwnProperty("column")) {
      if (!sorter.length && sorter.order) {
        order = sorter.field + (sorter.order == "descend" ? " desc" : "");
      }
    }
    if (sorter.length > 1) {
      for (var i = 0; i < sorter.length; i++) {
        order += sorter[i].field;
        if (sorter[i].order == "descend") order += " desc";
        order += ",";
      }
      order = order.slice(0, -1);
    }
    setOffset(offset);
    setLimit(limit);
    setOrder(order);
    setTableParamChanged(!tableParamChanged);
  };

  const removeTableRow = async (tableName, record, pk) => {
    setLoading(true);
    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    queryParams.append("pk", getPKParamForURL(pkColumns));
    if (userColumn) queryParams.append("usercol", userColumn);
    const endpoint = api + tableName + '/' + pk + '?' + queryParams;

    apiClient.delete(endpoint, { data: { record } })
      .then(() => {
        getTableData(tableName);
        message.success('Erfolgreich gelöscht.');
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Löschen', err));
  };

  const ToBinary = (str) => {
    let result = "";
    str = encodeURIComponent(str);
    for (let i = 0; i < str.length; i++)
      if (str[i] == "%") { result += String.fromCharCode(parseInt(str.substring(i + 1, i + 3), 16)); i += 2; }
      else result += str[i];
    return result;
  };

  const base64UrlSafeEncode = (input) => {
    if (isRepo === 'true') return input;
    let base64 = btoa(ToBinary(input));
    return "[base64@" + base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') + "]";
  };

  const getPKForURL = (record, _pkColumn) => {
    if (_pkColumn.length <= 1) return base64UrlSafeEncode(record[_pkColumn[0]]);
    let pkforurl = "(";
    for (var i = 0; i < _pkColumn.length; i++) {
      pkforurl += _pkColumn[i] + ":" + base64UrlSafeEncode(record[_pkColumn[i]]) + ":";
    }
    return pkforurl.replace(/^:+|:+$/g, '') + ")";
  };

  const getPKParamForURL = (_pkColumn) => {
    if (_pkColumn.length <= 1) return _pkColumn[0];
    return _pkColumn.join(",");
  };

  const pkExists = (value) => pkColumns.some((col) => col.toLowerCase() === value.toLowerCase());

  const getColsParamForURL = (_cols) => {
    return _cols
      .filter((col) => !(col.showdetailsonly == 'true' && !pkExists(col.column_name)))
      .map((col) => col.column_name)
      .join(",");
  };

  const deleteConfirm = (record) => removeTableRow(tableName, record, getPKForURL(record, pkColumns));

  const handelPkModalNavigation = () => {
    if (record_pk && allowedActions.includes("update")) navigate(parentpath);
  };

  const showEditModal = (record) => {
    setCurrentPK(getPKForURL(record, pkColumns));
    setModalMode("edit");
    setShowModal(true);
  };
  const showCreateModal = () => { setCurrentPK(null); setModalMode("new"); setShowModal(true); };
  const showDuplicateModal = (record) => {
    setCurrentPK(getPKForURL(record, pkColumns));
    setModalMode("duplicate");
    setShowModal(true);
  };
  const closeModal = () => { setShowModal(false); handelPkModalNavigation(); };
  const closeAndRefreshModal = () => { setShowModal(false); handelPkModalNavigation(); getTableData(tableName); };

  function getTableColumnDefinition(title, dataIndex, key) {
    return { title, dataIndex, key };
  }

  const openTableModal = (tableName, jsonData) => {
    try {
      let parsedJsonData = JSON.parse(jsonData);
      setTableModalData(parsedJsonData);
      setTableModalColumns(Object.keys(parsedJsonData[0]).map((col) => getTableColumnDefinition(col, col, col)));
      setShowTableModal(true);
    } catch (er) {
      setTableModalData([]);
      setTableModalColumns([]);
      message.error("Fehler beim Anzeigen der Daten");
    }
  };
  const closeTableModal = () => { setTableModalData([]); setTableModalColumns([]); setShowTableModal(false); };

  function getColumnAction(deleteAllowed, updateAllowed, duplicateAllowed, exportdsdbAllowed) {
    return {
      title: " ", key: "action", width: 100, fixed: "right",
      render: (_, record) => ([
        <Space key="actions">
          {deleteAllowed && pkColumns &&
            <Popconfirm title="Löschen" description="Wirklich löschen?" onConfirm={(e) => deleteConfirm(record, e)} okText="Ja" cancelText="Nein">
              <DeleteOutlined style={{ fontSize: "18px" }} />
            </Popconfirm>
          }
          {updateAllowed && pkColumns &&
            <Link title="Editieren" onClick={(e) => showEditModal(record, e)}>
              <EditOutlined style={{ fontSize: "18px" }} />
            </Link>
          }
          {duplicateAllowed && pkColumns &&
            <Link title="Duplizieren" onClick={(e) => showDuplicateModal(record, e)}>
              <CopyOutlined style={{ fontSize: "18px" }} />
            </Link>
          }
          {exportdsdbAllowed && pkColumns &&
            <Link title="als .dsdb exportieren" onClick={(e) => downloadDsdb(record, e)}>
              <DownloadOutlined style={{ fontSize: "18px" }} />
            </Link>
          }
        </Space>
      ])
    };
  }

  const getLookupData = (lookupid) => apiClient.get("/api/repo/lookup/" + lookupid + "/data")
    .then((res) => ({ lookup: lookupid, lookupdata: extractResponseData(res) }))
    .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));

  const getLookupDataAll = () => {
    try {
      Promise.all(lookups.map(getLookupData)).then((data) => setLookupData(data));
    } catch (error) {
      message.error('Es gab einen Fehler beim Laden der Lookup Werte.');
    }
  };

  function getLookupValue(lookupreturnid, lookupid) {
    let displayValue = "";
    try {
      var relevantLookupData = lookupData.filter((row) => row.lookup == lookupid)[0];
      for (var i = 0; i < relevantLookupData.lookupdata.length; i++) {
        if (relevantLookupData.lookupdata[i].r == lookupreturnid) {
          displayValue = relevantLookupData.lookupdata[i].d;
          break;
        }
      }
    } catch (error) {}
    return displayValue ? displayValue : lookupreturnid;
  }

  const renderSortIcon = (sortColumns, column_name) => {
    const sortedColumn = sortColumns?.find(({ column }) => column.key === column_name);
    const defaultSortedColumn = defaultOrderBy?.find((column) => column.column_name === column_name);
    let _isSorted = false;
    let _sortDirection = "";
    if (sortedColumn) {
      setDefaultOrderInactive(true);
      _isSorted = true;
      _sortDirection = sortedColumn.order;
    } else if (defaultSortedColumn && !defaultOrderInactive) {
      _isSorted = true;
      _sortDirection = defaultSortedColumn.direction ? defaultSortedColumn.direction : "ascend";
    }
    return _isSorted ? (
      (_sortDirection === "ascend" || _sortDirection === "asc") ?
        <CaretUpFilled style={{ fontSize: '14px' }} /> :
        <CaretDownFilled style={{ fontSize: '14px' }} />
    ) : <CaretUpFilled className="inactive" style={{ fontSize: '14px' }} />;
  };

  function getColumn(column_label, column_name, datatype, ui) {
    return {
      title: ({ sortColumns }) => (
        <div class="th-div-custom">
          <span class="th-div-custom-title">{column_label}</span>
          <span>{renderSortIcon(sortColumns, column_name)}</span>
        </div>
      ),
      dataIndex: column_name,
      sorter: { compare: Sorter.DEFAULT, multiple: 3 },
      ellipsis: { showTitle: false },
      render: (text) => (
        <Tooltip placement="topLeft" title={(ui === "html" && text) ? '' : ((ui === "modal_json_to_table" && text) ? '' : text)}>
          {(datatype === "datetime" && text) ? dayjs(text).format("YYYY-MM-DD HH:mm:ss") : (
            (ui === "html" && text) ? <div dangerouslySetInnerHTML={{ __html: text }} /> : (
              (ui === "modal_json_to_table" && text) ?
                <Button onClick={() => openTableModal(tableName, text)} size="small">...</Button> :
                text
            )
          )}
        </Tooltip>
      ),
      key: column_name,
      width: 100
    };
  }

  const getLookupColumn = (column_label, column_name, lookupid) => ({
    title: ({ sortColumns }) => (
      <div class="th-div-custom">
        <span class="th-div-custom-title">{column_label}</span>
        <span>{renderSortIcon(sortColumns, column_name)}</span>
      </div>
    ),
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

  const searchData = (value) => {
    setFilter(value);
    setTableParamChanged(!tableParamChanged);
  };

  const searchDataWithTimeout = (value) => {
    if (typingTimeout) clearTimeout(typingTimeout);
    setTypingTimeout(setTimeout(() => {
      setFilter(value);
      setOffset(0);
      setTableParamChanged(!tableParamChanged);
    }, 600));
  };

  var checkFunctions = {
    "eq": (a, b) => a === b,
    "neq": (a, b) => a !== b,
    "gt": (a, b) => parseFloat(a) > parseFloat(b),
    "ge": (a, b) => parseFloat(a) >= parseFloat(b),
    "lt": (a, b) => parseFloat(a) < parseFloat(b),
    "le": (a, b) => parseFloat(a) <= parseFloat(b)
  };

  const downloadData = (_format) => getBlobData(tableName, _format);

  const onRow = (record) => {
    if (conditionalRowFormats && conditionalRowFormats.length) {
      for (var i = 0; i < conditionalRowFormats.length; i++) {
        let { column_name, operator, value, style } = conditionalRowFormats[i];
        let _inputValue = Object.entries(record).find((element) => element[0] === column_name)?.[1];
        if (checkFunctions[operator](_inputValue, value)) return { style };
      }
    }
  };

  moment.locale('de');

  function parseDateString(str, dayAdd = 0) {
    try {
      const [year, month, day] = str.split("-").map(Number);
      const date = new Date(year, month - 1, day + dayAdd);
      return isNaN(date.getTime()) ? null : date;
    } catch (er) { return null; }
  }

  const CalendarMessages = {
    today: 'Heute', previous: 'Zurück', next: 'Weiter', month: 'Monat',
    week: 'Woche', day: 'Tag', agenda: 'Agenda', date: 'Datum',
    time: 'Uhrzeit', event: 'Termin', noEventsInRange: 'Keine Termine in diesem Zeitraum.',
  };

  const EventWithTwoColumns = ({ event }) => (
    <a href={event.url} target="_blank" rel="noopener noreferrer"
      style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', width: '100%', height: '100%', textDecoration: 'none', color: 'inherit', padding: '2px' }}>
      <span style={{ flex: '1 1 auto', minWidth: 0 }}>{event.title}</span>
      <span style={{ fontSize: '0.85em', flex: '1 1 auto', minWidth: 0 }}>{event.subtitle}</span>
    </a>
  );

  const eventStyleGetter = (event) => ({
    style: { backgroundColor: event.color || '#007bff', color: 'white', borderRadius: '4px', padding: '2px 4px', cursor: 'pointer' }
  });

  return (
    <React.Fragment>
      <PageHeader
        title=""
        subTitle=""
        extra={[
          allowedActions.includes("export_excel") &&
          <Button key="excel" icon={<DownloadOutlined />} onClick={() => downloadData("XLSX")}>Excel</Button>,
          externalActions && externalActions.map((ea) => (
            ea.type === 'call_rest_api' && (ea.position === 'summary' || !ea.position) ?
              <Tooltip key={ea.id} title={ea.tooltip || ''}>
                <Button onClick={() => callRestAPI(ea.id, ea.wait_repeat_in_ms, ea.url, ea.body)}>{ea.label}</Button>
              </Tooltip> : null
          )),
          externalActions && externalActions.map((ea) => (
            ea.type === 'call_stored_procedure' && (ea.position === 'summary' || !ea.position) ?
              <Tooltip key={ea.id} title={ea.tooltip || ''}>
                <Button onClick={() => callStoredProcedure(ea.id, ea.wait_repeat_in_ms, ea.name, ea.body)}>{ea.label}</Button>
              </Tooltip> : null
          )),
          allowedActions.includes("create") &&
          <Button key="new" onClick={showCreateModal} type="primary" icon={<PlusOutlined />}>Neu</Button>
        ]}
      />
      {lookupData && (
        <React.Fragment>
          <Space style={{ marginBottom: 20, marginRight: 16, display: 'flex', justifyContent: 'space-between' }}>
            <Space direction="vertical">
              {breadcrumbItems ? <Breadcrumb items={breadcrumbItems} /> : ''}
              <Input.Search
                placeholder="Suche ..."
                onSearch={(value) => searchData(value)}
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
            <React.Fragment>
              {view === 'calendar' && allowedActions.includes("view_calendar") ? (
                <div className="height600">
                  {loading ? <LoadingMessage /> : (
                    <Calendar
                      defaultDate={new Date()}
                      events={calendarData}
                      localizer={momentLocalizer(moment)}
                      showMultiDayTimes
                      step={60}
                      views={{ month: true }}
                      messages={CalendarMessages}
                      components={{ event: EventWithTwoColumns }}
                      eventPropGetter={eventStyleGetter}
                      popup
                    />
                  )}
                </div>
              ) : (
                <Table
                  size="small"
                  columns={tableColumns && tableColumns
                    .filter((column) => !column.showdetailsonly)
                    .map((column) => (column.ui === "lookup" && activateLookups)
                      ? getLookupColumn(column.column_label, column.column_name, column.lookup)
                      : getColumn(column.column_label, column.column_name, column.datatype, column.ui)
                    )
                    .concat((allowedActions.includes("delete") || allowedActions.includes("update") || allowedActions.includes("duplicate") || allowedActions.includes("export_dsdb"))
                      ? getColumnAction(allowedActions.includes("delete"), allowedActions.includes("update"), allowedActions.includes("duplicate"), allowedActions.includes("export_dsdb"))
                      : []
                    )
                  }
                  dataSource={filteredTableData == null ? tableData : filteredTableData}
                  pagination={{ defaultPageSize: 20, total: totalCount, hideOnSinglePage: true, showTotal: (total) => `Gesamt: ${total}` }}
                  scroll={{ y: 'calc(100vh - 400px)', x: 'max-content' }}
                  tableLayout="auto"
                  loading={loading}
                  onChange={handleChange}
                  onRow={onRow}
                />
              )}
            </React.Fragment>
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
