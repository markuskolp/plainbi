import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Card,  Row, Col, Tooltip , Image, Table, Tag, Button, DatePicker, Space, version, message } from "antd";
import {
  AppstoreOutlined,
  SettingOutlined,
  UserOutlined,
  FileExcelTwoTone, FileExcelOutlined, FileExcelFilled,
  FileTextTwoTone, FileTextFilled,
  TableOutlined,
  DashboardOutlined,
  FileUnknownOutlined
} from "@ant-design/icons";
import {  Avatar, Breadcrumb,  Layout, Menu, theme } from "antd";
import { Typography } from 'antd';
const { Meta } = Card;
const { Title, Link, Text } = Typography;
const { Header, Content, Footer } = Layout;


const Resources = () => {


  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]); // all eligable resources (adhoc, application, external_resource)

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    await Axios.get("/api/repo/resources").then(
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
        message.error('Es gab einen Fehler beim Laden der berechtigten Ressourcen.');
      }
    );
  };



  
//resource_type, resource_type_de, output_format, name, description, url, dataset, source, target
const columns = [
  {
    title: " ",
    dataIndex: "output_format",
    key: "output_format",
    width: 50,
    render: (outputformat, record) => (
      
      (record.resource_type === "external_resource" ? <DashboardOutlined /> : (
        record.resource_type === "application" ? <AppstoreOutlined /> : (
          outputformat === "XLSX" ? <FileExcelFilled style={{color:'#1D6F42'}}/> : (
            outputformat === "CSV" ? <FileTextFilled style={{color:'#0055b3'}}/> : (
              outputformat === "HTML" ? <TableOutlined /> : <FileUnknownOutlined />
              ) 
            )
          )
        )
      )

    )
  },
  {
    title: "Name",
    dataIndex: "name",
    key: "name",
    sorter: (a, b) => (a.name > b.name ? 1 : -1),
    //defaultSortOrder: "ascend",
    width: 500,
    render: (name, record) => (
      <React.Fragment>
      <Tooltip title={record.description}>
          <Link href={record.url} target={record.target?record.target:""}>{name}</Link>
      </Tooltip>
      </React.Fragment>
      )
  },    
  {
    title: "Daten",
    dataIndex: "dataset",
    key: "dataset",
    width: 100,
    render: (name, record) => (
      record.dataset && <Tag color="blue" style={{textTransform:'uppercase'}}>{record.dataset}</Tag>
    )
  },    
  {
    title: "Typ",
    dataIndex: "resource_type_de",
    key: "resource_type_de",
    width: 100,
    render: (name, record) => (
      record.resource_type_de && <Tag color="blue" style={{textTransform:'uppercase'}}>{record.resource_type_de}</Tag>
    )
  }
  
];


const onTableChange = (pagination, filters, sorter, extra) => {
  console.log('params', pagination, filters, sorter, extra);
};


  return (
    <React.Fragment>
      <h1>Berechtigte Inhalte</h1>
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

export default Resources;
