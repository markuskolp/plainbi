import React from "react";
import Table from "../components/Table";
import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { Alert, Button, Form, Divider, Collapse, Tag, Space } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { DownloadOutlined, PlayCircleOutlined, FilterFilled } from "@ant-design/icons";
import LoadingMessage from "../components/LoadingMessage";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData, isTrue } from "../utils/dataUtils";
import CRUDFormItem from "../components/CRUDFormItem";
import ColumnFilterDropdown from "../components/ColumnFilterDropdown";

const AdhocRuntime = (props) => {

  let { id } = useParams();
  const [queryParameters] = useSearchParams();
  let format = queryParameters.get("format");
  const autorun = queryParameters.get("autorun") === "1";

  const navigate = useNavigate();

  const { loading, setLoading, error, errorMessage, errorDetail, setApiError } = useApiState(true);
  const [adhoc, setAdhoc] = useState([]);
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [parameters, setParameters] = useState([]);
  const [paramValues, setParamValues] = useState({});
  const [hasParams, setHasParams] = useState(false);
  const [urlParamsActive, setUrlParamsActive] = useState(false);
  const [errorFields, setErrorFields] = useState(new Set());
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [order, setOrder] = useState("");
  const [sortState, setSortState] = useState({});
  const [columnFilters, setColumnFilters] = useState({});
  const adhocRef = useRef({});

  useEffect(() => {
    getAdhoc().then(() => getParameters());
  }, []);

  const getAdhoc = async () => {
    return apiClient.get("/api/repo/adhoc/" + id)
      .then((res) => {
        const resData = res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0];
        adhocRef.current = resData;
        setAdhoc(resData);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden des Adhoc.', err));
  };

  const getParameters = async () => {
    const queryParams = new URLSearchParams();
    queryParams.append("filter", "adhoc_id:" + id);
    queryParams.append("cols", "id,name,name_technical,datatype,ui,lookup,default_value,required");
    apiClient.get("/api/repo/adhoc_parameter?" + queryParams)
      .then((res) => {
        const params = [...(extractResponseData(res) || [])].sort((a, b) => a.id - b.id);
        setParameters(params);
        setHasParams(params.length > 0);
        const defaults = {};
        let hasUrlParams = false;
        params.forEach(p => {
          if (p.default_value !== null && p.default_value !== undefined && p.default_value !== "")
            defaults[p.name_technical] = p.default_value;
          const urlVal = queryParameters.get(p.name_technical);
          if (urlVal !== null) { defaults[p.name_technical] = urlVal; hasUrlParams = true; }
        });
        setUrlParamsActive(hasUrlParams);
        setParamValues(defaults);
        const allRequiredHaveValues = params.every(p => {
          if (!isTrue(p.required) || p.ui === 'hidden') return true;
          const v = defaults[p.name_technical];
          return v !== null && v !== undefined && v !== "";
        });
        if (params.length > 0) {
          if (format !== 'XLSX' && format !== 'CSV') {
            if (allRequiredHaveValues) getData(defaults, 1, {});
            else setLoading(false);
          } else if ((hasUrlParams || autorun) && allRequiredHaveValues) {
            getBlobData(format, defaults);
          } else {
            setLoading(false);
          }
        } else if (format === 'XLSX' || format === 'CSV') {
          getBlobData(format, {});
        } else {
          getData({}, 1, {});
        }
      })
      .catch(() => {
        setHasParams(false);
        if (format === 'XLSX' || format === 'CSV') getBlobData(format, {});
        else getData({}, 1, {});
      });
  };

  const buildBody = (params) => {
    const entries = Object.entries(params).filter(([, v]) => v !== null && v !== undefined && v !== "");
    return entries.length > 0
      ? Object.fromEntries(entries.map(([k, v]) => [k, String(v)]))
      : undefined;
  };

  const buildFilterQuery = (filters) => {
    return Object.entries(filters)
      .map(([col, val]) => `filter=${encodeURIComponent(col + '~' + val)}`)
      .join('&');
  };

  const getData = async (params, page, filters, ord, ps) => {
    const p = params !== undefined ? params : paramValues;
    const pg = page !== undefined ? page : currentPage;
    const cf = filters !== undefined ? filters : columnFilters;
    const o = ord !== undefined ? ord : order;
    const psize = ps !== undefined ? ps : pageSize;
    setLoading(true);
    const body = buildBody(p);
    let pageQuery = `offset=${(pg - 1) * psize}&limit=${psize}`;
    const filterQuery = buildFilterQuery(cf);
    if (filterQuery) pageQuery += '&' + filterQuery;
    if (o) pageQuery += '&order_by=' + encodeURIComponent(o);
    const req = body
      ? apiClient.post("/api/repo/adhoc/" + id + "/data?" + pageQuery, body)
      : apiClient.get("/api/repo/adhoc/" + id + "/data?" + pageQuery);
    req
      .then((res) => {
        setData(extractResponseData(res));
        setColumns(res.data.length === 0 || res.data.length === undefined ? res.data.columns : res.columns);
        if (res.data.total_count !== undefined) setTotal(res.data.total_count);
        setCurrentPage(pg);
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));
  };

  const getBlobData = async (_format, params) => {
    const p = params !== undefined ? params : paramValues;
    setLoading(true);
    const now = new Date();
    const dt = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().substring(0, 19);
    const body = buildBody(p);
    const req = body
      ? apiClient.post("/api/repo/adhoc/" + id + "/data?format=" + _format, body, { responseType: 'blob' })
      : apiClient.get("/api/repo/adhoc/" + id + "/data?format=" + _format, { responseType: 'blob' });
    req
      .then((res) => {
        const href = URL.createObjectURL(res.data);
        const link = document.createElement('a');
        link.href = href;
        const safeName = (adhocRef.current.name || adhoc.name || "").replace(/[^a-zA-Z0-9äöüÄÖÜß _-]/g, "_").trim().substring(0, 50);
        link.setAttribute('download', 'Adhoc_' + id + (safeName ? "_" + safeName : "") + "_" + dt + "." + _format.toLowerCase());
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
        if (!hasParams || autorun) navigate("/");
        else setLoading(false);
      })
      .catch(async (err) => {
        if (err.response?.data instanceof Blob) {
          try {
            const json = JSON.parse(await err.response.data.text());
            setApiError('Es gab einen Fehler beim Laden der Daten als ' + _format, { response: { data: json } });
          } catch {
            setApiError('Es gab einen Fehler beim Laden der Daten als ' + _format, err);
          }
        } else {
          setApiError('Es gab einen Fehler beim Laden der Daten als ' + _format, err);
        }
      });
  };

  const validate = () => {
    const missing = new Set();
    parameters.forEach(p => {
      if (isTrue(p.required) && p.ui !== 'hidden') {
        const v = paramValues[p.name_technical];
        if (v === null || v === undefined || v === "") missing.add(p.name_technical);
      }
    });
    setErrorFields(missing);
    return missing.size === 0;
  };

  const handleParamChange = (key, value) => {
    setParamValues(prev => ({ ...prev, [key]: value === "" ? null : value }));
    setErrorFields(prev => { const s = new Set(prev); s.delete(key); return s; });
  };

  const handleColumnFilter = (column, value) => {
    const newFilters = { ...columnFilters, [column]: value };
    setColumnFilters(newFilters);
    getData(undefined, 1, newFilters);
  };

  const handleColumnFilterReset = (column) => {
    const newFilters = { ...columnFilters };
    delete newFilters[column];
    setColumnFilters(newFilters);
    getData(undefined, 1, newFilters);
  };

  const handleClearAllFilters = () => {
    setColumnFilters({});
    getData(undefined, 1, {});
  };

  const isExportFormat = format === 'XLSX' || format === 'CSV';

  const handleTableChange = (pagination, _filters, sorter) => {
    const page = pagination.current || 1;
    const ps = pagination.pageSize || pageSize;
    const newSortState = {};
    let newOrder = "";
    if (Array.isArray(sorter)) {
      sorter.filter(s => s.order).forEach(s => { newSortState[s.field] = s.order; });
      newOrder = Object.entries(newSortState).map(([f, o]) => f + (o === "descend" ? " desc" : "")).join(",");
    } else if (sorter.order) {
      newSortState[sorter.field] = sorter.order;
      newOrder = sorter.field + (sorter.order === "descend" ? " desc" : "");
    }
    setSortState(newSortState);
    setCurrentPage(page);
    setPageSize(ps);
    setOrder(newOrder);
    getData(undefined, page, undefined, newOrder, ps);
  };

  const handleExecute = () => {
    if (validate()) {
      setColumnFilters({});
      setSortState({});
      setOrder("");
      isExportFormat ? getBlobData(format) : getData(undefined, 1, {}, "");
    }
  };

  function getColumn(column_label, column_name) {
    const hasFilter = !!columnFilters[column_name];
    return {
      title: column_label,
      dataIndex: column_name,
      sorter: { multiple: 3 },
      sortOrder: sortState[column_name] ?? null,
      width: Math.max(column_label.length * 10, 80),
      filterIcon: <FilterFilled style={{ color: hasFilter ? '#1677ff' : undefined }} />,
      filterDropdown: ({ confirm, clearFilters }) => (
        <ColumnFilterDropdown
          confirm={confirm}
          clearFilters={clearFilters}
          columnName={column_name}
          currentValue={columnFilters[column_name] || ""}
          onFilter={(value) => handleColumnFilter(column_name, value)}
          onReset={() => handleColumnFilterReset(column_name)}
        />
      ),
      filtered: hasFilter,
    };
  }

  const activeFilterEntries = Object.entries(columnFilters);

  return (
    <React.Fragment>
      <PageHeader
        onBack={() => (window.location.href = "/")}
        title={adhoc.name ? adhoc.name : 'Adhoc wird geladen ...'}
        subTitle=""
        extra={!isExportFormat ? [
          <Button key="1" type="primary" icon={<DownloadOutlined />} onClick={() => { if (validate()) getBlobData("CSV"); }}>CSV</Button>,
          <Button key="2" type="primary" icon={<DownloadOutlined />} onClick={() => { if (validate()) getBlobData("XLSX"); }}>Excel</Button>
        ] : []}
      />
      <br />
      {hasParams && !autorun && (
        isExportFormat ? (
          <>
            <Form labelCol={{ span: 6 }} wrapperCol={{ span: 14 }} layout="horizontal" style={{ maxWidth: 900 }}>
              {parameters.map(param => (
                <CRUDFormItem
                  key={param.name_technical}
                  type="new"
                  name={param.name_technical}
                  label={param.name}
                  required={param.required}
                  isprimarykey={false}
                  editable="true"
                  lookupid={param.lookup}
                  ui={param.ui}
                  defaultValue={paramValues[param.name_technical] ?? param.default_value ?? ""}
                  onChange={handleParamChange}
                  token={props.token}
                  multiple="false"
                  hasError={errorFields.has(param.name_technical)}
                />
              ))}
            </Form>
            <div style={{ marginLeft: '25%', marginBottom: 16 }}>
              <Button type="primary" icon={<PlayCircleOutlined />} onClick={handleExecute}>Ausführen</Button>
            </div>
            <Divider />
          </>
        ) : (
          <Collapse
            defaultActiveKey={urlParamsActive ? [] : ['filter']}
            style={{ marginBottom: 16 }}
            items={[{
              key: 'filter',
              label: 'Filter',
              children: (
                <>
                  <Form labelCol={{ span: 6 }} wrapperCol={{ span: 14 }} layout="horizontal" style={{ maxWidth: 900 }}>
                    {parameters.map(param => (
                      <CRUDFormItem
                        key={param.name_technical}
                        type="new"
                        name={param.name_technical}
                        label={param.name}
                        required={param.required}
                        isprimarykey={false}
                        editable="true"
                        lookupid={param.lookup}
                        ui={param.ui}
                        defaultValue={paramValues[param.name_technical] ?? param.default_value ?? ""}
                        onChange={handleParamChange}
                        token={props.token}
                        multiple="false"
                        hasError={errorFields.has(param.name_technical)}
                      />
                    ))}
                  </Form>
                  <div style={{ marginLeft: '25%', marginBottom: 8 }}>
                    <Button type="primary" icon={<PlayCircleOutlined />} onClick={handleExecute}>Ausführen</Button>
                  </div>
                </>
              )
            }]}
          />
        )
      )}
      {activeFilterEntries.length > 0 && (
        <Space wrap style={{ marginBottom: 8 }}>
          {activeFilterEntries.map(([col, val]) => (
            <Tag key={col} closable color="blue" onClose={() => handleColumnFilterReset(col)}>
              {col}: {val}
            </Tag>
          ))}
          <Button size="small" onClick={handleClearAllFilters}>Alle löschen</Button>
        </Space>
      )}
      <div>
        {loading ? (
          <LoadingMessage />
        ) : error ? (
          <Alert message={errorMessage} description={errorDetail} type="error" showIcon />
        ) : (
          !isExportFormat && data && columns &&
          <Table
            size="small"
            columns={columns.map((column) => getColumn(column, column))}
            dataSource={data}
            onChange={handleTableChange}
            pagination={{ current: currentPage, pageSize, total, showSizeChanger: true, pageSizeOptions: [20, 50, 100, 200], showTotal: (t) => `Gesamt: ${t}` }}
            scroll={{ y: 'calc(100vh - 400px)', x: 'max-content' }}
            loading={loading}
            rowKey="id"
          />
        )}
      </div>
    </React.Fragment>
  );
};

export default AdhocRuntime;
