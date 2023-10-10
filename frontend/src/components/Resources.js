import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Segmented, Card,  Row, Col, Tooltip , Image, Table, Tag, Button, DatePicker, Space, version, message } from "antd";
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
import { PageHeader } from "@ant-design/pro-layout";
const { Meta } = Card;
const { Title, Link, Text } = Typography;
const { Header, Content, Footer } = Layout;


const Resources = (props) => {


  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]); // all eligable resources (adhoc, application, external_resource)
  const [selectedCategory, setSelectedCategory] = useState(); 
  const [availableCategories, setAvailableCategories] = useState(); 

  useEffect(() => {
      setSelectedCategory("all");
      setAvailableCategories([
        {value: "all", label: "Alle"},
        {value: "adh", label: "Adhoc"},
        {value: "app", label: "Applikation"},
        {value: "ext", label: "Extern"}
      ]);
      initializeApp();
    }, []);

  const initializeApp = async () => {
    await Axios.get("/api/repo/resources", {headers: {Authorization: props.token}}).then(
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
        if (error.response.status === 401) {
          props.removeToken()
          message.error('Session ist abgelaufen');
        } else {
          message.error('Es gab einen Fehler beim Laden der berechtigten Ressourcen.');

        }
        console.log("error.response: " + error.response);
        console.error('Request Failed:', error.config);
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

const handleCategoryChange = (value) => {
  console.log('handleCategoryChange: ' + value);
  setSelectedCategory(value);
};

  return (
    <React.Fragment>
      <Space direction="vertical" size="middle" >
      <PageHeader
        title="Berechtigte Inhalte"
        subTitle=""
      />
        <Segmented 
          defaultValue="all" 
          options={availableCategories}
          onChange={handleCategoryChange}
        />
      <Table 
            pagination={false} 
            size="middle" 
            columns={columns}
            dataSource={data && selectedCategory && data.filter((row) => ("all" == selectedCategory || row.resource_type_de.substring(0,3).toLowerCase() == selectedCategory.toLowerCase()))} 
            onChange={onTableChange}
            loading={loading}
            rowKey="id"
            />
      </Space>
    </React.Fragment>
  );
};

export default Resources;
