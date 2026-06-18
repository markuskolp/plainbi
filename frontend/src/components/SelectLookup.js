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

  const { loading, setLoading, error, errorMessage, errorDetail, setApiError } = useApiState(true);
  const [lookupData, setLookupData] = useState([]);
  const [selectedValue, setSelectedValue] = useState(null);
  const [searchText, setSearchText] = useState("");
  const [searching, setSearching] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const searchTimeout = useRef(null);
  const isInitialLoad = useRef(true);
  const currentOffset = useRef(0);
  const currentSearch = useRef("");
  const lookupDataRef = useRef([]);
  const allDataLoaded = useRef(false); // true when server has < LOOKUP_LIMIT items total → client-side filter
  const fullData = useRef([]);         // complete unfiltered list when allDataLoaded
  const initialOnChangeFired = useRef(false); // guard: call onChange with defaultValue only once per lookupid
  const searchGen = useRef(0);         // generation counter: ignore stale API responses

  useEffect(() => { lookupDataRef.current = lookupData; }, [lookupData]);

  useEffect(() => {
    isInitialLoad.current = true;
    currentOffset.current = 0;
    currentSearch.current = "";
    allDataLoaded.current = false;
    fullData.current = [];
    initialOnChangeFired.current = false;
    setHasMore(true);
    setSearchText("");
    fetchLookupData("", defaultValue, false);
  }, [lookupid]);

  useEffect(() => {
    const cleansed = multiple
      ? (defaultValue || "").split(",")
      : (defaultValue === 0 ? defaultValue.toString() : defaultValue);
    setSelectedValue(cleansed || null);
    if (!isInitialLoad.current && defaultValue) {
      const val = String(defaultValue);
      if (!lookupDataRef.current.some(o => String(o.value) === val))
        fetchAndPrependSelected(defaultValue);
    }
  }, [defaultValue]);

  useEffect(() => {
    if (defaultValue && selectedValue && !initialOnChangeFired.current) {
      initialOnChangeFired.current = true;
      const valueCleansed = Array.isArray(selectedValue) ? selectedValue.join(",") : selectedValue;
      onChange({ target: { name, value: valueCleansed || null } });
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

  const getSelectedLabel = () => {
    if (!selectedValue || Array.isArray(selectedValue)) return "";
    const opt = lookupDataRef.current.find(o => String(o.value) === String(selectedValue));
    return opt ? opt.label : "";
  };

  const fetchAndPrependSelected = (value, baseOptions) => {
    apiClient.get("/api/repo/lookup/" + lookupid + "/data?selected=" + encodeURIComponent(value))
      .then((res) => {
        const selOpts = toOptions(extractResponseData(res));
        if (baseOptions !== undefined) {
          const combined = selOpts.length > 0 ? [...selOpts, ...baseOptions] : baseOptions;
          if (allDataLoaded.current) fullData.current = combined;
          setLookupData(combined);
          setLoading(false);
        } else if (selOpts.length > 0) {
          const updated = [...selOpts, ...lookupDataRef.current.filter(o => String(o.value) !== String(value))];
          if (allDataLoaded.current) fullData.current = updated;
          setLookupData(updated);
        }
      })
      .catch(() => {
        if (baseOptions !== undefined) { setLookupData(baseOptions); setLoading(false); }
      });
  };

  const fetchLookupData = (q, currentDefaultValue, append) => {
    const offset = append ? currentOffset.current : 0;
    const isFirstLoad = !append && isInitialLoad.current;
    const gen = append ? searchGen.current : ++searchGen.current;
    if (isFirstLoad) setLoading(true);
    else if (!append) setSearching(true);

    apiClient.get(buildUrl(q, offset))
      .then((res) => {
        if (!append && gen !== searchGen.current) return;
        const options = toOptions(extractResponseData(res));
        const serverCount = options.length;
        if (allowNewValues && q && !options.some((op) => String(op.label) === q))
          options.unshift({ value: q, label: q });
        setHasMore(serverCount === LOOKUP_LIMIT);
        if (append) {
          setLookupData(prev => [...prev, ...options]);
          currentOffset.current += LOOKUP_LIMIT;
          setLoadingMore(false);
        } else {
          currentOffset.current = LOOKUP_LIMIT;
          currentSearch.current = q;
          isInitialLoad.current = false;
          setSearching(false);
          if (!q) allDataLoaded.current = options.length < LOOKUP_LIMIT;
          if (isFirstLoad && currentDefaultValue && !options.some(o => String(o.value) === String(currentDefaultValue))) {
            fetchAndPrependSelected(currentDefaultValue, options);
          } else {
            if (!q && allDataLoaded.current) fullData.current = options;
            setLookupData(options);
            setLoading(false);
            if (isFirstLoad && !currentDefaultValue) initialOnChangeFired.current = true;
          }
        }
      })
      .catch((err) => {
        if (!append && gen !== searchGen.current) return;
        setApiError('Es gab einen Fehler beim Laden der Werte.', err);
        setSearching(false);
        setLoadingMore(false);
        isInitialLoad.current = false;
      });
  };

  const handleChange = (value) => {
    setSelectedValue(value);
    setSearchText("");
    currentSearch.current = "";
    const valueCleansed = Array.isArray(value) ? value.join(",") : value;
    const emuEvent = { "target": { "name": name, "value": valueCleansed ? valueCleansed : null } };
    onChange(emuEvent);
  };

  const onSearch = (value) => {
    setSearchText(value);
    currentSearch.current = value;
    if (allDataLoaded.current) {
      let filtered = value
        ? fullData.current.filter(o => o.label != null && o.label.toLowerCase().includes(value.toLowerCase()))
        : fullData.current;
      if (allowNewValues && value && !filtered.some(o => o.label === value))
        filtered = [{ value, label: value }, ...filtered];
      setLookupData(filtered);
      return;
    }
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => {
      currentOffset.current = 0;
      setHasMore(true);
      fetchLookupData(value, null, false);
    }, 300);
  };

  const onDropdownVisibleChange = (open) => {
    if (!open) {
      setSearchText("");
      currentSearch.current = "";
      return;
    }
    currentOffset.current = 0;
    if (allDataLoaded.current) {
      setLookupData(fullData.current);
      return;
    }
    setHasMore(true);
    fetchLookupData("", null, false);
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
    <Space direction="vertical" size={2}>
      <Space>
        <WarningOutlined style={{ color: 'darkred' }} />
        <Text style={{ color: 'darkred' }}>{errorMessage}</Text>
      </Space>
      {errorDetail && <Text style={{ color: 'darkred', fontSize: 11 }}>{errorDetail}</Text>}
    </Space>
  ) : (
    <Select
      placeholder="bitte auswählen ..."
      mode={multiple ? "multiple" : undefined}
      allowClear
      showSearch
      disabled={disabled}
      options={lookupData}
      value={selectedValue}
      searchValue={searchText}
      onChange={handleChange}
      onSearch={onSearch}
      onDropdownVisibleChange={onDropdownVisibleChange}
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
