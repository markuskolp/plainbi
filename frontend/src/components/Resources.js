import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Card,  Row, Col, Tooltip , Image, Table, Tag, Button, DatePicker, Space, version } from "antd";
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
    // get app metadata
    await Axios.get("/api/repo/resources.json").then(
      (res) => {
        setData(res.data);
        setLoading(false);
      }
    ).catch(
      function (error) {
        setError(true);
        setLoading(false);
      }
    );
  };

  
//type, outputformat, name, description, url, dataset, source, target
const columns = [
  {
    title: " ",
    dataIndex: "outputformat",
    key: "outputformat",
    width: 50,
    render: (outputformat, record) => (
      
      (record.type === "Dashboard" ? <DashboardOutlined /> : (
        outputformat === "XLSX" ? <FileExcelFilled style={{color:'#1D6F42'}}/> : (
          outputformat === "CSV" ? <FileTextFilled style={{color:'#0055b3'}}/> : (
            outputformat === "HTML" ? <TableOutlined /> : <FileUnknownOutlined />
          ) 
        )
      )) 
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
      <Tag color="blue" style={{textTransform:'uppercase'}}>{record.dataset}</Tag>
    )
  }/*,    
  {
    title: "Quelle/System",
    dataIndex: "source",
    key: "source",
    width: 100,
    render: (name, record) => (
      <Tag color="blue" style={{textTransform:'uppercase'}}>{record.source}</Tag>
    )
  }
  */
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
            onChange={onTableChange}>
              
      </Table>
    </React.Fragment>
  );
};

export default Resources;
