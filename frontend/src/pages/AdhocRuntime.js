import React from "react";
import Table from "../components/Table";
import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { Alert, Button } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { DownloadOutlined } from "@ant-design/icons";
import LoadingMessage from "../components/LoadingMessage";
import { Sorter } from "../utils/sorter";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData } from "../utils/dataUtils";

const AdhocRuntime = (props) => {

  let { id } = useParams();
  const [queryParameters] = useSearchParams();
  let format = queryParameters.get("format");

  const navigate = useNavigate();

  const { loading, setLoading, error, errorMessage, errorDetail, setApiError } = useApiState(true);
  const [adhoc, setAdhoc] = useState([]);
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    getAdhoc();
    if (format === 'XLSX' || format === 'CSV') {
      getBlobData(format);
    } else {
      getData();
    }
  }, []);

  const getAdhoc = async () => {
    apiClient.get("/api/repo/adhoc/" + id)
      .then((res) => {
        const resData = res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0];
        setAdhoc(resData);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden des Adhoc.', err));
  };

  const getData = async () => {
    setLoading(true);
    apiClient.get("/api/repo/adhoc/" + id + "/data")
      .then((res) => {
        setData(extractResponseData(res));
        setColumns(res.data.length === 0 || res.data.length === undefined ? res.data.columns : res.columns);
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten', err));
  };

  const getBlobData = async (_format) => {
    setLoading(true);
    const dt = new Date().toISOString().substring(0, 19);
    apiClient.get("/api/repo/adhoc/" + id + "/data?format=" + _format, { responseType: 'blob' })
      .then((res) => {
        const href = URL.createObjectURL(res.data);
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', 'Adhoc_' + id + "_" + dt + "." + _format.toLowerCase());
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
        navigate("/");
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Daten als ' + _format, err));
  };

  const downloadData = (_format) => getBlobData(_format);

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
        extra={[
          <Button key="1" type="primary" icon={<DownloadOutlined />} onClick={() => downloadData("CSV")}>CSV</Button>,
          <Button key="2" type="primary" icon={<DownloadOutlined />} onClick={() => downloadData("XLSX")}>Excel</Button>
        ]}
      />
      <br />
      <div>
        {loading ? (
          <LoadingMessage />
        ) : error ? (
          <Alert message={errorMessage} description={errorDetail} type="error" showIcon />
        ) : (
          data && columns &&
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
