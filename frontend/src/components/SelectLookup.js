import React from "react";
import { useState, useEffect, useRef, useCallback } from "react";
import { Select, Space, Typography } from "antd";
import LoadingMessage from "./LoadingMessage";
import { WarningOutlined } from "@ant-design/icons";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData } from "../utils/dataUtils";

const { Text } = Typography;

const SelectLookup = ({ name, lookupid, defaultValue, onChange, disabled, token, allowNewValues, multiple = false }) => {

  const { loading, setLoading, error, errorMessage, setApiError } = useApiState(true);
  const [lookupData, setLookupData] = useState([]);
  const [defaultValueCleansed, setDefaultValueCleansed] = useState('');

  useEffect(() => {
    setDefaultValueCleansed(multiple ? (defaultValue || "").split(",") : (defaultValue === 0 ? defaultValue.toString() : defaultValue));
    getLookupData(lookupid);
  }, [lookupid]);

  useEffect(() => {
    if (defaultValue && defaultValueCleansed && defaultValueCleansed.length > 0 && defaultValueCleansed != '') {
      handleChange(defaultValueCleansed);
    }
  }, [lookupData]);

  const getLookupData = async (lookupid) => {
    apiClient.get("/api/repo/lookup/" + lookupid + "/data")
      .then((res) => {
        setLookupData(extractResponseData(res).map((row) => ({
          value: row.r === 0 ? row.r.toString() : row.r,
          label: row.d
        })));
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Werte.', { response: { data: { detail: err.toString() } } }));
  };

  const handleChange = (value) => {
    const valueCleansed = Array.isArray(value) ? value.join(",") : value;
    const emuEvent = { "target": { "name": name, "value": valueCleansed ? valueCleansed : null } };
    onChange(emuEvent);
  };

  const currentValue = useRef();
  const onSearch = useCallback((value) => {
    currentValue.current = value;
    if (allowNewValues && value && !lookupData.some((op) => op.label === value)) {
      setLookupData([...lookupData, { value: value, label: value }]);
    } else {
      setLookupData([...lookupData]);
    }
  }, [lookupData]);

  return loading ? (
    <LoadingMessage />
  ) : error ? (
    <Space>
      <WarningOutlined style={{ color: 'darkred' }} />
      <Text style={{ color: 'darkred' }}>{errorMessage}</Text>
    </Space>
  ) : (
    <Select
      placeholder="bitte auswählen ..."
      mode={multiple ? "multiple" : ""}
      allowClear
      showSearch
      disabled={disabled}
      options={lookupData}
      defaultValue={defaultValueCleansed}
      onChange={handleChange}
      onSearch={onSearch}
      name={name}
      optionFilterProp="label"
    />
  );
};

export default SelectLookup;
