import React from "react";
import { useState, useEffect } from "react";
import CRUDFormItem from "./CRUDFormItem";
import {
  Button,
  Modal,
  Form,
  message,
  Alert,
  Tooltip,
  Spin
} from "antd";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { getPKParamForURL, getColsParamForModal } from "../utils/pkUtils";

const CRUDModal = ({ tableColumns, handleSave, handleCancel, type, tableName, pk, pkColumns, userColumn, versioned, datasource, isRepo, token, sequence, externalActions }) => {

  const { loading, setLoading, error, errorMessage, errorDetail, setApiError } = useApiState(false);
  const [saving, setSaving] = useState(false);
  const [recordData, setRecordData] = useState([]);
  const [externalActionTimeout, setExternalActionTimeout] = useState(null);
  const [username, setUsername] = useState("plainbi");

  let api = isRepo === 'true' ? "/api/repo/" : "/api/crud/" + (datasource ? datasource + '/' : '');

  useEffect(() => {
    (type == 'edit' || type == 'duplicate') ? getRecordData(tableName, pk) : setRecordData([]);
  }, [type, tableName, pk]);

  useEffect(() => {
    apiClient.get("/api/profile")
      .then((res) => setUsername(res.data.username))
      .catch(() => {});
  }, []);

  const getRecordData = async (tableName) => {
    setLoading(true);
    setRecordData(null);

    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    queryParams.append("pk", getPKParamForURL(pkColumns));
    queryParams.append("cols", getColsParamForModal(tableColumns));

    const endpoint = api + tableName + '/' + pk + '?' + queryParams;
    apiClient.get(endpoint)
      .then((res) => {
        const resData = res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0];
        setRecordData(resData);
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));
  };

  const replaceColumnVariables = (input) => {
    let _input = input;
    tableColumns && tableColumns.map((column) => {
      let dataValue = (recordData ? recordData[column.column_name] : null);
      _input = _input.replaceAll("${" + column.column_name + "}", dataValue);
    });
    return _input;
  };

  const callStoredProcedure = (_id, wait_repeat_in_ms = 1000, name, body) => {
    body = replaceColumnVariables(body);
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
    body = replaceColumnVariables(body);
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


  const updateTableRow = async (tableName, record, pk) => {
    setSaving(true);
    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    queryParams.append("pk", getPKParamForURL(pkColumns));
    if (userColumn) queryParams.append("usercol", userColumn);
    const endpoint = api + tableName + '/' + pk + '?' + queryParams;
    apiClient.put(endpoint, record)
      .then(() => {
        message.success('Erfolgreich gespeichert.');
        handleSave();
      })
      .catch((err) => {
        setSaving(false);
        setApiError('Es gab einen Fehler beim Speichern', err);
      });
  };

  const addTableRow = async (tableName, record) => {
    setSaving(true);
    const queryParams = new URLSearchParams();
    if (versioned) queryParams.append("v", 1);
    queryParams.append("pk", getPKParamForURL(pkColumns));
    if (userColumn) queryParams.append("usercol", userColumn);
    if (sequence) queryParams.append("seq", sequence);
    const endpoint = api + tableName + '?' + queryParams;
    apiClient.post(endpoint, record)
      .then(() => {
        message.success('Erfolgreich gespeichert.');
        handleSave();
      })
      .catch((err) => {
        setSaving(false);
        setApiError('Es gab einen Fehler beim Speichern', err);
      });
  };

  const handleOk = () => {
    type === 'edit' ? updateTableRow(tableName, recordData, pk) : addTableRow(tableName, recordData);
  };

  const handleChange = (key, value) => {
    setRecordData(prev => ({ ...prev, [key]: (value === "" ? null : value) }));
  };

  const layoutpage = { labelCol: { span: 6 }, wrapperCol: { span: 14 } };

  return (
    <React.Fragment>
      <Modal
        open={true}
        onOk={handleOk}
        onCancel={handleCancel}
        centered
        width="80vw"
        maskClosable={false}
        style={{ maxWidth: "1500px" }}
        afterOpenChange={(open) => { if (open) window.dispatchEvent(new CustomEvent('plainbi:modal-ready')); }}
        footer={[
          <Button key="2" htmlType="button" onClick={handleCancel}>Abbrechen</Button>,
          <Button key="3" type="primary" htmlType="submit" onClick={handleOk} loading={saving}>Speichern</Button>
        ]}
      >
        {loading && (
          <div style={{ textAlign: "center", marginBottom: 16 }}>
            <Spin size="large" />
          </div>
        )}

        {error && (
          <Alert message={errorMessage} description={errorDetail} type="error" showIcon />
        )}

        {type == 'edit' && externalActions && externalActions.map((externalAction) => (
          externalAction.type === 'call_rest_api' && (externalAction.position === 'detail' || !externalAction.position) ?
            <Tooltip key={externalAction.id} title={externalAction.tooltip ? externalAction.tooltip : ''}>
              <Button onClick={() => callRestAPI(externalAction.id, externalAction.wait_repeat_in_ms, externalAction.url, externalAction.body)}>
                {externalAction.label}
              </Button>
            </Tooltip> : null
        ))}

        {type == 'edit' && externalActions && externalActions.map((externalAction) => (
          externalAction.type === 'call_stored_procedure' && (externalAction.position === 'detail' || !externalAction.position) ?
            <Tooltip key={externalAction.id} title={externalAction.tooltip ? externalAction.tooltip : ''}>
              <Button onClick={() => callStoredProcedure(externalAction.id, externalAction.wait_repeat_in_ms, externalAction.name, externalAction.body)}>
                {externalAction.label}
              </Button>
            </Tooltip> : null
        ))}

        <Form {...layoutpage} layout="horizontal">
          {tableColumns && tableColumns.map((column) => {
            let defaultValue = column.default_value ? column.default_value : "";
            let dataValue = (recordData ? recordData[column.column_name] : defaultValue);
            if (dataValue === undefined) dataValue = defaultValue;
            if (typeof dataValue === 'function') dataValue = "";

            return (
              ((type == 'new' || recordData) && !column.showsummaryonly) ?
                <CRUDFormItem
                  key={column.column_name}
                  type={type}
                  name={column.column_name}
                  label={column.column_label}
                  required={column.required}
                  isprimarykey={pkColumns.includes(column.column_name)}
                  editable={column.editable}
                  lookupid={column.lookup}
                  ui={column.ui}
                  defaultValue={dataValue}
                  onChange={handleChange}
                  tooltip={column.tooltip}
                  multiple={column.multiple}
                  token={token}
                /> : ""
            );
          })}
        </Form>
      </Modal>
    </React.Fragment>
  );
};

export default CRUDModal;
