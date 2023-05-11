import React from "react";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Table, Button, notification } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { DownloadOutlined } from "@ant-design/icons";
import { LoadingMessage } from "../components/LoadingMessage";
import { message } from "antd";
import Axios from "axios";

const AdhocRuntime = () => {

  let { id } = useParams();
  let title = "A_" + id + ": t.b.d.";

  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    getData();
  }, []);

  //TODO: get adhoc metadata to set title !!!
  //TODO: make CSV/Excel buttons work
  //TODO: sorting
  //TODO: pagination

  const getData = async () => {
    setLoading(true);
    await Axios.get("/api/repo/adhoc/"+id+"/data").then(
      (res) => {
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        const resDataColumns = (res.data.length === 0 || res.data.length === undefined ? res.data.columns : res.columns); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setData(resData);
        console.log(JSON.stringify(resDataColumns));
        setColumns(resDataColumns);
        setLoading(false);
      }
      ).catch(
        function (error) {
          setLoading(false);
          message.error('Es gab einen Fehler beim Laden der Daten.');
        }
      );
  
  };

    // return a column to be used as metadata for a Table component
    function getColumn(column_label, column_name) {
      return {
        title: column_label,
        dataIndex: column_name,
        //key: column_name
        //width: 50,
        //render
      };
    }
  

  /*
  const columns = [
    {
      title: "Titel",
      dataIndex: "Title",
      width: 50
    },
    {
      title: "Inhalt",
      dataIndex: "Content",
      width: 150
    },
    {
      title: "Erstellt am",
      dataIndex: "CreatedAt",
      width: 50
    }
  ];
  */

  return (
    <React.Fragment>
      <PageHeader
        onBack={() => (window.location.href = "/")}
        title={title}
        subTitle=""
        extra={[
          <Button key="1" type="primary" icon={<DownloadOutlined />}>
            CSV
          </Button>,
          <Button key="2" type="primary" icon={<DownloadOutlined />}>
            Excel
          </Button>
        ]}
      />
      <br />
      <div>
        {loading ? (
          <h1>Lädt...</h1>
        ) : ( data && columns && 
          //<LoadingMessage />
          <Table 
            size="small"
            //columns={columns}
            columns={columns.map((column) => {
                return getColumn(column, column); 
              })
            }
            dataSource={data}
            pagination={{ pageSize: 50 }}
            scroll={{ y: 'calc(100vh - 400px)' }} // change later from 400px dynamically to the height of the header, page header and footer
            loading={loading}
          />
        )}
      </div>
    </React.Fragment>
  );
};

export default AdhocRuntime;
