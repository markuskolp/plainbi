import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Image, Table, Tag, message } from "antd";
import { Typography } from 'antd';
const { Title, Link, Text } = Typography;


const TileVA = () => {

  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]); 

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    await Axios.get("/api/crud/DWH.CONFIG.v_portal_veranstaltung?order_by=beginn_dt,ende_dt").then(
      (res) => {
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setData(resData);
        setLoading(false);
      }
    ).catch(
      function (error) {
        setError(true);
        setLoading(false);
        message.error('Es gab einen Fehler beim Laden der Daten.');
      }
    );
  };


  
  const columns = [
    {
      title: "Zeitraum",
      dataIndex: "zeitraum",
      key: "zeitraum",
      width: 200,
      render: (zeitraum, record) => (<React.Fragment><Text>{zeitraum}</Text></React.Fragment>)
    },
    {
      title: " ",
      dataIndex: "logo_url",
      key: "logo_url",
      //width: 140,
      //minwidth: 200,
      render: (logo_url) => (<Image preview={false} height={40} maxWidth={80} src={logo_url} />)
    },
    {
      title: "Messe",
      dataIndex: "name",
      key: "name",
      width: 250,
      render: (name, record) => (
        <React.Fragment>
          <Link href={record.url} target='_blank'><b>{name}</b></Link>
        </React.Fragment>
        )
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 50,
      render: (status,) => (<React.Fragment><Tag color={(status === "aktiv" ? "blue" : (status === "geplant" ? "volcano" : ""))} >{status.toUpperCase()}</Tag></React.Fragment>)
    }

  ];


const onTableChange = (pagination, filters, sorter, extra) => {
  console.log('params', pagination, filters, sorter, extra);
};


  return (
    <React.Fragment>
      <h1>Veranstaltungen</h1>
      <br />
      <Table 
            pagination={false} 
            size="middle" 
            columns={columns}
            dataSource={data} 
            onChange={onTableChange}
            rowKey="id"
            />
    </React.Fragment>
  );
};

export default TileVA;
