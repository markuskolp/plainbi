import React from "react";
import Table from "../components/Table";
import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { Alert, Button, Form, Divider, Collapse } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { DownloadOutlined, PlayCircleOutlined } from "@ant-design/icons";
import LoadingMessage from "../components/LoadingMessage";
import { Sorter } from "../utils/sorter";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData, isTrue } from "../utils/dataUtils";
import CRUDFormItem from "../components/CRUDFormItem";

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

  useEffect(() => {
    getAdhoc();
    getParameters();
  }, []);

  const getAdhoc = async () => {
    apiClient.get("/api/repo/adhoc/" + id)
      .then((res) => {
        const resData = res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0];
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
        if (params.length > 0) {
          if (format !== 'XLSX' && format !== 'CSV') getData(defaults);
          else if (hasUrlParams || autorun) getBlobData(format, defaults);
          else setLoading(false);
        } else if (format === 'XLSX' || format === 'CSV') {
          getBlobData(format, {});
        } else {
          getData({});
        }
      })
      .catch(() => {
        setHasParams(false);
        if (format === 'XLSX' || format === 'CSV') getBlobData(format, {});
        else getData({});
      });
  };

  const buildBody = (params) => {
    const entries = Object.entries(params).filter(([, v]) => v !== null && v !== undefined && v !== "");
    return entries.length > 0
      ? Object.fromEntries(entries.map(([k, v]) => [k, String(v)]))
      : undefined;
  };

  const getData = async (params) => {
    const p = params !== undefined ? params : paramValues;
    setLoading(true);
    const body = buildBody(p);
    const req = body
      ? apiClient.post("/api/repo/adhoc/" + id + "/data", body)
      : apiClient.get("/api/repo/adhoc/" + id + "/data");
    req
      .then((res) => {
        setData(extractResponseData(res));
        setColumns(res.data.length === 0 || res.data.length === undefined ? res.data.columns : res.columns);
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));
  };

  const getBlobData = async (_format, params) => {
    const p = params !== undefined ? params : paramValues;
    setLoading(true);
    const dt = new Date().toISOString().substring(0, 19);
    const body = buildBody(p);
    const req = body
      ? apiClient.post("/api/repo/adhoc/" + id + "/data?format=" + _format, body, { responseType: 'blob' })
      : apiClient.get("/api/repo/adhoc/" + id + "/data?format=" + _format, { responseType: 'blob' });
    req
      .then((res) => {
        const href = URL.createObjectURL(res.data);
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', 'Adhoc_' + id + "_" + dt + "." + _format.toLowerCase());
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
        if (!hasParams || autorun) navigate("/");
        else setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten als ' + _format, err));
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

  const isExportFormat = format === 'XLSX' || format === 'CSV';

  const handleExecute = () => { if (validate()) { isExportFormat ? getBlobData(format) : getData(); } };

  function getColumn(column_label, column_name) {
    return {
      title: column_label,
      dataIndex: column_name,
      sorter: { compare: Sorter.DEFAULT, multiple: 3 },
      width: column_label.length * 10
    };
  }

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
            pagination={{ pageSize: 50 }}
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
