import React from "react";
import { useState, useEffect } from "react";
import { Segmented, Select, Table, Tag, Alert, Space, Tooltip } from "antd";
import { Typography } from 'antd';
import { PageHeader } from "@ant-design/pro-layout";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData } from "../utils/dataUtils";

const { Link, Text } = Typography;

const TileVA = (props) => {

  const { loading, setLoading, error, errorMessage, errorDetail, setApiError } = useApiState(true);
  const [data, setData] = useState([]);
  const [selectedYear, setSelectedYear] = useState();
  const [defaultYear] = useState(new Date().getFullYear());
  const [selectedCategory, setSelectedCategory] = useState();
  const [availableYears, setAvailableYears] = useState();
  const [availableCategories, setAvailableCategories] = useState();

  useEffect(() => {
    setSelectedYear(new Date().getFullYear());
    setSelectedCategory("Eigenveranstaltung");
    apiClient.get("/api/crud/1/DWH.CONFIG.v_portal_veranstaltung?order_by=beginn_dt:desc,ende_dt")
      .then((res) => {
        const resData = extractResponseData(res);
        setData(resData);
        setAvailableYears(getUniqueYears(resData).map((row) => ({ value: row, label: row })));
        setAvailableCategories(getUniqueCategories(resData).map((row) => ({ value: row, label: row })));
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten.', { response: { data: { detail: err.toString() } } }));
  }, []);

  const getUniqueYears = (arr) => {
    let tmpArr = arr.map((row) => ({ value: row.jahr }));
    tmpArr = [...new Set(tmpArr.map(item => item.value))];
    return tmpArr.sort((a, b) => a - b);
  };

  const getUniqueCategories = (arr) => {
    let tmpArr = arr.map((row) => ({ value: row.kategorie }));
    tmpArr = [...new Set(tmpArr.map(item => item.value))];
    return tmpArr.sort((a, b) => {
      const nameA = a.toUpperCase();
      const nameB = b.toUpperCase();
      if (nameA < nameB) return -1;
      if (nameA > nameB) return 1;
      return 0;
    });
  };

  const columns = [
    {
      title: "Zeitraum",
      dataIndex: "zeitraum",
      key: "zeitraum",
      width: 200,
      render: (zeitraum) => <Text>{zeitraum}</Text>
    },
    {
      title: " ",
      dataIndex: "logo_url",
      key: "logo_url",
      render: (logo_url, record) => (
        <Tooltip title={record.url ? "Klicken, um Homepage aufzurufen" : "keine Homepage hinterlegt"}>
          <Link href={record.url} target='_blank'>
            <img src={logo_url} alt="" style={{ height: 30, maxWidth: 80 }}
              onError={(e) => { e.target.style.display = 'none'; }} />
          </Link>
        </Tooltip>
      )
    },
    {
      title: "Messe",
      dataIndex: "name",
      key: "name",
      width: 250,
      render: (name, record) => (
        <Tooltip title={record.url ? "Klicken, um Homepage aufzurufen" : "keine Homepage hinterlegt"}>
          <Link href={record.url} target='_blank'><b>{name}</b></Link>
        </Tooltip>
      )
    },
    {
      title: "Nr",
      dataIndex: "veranstaltung_nr",
      key: "veranstaltung_nr",
      width: 50,
      render: (veranstaltung_nr) => <Tag>{veranstaltung_nr}</Tag>
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 50,
      render: (status) => (
        <Tag color={status === "aktiv" ? "blue" : (status === "geplant" ? "volcano" : "")}>
          {status.toUpperCase()}
        </Tag>
      )
    }
  ];

  return error ? (
    <Alert message={errorMessage} description={errorDetail} type="error" showIcon />
  ) : (
    <React.Fragment>
      <Space direction="vertical" size="middle">
        <PageHeader title="Veranstaltungen" subTitle="" />
        <Space>
          <Select
            defaultValue={defaultYear}
            style={{ width: 120 }}
            onChange={setSelectedYear}
            options={availableYears}
          />
          <Segmented
            defaultValue="Eigenveranstaltung"
            options={availableCategories}
            onChange={setSelectedCategory}
          />
        </Space>
        <Table
          pagination={false}
          size="middle"
          columns={columns}
          dataSource={data && selectedYear && selectedCategory && data.filter((row) => (row.jahr == selectedYear && row.kategorie == selectedCategory))}
          loading={loading}
          rowKey="id"
        />
      </Space>
    </React.Fragment>
  );
};

export default TileVA;
