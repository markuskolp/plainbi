import React from "react";
import { useState, useEffect, useRef } from "react";
import { Select, Space, Typography, Spin } from "antd";
import LoadingMessage from "./LoadingMessage";
import { WarningOutlined } from "@ant-design/icons";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData } from "../utils/dataUtils";

const { Text } = Typography;
const LOOKUP_LIMIT = 50;

const SelectLookup = ({ name, lookupid, defaultValue, onChange, disabled, token, allowNewValues, multiple = false }) => {

  const { loading, setLoading, error, errorMessage, setApiError } = useApiState(true);
  const [lookupData, setLookupData] = useState([]);
  const [searching, setSearching] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [defaultValueCleansed, setDefaultValueCleansed] = useState('');
  const searchTimeout = useRef(null);
  const isInitialLoad = useRef(true);
  const currentOffset = useRef(0);
  const currentSearch = useRef("");
  const lookupDataRef = useRef([]);

  useEffect(() => { lookupDataRef.current = lookupData; }, [lookupData]);

  useEffect(() => {
    const cleansed = multiple ? (defaultValue || "").split(",") : (defaultValue === 0 ? defaultValue.toString() : defaultValue);
    setDefaultValueCleansed(cleansed);
    isInitialLoad.current = true;
    currentOffset.current = 0;
    currentSearch.current = "";
    setHasMore(true);
    fetchLookupData("", defaultValue, false);
  }, [lookupid]);

  // When defaultValue changes after initial load, ensure it's resolved in the options
  useEffect(() => {
    if (!defaultValue || isInitialLoad.current) return;
    if (lookupDataRef.current.some(o => String(o.value) === String(defaultValue))) return;
    fetchAndPrependSelected(defaultValue);
  }, [defaultValue]);

  useEffect(() => {
    if (defaultValue && defaultValueCleansed && defaultValueCleansed.length > 0 && defaultValueCleansed != '') {
      handleChange(defaultValueCleansed);
    }
  }, [lookupData]);

  const toOptions = (rows) => rows.map((row) => ({
    value: row.r === 0 ? row.r.toString() : row.r,
    label: row.d
  }));

  const buildUrl = (q, offset) => {
    const params = new URLSearchParams({ limit: LOOKUP_LIMIT });
    if (q) params.append("q", q);
    if (offset > 0) params.append("offset", offset);
    return "/api/repo/lookup/" + lookupid + "/data?" + params;
  };

  const fetchAndPrependSelected = (value, baseOptions) => {
    apiClient.get("/api/repo/lookup/" + lookupid + "/data?selected=" + encodeURIComponent(value))
      .then((res) => {
        const selOpts = toOptions(extractResponseData(res));
        if (selOpts.length > 0) {
          if (baseOptions !== undefined) {
            setLookupData([...selOpts, ...baseOptions]);
            setLoading(false);
          } else {
            setLookupData(prev => [...selOpts, ...prev.filter(o => String(o.value) !== String(value))]);
          }
        } else if (baseOptions !== undefined) {
          setLookupData(baseOptions);
          setLoading(false);
        }
      })
      .catch(() => {
        if (baseOptions !== undefined) { setLookupData(baseOptions); setLoading(false); }
      });
  };

  const fetchLookupData = (q, currentDefaultValue, append) => {
    const offset = append ? currentOffset.current : 0;
    const isFirstLoad = !append && isInitialLoad.current;
    if (isFirstLoad) setLoading(true);
    else if (!append) setSearching(true);

    apiClient.get(buildUrl(q, offset))
      .then((res) => {
        const options = toOptions(extractResponseData(res));
        if (allowNewValues && q && !options.some((op) => op.label === q))
          options.push({ value: q, label: q });
        setHasMore(options.length === LOOKUP_LIMIT);
        if (append) {
          setLookupData(prev => [...prev, ...options]);
          currentOffset.current += LOOKUP_LIMIT;
          setLoadingMore(false);
        } else {
          currentOffset.current = LOOKUP_LIMIT;
          currentSearch.current = q;
          isInitialLoad.current = false;
          setSearching(false);
          if (isFirstLoad && currentDefaultValue && !options.some(o => String(o.value) === String(currentDefaultValue))) {
            fetchAndPrependSelected(currentDefaultValue, options);
          } else {
            setLookupData(options);
            setLoading(false);
          }
        }
      })
      .catch((err) => {
        setApiError('Es gab einen Fehler beim Laden der Werte.', { response: { data: { detail: err.toString() } } });
        setSearching(false);
        setLoadingMore(false);
        isInitialLoad.current = false;
      });
  };

  const handleChange = (value) => {
    const valueCleansed = Array.isArray(value) ? value.join(",") : value;
    const emuEvent = { "target": { "name": name, "value": valueCleansed ? valueCleansed : null } };
    onChange(emuEvent);
  };

  const onSearch = (value) => {
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => {
      currentOffset.current = 0;
      setHasMore(true);
      fetchLookupData(value, null, false);
    }, 300);
  };

  const onPopupScroll = (e) => {
    const { target } = e;
    if (!loadingMore && hasMore && target.scrollTop + target.offsetHeight >= target.scrollHeight - 100) {
      setLoadingMore(true);
      fetchLookupData(currentSearch.current, null, true);
    }
  };

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
      onPopupScroll={onPopupScroll}
      name={name}
      filterOption={false}
      notFoundContent={searching ? <Spin size="small" /> : "Keine Einträge"}
      dropdownRender={(menu) => (
        <>
          {menu}
          {loadingMore && <div style={{ textAlign: 'center', padding: 8 }}><Spin size="small" /></div>}
        </>
      )}
    />
  );
};

export default SelectLookup;
