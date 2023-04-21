import React from "react";
import { Card,  Row, Col, Tooltip , Image, Table, Tag, Button, DatePicker, Space, version } from "antd";
import {  Avatar, Breadcrumb,  Layout, Menu, theme } from "antd";
import { Typography } from 'antd';
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

const { Meta } = Card;
const { Title, Link, Text } = Typography;
const { Header, Content, Footer } = Layout;
 

const Home = () => {

  const { Column, ColumnGroup } = Table;

  const data = [
    {
      key: "1",
      name: "Ticketaktionen - Wallet",
      description: "This is a ...",
      outputformat: "XLSX",
      datasource: "Adhoc",
      system: "Adhoc Tool",
      type: "Report",
      url: "static/Demo.xlsx" // /apps/adhoc/<nr>/export?format=<outputformat>
    },
    {
      key: "2",
      name: "ELQ - Prüfung Datenübertragung",
      outputformat: "HTML",
      datasource: "Adhoc",
      system: "Adhoc Tool",
      type: "Report",
      url: "adhoc/2" // /apps/adhoc/<nr>/export?format=<outputformat>
    },
    {
      key: "3",
      name: 'BigQuery vs. ADT - "Consent-Quote"',
      outputformat: "CSV",
      datasource: "Adhoc",
      system: "Adhoc Tool",
      type: "Report",
      url: "static/Demo.csv" // /apps/adhoc/<nr>/export?format=<outputformat>
    }
    
];

const data_va = [
  
];

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
      dataIndex: "datasource",
      key: "datasource",
      width: 100,
      render: (name, record) => (
        <Tag color="blue" style={{textTransform:'uppercase'}}>{record.datasource}</Tag>
      )
    }
  ];

  const columns_va = [
    {
      title: "Zeitraum",
      dataIndex: "period",
      key: "period",
      width: 200,
      render: (period, record) => (<React.Fragment><Text>{period}</Text></React.Fragment>)
    },
    {
      title: " ",
      dataIndex: "logo_url",
      key: "logo_url",
      width: 200,
      minwidth: 200,
      render: (logo_url) => (<Image preview={false} height={60} src={logo_url} />)
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
      render: (status,) => (<React.Fragment><Tag>{status.toUpperCase()}</Tag></React.Fragment>)
    }

  ];

  const onTableChange = (pagination, filters, sorter, extra) => {
    console.log('params', pagination, filters, sorter, extra);
  };

  return (
        <React.Fragment>
          <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
            <Col span={12}>
              <h1>Berechtigte Inhalte</h1>
              <br />
              <Table 
                    pagination={false} 
                    size="middle" 
                    columns={columns}
                    dataSource={data} 
                    onChange={onTableChange}>
                      
              </Table>
            </Col>
            <Col span={12}> 
              <h1>Veranstaltungen</h1>
              <br />
              <Table 
                    pagination={false} 
                    size="middle" 
                    columns={columns_va}
                    dataSource={data_va}>                    
              </Table>
            </Col>
          </Row>
      </React.Fragment>
  );
};

/*
          <Card style={{ width: 300, marginTop: 16 }} hoverable={true} >
            <Meta
              avatar={<Avatar src="/logo_va_automatica.png" />}
              title="automatica 2023"
              description="27. - 30.06.2023 (in 300 Tagen)"
            />
          </Card>

*/
export default Home;