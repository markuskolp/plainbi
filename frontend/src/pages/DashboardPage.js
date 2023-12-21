import React from "react";
import Table from "../components/Table";
import { Alert, Button, Typography,Tooltip, Col, Row, Select, Space, DatePicker, Menu, Dropdown, Input} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { FullscreenOutlined, MoreOutlined, HistoryOutlined } from "@ant-design/icons";
import DashboardItem from "../components/DashboardItem";
import ChartRenderer from "../components/ChartRenderer";
import Dashboard from "../components/Dashboard";
import cubejs from "@cubejs-client/core";
import { CubeProvider } from "@cubejs-client/react";

import dayjs from 'dayjs';

const { Title, Link, Text } = Typography;
import "../css/dashboard.css";

const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDI2NjYzNDcsImV4cCI6MTcwMjc1Mjc0N30.D8iCMGAH72GgOjNm6dWuFWHStlrzVVAEpomOk4eKK5Y';
const cubejsApi = cubejs(token, { apiUrl: 'http://localhost:4000/cubejs-api/v1' });

const { RangePicker } = DatePicker;

const rangePresets = [
  { label: 'Letzte 7 Tage', value: [dayjs().add(-7, 'd'), dayjs()] },
  { label: 'Letzte 14 Tage', value: [dayjs().add(-14, 'd'), dayjs()] },
  { label: 'Letzte 30 Tage', value: [dayjs().add(-30, 'd'), dayjs()] },
  { label: 'Letzte 90 Tage', value: [dayjs().add(-90, 'd'), dayjs()] },
];
const onRangeChange = (dates, dateStrings) => {
  if (dates) {
    console.log('From: ', dates[0], ', to: ', dates[1]);
    console.log('From: ', dateStrings[0], ', to: ', dateStrings[1]);
  } else {
    console.log('Clear');
  }
};

/*
const deserializeItem = i => ({
  ...i,
  layout: JSON.parse(i.layout) || {},
  vizState: JSON.parse(i.vizState)
});
*/

const defaultLayout = i => ({
  x: i.layout.x || 0,
  y: i.layout.y || 0,
  w: i.layout.w || 4,
  h: i.layout.h || 8,
  minW: 4,
  minH: 3
});

const DashboardPage = (props) => {

  //const { loading, error, data } = useQuery(GET_DASHBOARD_ITEMS);
  const loading = false;
  const error = false;
  const dashboard = { name: 'Tickets'};
  
    
  const defaultDashboard = 
    {
      dashboardName: "Tickets",
      dashboardItems: [
        {
            vizState: {
              query:{
                "measures": [
                  "Tickets.ticketsOrdered"
                ],
                "order": {
                  "Tickets.dateRegistration": "asc"
                },
                "segments": [
                  "Tickets.onlineBestellungen"
                ],
                "filters": [
                  {
                    "member": "Veranstaltung.faireventNameYear",
                    "operator": "equals",
                    "values": [
                      "EXPO REAL 2023"
                    ]
                  }
                ]
              },
              chartType:"number"
            },
            name: "Onlinebestellungen",
            id: 10,
            layout: {x:0,y:0,w:4,h:4}
        },
        {
            vizState: {
              query:{
                "measures": [
                  "Tickets.ticketsOrderedCumulativeSQL"
                ],
                "order": [
                  [
                    "Tickets.ticketsOrderedCumulativeSQL",
                    "asc"
                  ]
                ],
                "segments": [
                  "Tickets.onlineBestellungen"
                ],
                "filters": [
                  {
                    "member": "Veranstaltung.faireventNameYear",
                    "operator": "equals",
                    "values": [
                      "EXPO REAL 2023"
                    ]
                  }
                ],
                "dimensions": [
                  "Tickets.dayBeforeEnd"
                ]
              },
              chartType:"bar"
            },
            name: "Verlauf nach Tagen vor VA-Ende",
            id: 14,
            layout: {x:5,y:0,w:20,h:8}
        },
        {
            vizState: {
              query:{
                "order": [
                  [
                    "Tickets.ticketsOrdered",
                    "desc"
                  ]
                ],
                "segments": [
                  "Tickets.onlineBestellungen"
                ],
                "dimensions": [
                  "Land.countryDe"
                ],
                "filters": [
                  {
                    "member": "Veranstaltung.faireventNameYear",
                    "operator": "equals",
                    "values": [
                      "EXPO REAL 2023"
                    ]
                  }
                ],
                "measures": [
                  "Tickets.ticketsOrdered"
                ]
              },
              chartType:"verticalbar"
            },
            name: "Länderranking",
            id: 15,
            layout: {x:16,y:8,w:8,h:8}
        },
        {
            vizState: {
              query:{
                "order": [
                  [
                    "Tickets.ticketsOrdered",
                    "desc"
                  ]
                ],
                "segments": [
                  "Tickets.onlineBestellungen"
                ],
                "dimensions": [
                  "Land.countryDe"
                ],
                "filters": [
                  {
                    "member": "Veranstaltung.faireventNameYear",
                    "operator": "equals",
                    "values": [
                      "EXPO REAL 2023"
                    ]
                  }
                ],
                "measures": [
                  "Tickets.ticketsOrdered"
                ]
              },
              chartType:"table"
            },
            name: "Länderranking",
            id: 16,
            layout: {x:8,y:8,w:8,h:8}
        },
        {
            vizState: {
              query:{
                "measures": [
                  "Tickets.ticketsOrdered"
                ],
                "order": {
                  "Tickets.ticketsOrdered": "desc"
                },
                "segments": [
                  "Tickets.onlineBestellungen"
                ],
                "dimensions": [
                  "Artikel.articleNameDe",
                  "Artikel.articleNumber",
                  "Artikel.ticketCategoryDe"
                ],
                "filters": [
                  {
                    "member": "Veranstaltung.faireventNameYear",
                    "operator": "equals",
                    "values": [
                      "EXPO REAL 2023"
                    ]
                  }
                ]
              },
              chartType:"table"
            },
            name: "Produktranking",
            id: 18,
            layout: {x:0,y:8,w:8,h:8}
        }
      ]
    }
  ;
  

  const data = defaultDashboard; //JSON.parse(defaultDashboardItems);

  if (loading) {
    return <Spin />;
  }

  if (error) {
    return (
      <Alert
        message="Error occured while loading your query"
        description={error.toString()}
        type="error"
      />
    );
  }

  const Empty = () => (
    <div
      style={{
        textAlign: "center",
        padding: 12
      }}
    >
      <h2>Dieses Dashboard ist noch leer.</h2>
      <Link to="/explore">
        <Button type="primary" size="large" icon="plus">
          Inhalt hinzufügen
        </Button>
      </Link>
    </div>
  );

  const automaticUpdateDropdownMenu = (
    <Menu>
      <Menu.Item>
        <Text>jede Minute</Text>
      </Menu.Item>
      <Menu.Item>
        <Text>alle 5 Minuten</Text>
      </Menu.Item>
      <Menu.Item>
        <Text>alle 15 Minuten</Text>
      </Menu.Item>
      <Menu.Item>
        <Input size="small" placeholder="Alle x Sekunden" />
      </Menu.Item>
      <Menu.Item>
        <Text>deaktivieren</Text>
      </Menu.Item>
    </Menu>
  );

  const dashboardItem = item => (
    <div key={item.id} data-grid={defaultLayout(item)}>
      <DashboardItem key={item.id} itemId={item.id} title={item.name}>
        <ChartRenderer vizState={item.vizState} />
      </DashboardItem>
    </div>
  );

  return !data || data.dashboardItems.length ? (
      <CubeProvider cubejsApi={cubejsApi}>
        <React.Fragment>
          <PageHeader
            //onBack={() => (window.location.href = "/")}
            title={dashboard.name}
            subTitle=""
            //style={{ background: 'white' }}
            extra={[
              <Space>
                <Link href="#">
                  <Tooltip title="Vollbild">
                    <FullscreenOutlined />
                  </Tooltip>
                </Link>
                <Link href="#">
                  <Tooltip title="Automatische Aktualisierung">
                    <Dropdown
                      overlay={automaticUpdateDropdownMenu}
                      placement="bottomLeft"
                      trigger={["click"]}
                    >
                      <HistoryOutlined />
                    </Dropdown>
                  </Tooltip>
                </Link>
              </Space>
            ]}
          />
          <Row style={{paddingInline: "16px", paddingBlock: "6px"}}>
            <Col span={24} style={{textAlign:"right"}}>
              <Space style={{textAlign:"left"}}>
                <Select
                    placeholder="bitte auswählen ..."
                    allowClear
                    showSearch
                    size='small'
                    disabled={false}
                    options={[
                              { 
                                label: '2023',
                                options: [
                                  { value: 'EXR2023', label: 'EXPO REAL 2023' },
                                  { value: 'AUT2023', label: 'automatica 2023' },
                                  { value: 'FRE2023', label: 'f.re.e 2023' },
                                ]
                              },
                              { 
                                label: '2022',
                                options: [
                                  { value: 'XXX2022', label: 'automatica | analytica | ceramitec 2022' },
                                ]
                              }
                            ]}
                    defaultValue={'EXPO REAL 2023'}
                    //onChange={handleChange}
                    //onSearch={onSearch}
                    name={'va'}
                    style={{ minWidth: 150 }}
                    optionFilterProp="label" // filter by label (not by value/key)
                  />
              </Space>
            </Col>
          </Row>
          <Dashboard dashboardItems={data && data.dashboardItems}>
            {data && data.dashboardItems.map(dashboardItem)}
          </Dashboard>
          <Row style={{paddingInline: "16px", paddingBlock: "6px"}}>
            <Col span={24} style={{textAlign:"right"}}>
              <Text style={{fontSize:"smaller"}}>Stand: 20.12.2023 14:48 Uhr</Text>
            </Col>
          </Row>          
        </React.Fragment>
      </CubeProvider>
    ) : <Empty />;
};

export default DashboardPage;

/*

{data && data.dashboardItems.map(deserializeItem).map(dashboardItem)}
      <Row style={{paddingInline: "16px", paddingBlock: "6px"}}>
        <Col span={6} style={{paddingInline: "16px", paddingBlock: "6px"}}>
          <DashboardItem key={1} itemId={1} title={"Onlinebestellungen"}>
          </DashboardItem>
        </Col>
        <Col span={6} style={{paddingInline: "16px", paddingBlock: "6px"}}>
          <DashboardItem key={1} itemId={1} title={"Tage bis VA-Ende"}>
          </DashboardItem>
        </Col>
        <Col span={12} style={{paddingInline: "16px", paddingBlock: "6px"}}>
          <DashboardItem key={1} itemId={1} title={"Tagesverlauf"}>
          </DashboardItem>
        </Col>
      </Row>
      <Row style={{paddingInline: "16px", paddingBlock: "6px"}}>
        <Col span={24} style={{textAlign:"right"}}>
          <Text style={{fontSize:"smaller"}}>Stand: 20.12.2023 14:48 Uhr</Text>
        </Col>
      </Row>

<RangePicker size='small' presets={rangePresets} onChange={onRangeChange} />

<ChartRenderer vizState={item.vizState} />
key={item.id} itemId={item.id} title={item.name}>
      react-grid-layout
        react-grid-item
          card
            head
              head-title
              card-extra
            body
              chart/statistic/...*/