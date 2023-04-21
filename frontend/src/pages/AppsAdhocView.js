import React from "react";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Table, Button, notification } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { DownloadOutlined } from "@ant-design/icons";
import { LoadingMessage } from "./utils/LoadingMessage";
import Axios from "axios";

const AppsAdhocView = () => {
  const message = (type, message, description) => {
    alert(type + ': ' + message);
    /*
    notification.error({
      message: message,
      description: description,
      onClick: () => {
        console.log('Notification Clicked!');
      },
    })
    */
  };
  const [state, setstate] = useState([]);
  const [loading, setloading] = useState(true);
  useEffect(() => {
    getData();
  }, []);

  const getData = async () => {
    await Axios.get("https://api.fake-rest.refine.dev/samples").then(
      //await Axios.get("https://jsonplaceholder.typicode.com/comments").then(
      (res) => {
        setloading(false);
        setstate(
          res.data.map((row) => ({
            Title: row.title,
            Content: row.content,
            CreatedAt: row.createdAt,
            id: row.id
          }))
        );
      }
    ).catch(error => 
      message('error', 'Daten abrufen', error)
    )

  };

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

  let { id } = useParams();
  let title = "A_" + id + ": eloqua - Prüfung Datenübertragung";

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
        ) : (
          //<LoadingMessage />
          <Table
            size="small"
            columns={columns}
            dataSource={state}
            pagination={{ pageSize: 50 }}
            scroll={{ y: 500 }}
            loading={loading}
          />
        )}
      </div>
    </React.Fragment>
  );
};

export default AppsAdhocView;
