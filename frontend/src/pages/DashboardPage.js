import React from "react";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Table from "../components/Table";
import { Alert, Button, Typography,Tooltip, Col, Row, Select, Space, DatePicker, Menu, Dropdown, Input} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { FullscreenOutlined, MoreOutlined, HistoryOutlined, EditOutlined, SaveOutlined } from "@ant-design/icons";
import DashboardItem from "../components/dashboard/DashboardItem";
import ChartRenderer from "../components/dashboard/ChartRenderer";
import Dashboard from "../components/dashboard/Dashboard";
import MemberSelect from "../components/dashboard/MemberSelect";
import cubejs from "@cubejs-client/core";
import { CubeProvider } from "@cubejs-client/react";
import { dashboards } from "../api/dashboards";
import NoPage from "./NoPage";
import { message } from "antd";
import { DrilldownModal } from "../components/dashboard/DrilldownModal/DrilldownModal";
import dayjs from 'dayjs';
const { Title, Link, Text } = Typography;
import "../css/dashboard.css";

const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDI2NjYzNDcsImV4cCI6MTcwMjc1Mjc0N30.D8iCMGAH72GgOjNm6dWuFWHStlrzVVAEpomOk4eKK5Y';
const cubejsApi = cubejs(token, { apiUrl: '/cubejs-api/v1' });

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

  let { id } = useParams(); // get URL parameters - here the "id" of a app
  let id_type = Number.isNaN(id * 1) ? "alias" : "id"; // check whether the "id" refers to the real "id" of the app or its "alias"

  console.log("DashboardPage - id: " + id);
  console.log("DashboardPage - id_type: " + id_type);
  //const data = dashboards[0]; //JSON.parse(defaultDashboardItems);
  const data = (id_type === 'id' ? dashboards.filter((dashboard)=> dashboard.id === Number(id)) : dashboards.filter((dashboard)=> dashboard.alias === id))[0];
  console.log(data);

  //const { loading, error, data } = useQuery(GET_DASHBOARD_ITEMS);
  const loading = false;
  const error = false;
  const [dashboardFilter, setDashboardFilter] = useState(null);
  const [editable, setEditable] = useState(false);
  const [drillDownQuery, setDrillDownQuery] = useState();
  const [open, setOpen] = useState(false);

  if (loading) {
    return <Spin />;
  }

  if (!data) {
    message.error('Es gab einen Fehler beim Laden des Dashboards.')
    return (
      <NoPage />
    );
  }

  if (error) {
    return (
      <Alert
        message="Es wurde kein Dashboard gefunden."
        description={error.toString()}
        type="error"
      />
    );
  }

  function openFullscreen() {
    if (document.fullscreenElement) {
      // If there is a fullscreen element, exit full screen.
      document.exitFullscreen();
      return;
    }
    var elem = document.getElementsByTagName("main")[0];
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) { /* Safari */
      elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { /* IE11 */
      elem.msRequestFullscreen();
    }
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

  const handleClose = () => {
    setOpen(false);
  };

  const handleDrill = (drillQuery) => {
    console.log("handleDrill");
    console.log("drillQuery");
    console.log(drillQuery);
    setDrillDownQuery(drillQuery);
    setOpen(true);
  };

  const dashboardItem = item => (
    <div key={item.id} data-grid={defaultLayout(item)}>
      <DashboardItem key={item.id} itemId={item.id} title={item.name} editable={editable}>
        {dashboardFilter ? (
            <ChartRenderer vizState={replaceVizStateFilters(item.vizState, dashboardFilter.name, dashboardFilter.value)} handleDrill={handleDrill} /> 
          ) : (
            <ChartRenderer vizState={item.vizState} handleDrill={handleDrill} /> 
          )
        }
      </DashboardItem>
    </div>
  );
  //<ChartRenderer vizState={replaceVizStateFilters(item.vizState, dashboardFilter.name, dashboardFilter.value)} /> 
  //<ChartRenderer vizState={item.vizState} /> 

  //item.vizState -> if dashboardFilter, then put this filter in here or replace an existing one !
  const replaceVizStateFilters = (vizState, filterName, filterValue) => {
    const vizStateNew = vizState;
    const vizStateOriginal = vizState;
    try {
      console.log("replaceVizStateFilters: vizState");
      console.log(vizState);
      console.log("replaceVizStateFilters: filterName");
      console.log(filterName);
      console.log("replaceVizStateFilters: filterValue");
      console.log(filterValue);

      // check if filter exists
      // if filter exists, delete it
      let filtersReplaced = vizState.query.filters.filter((el) => el.member != filterName);
      console.log("replaceVizStateFilters: filtersReplaced - delete existing");
      console.log(filtersReplaced);

      // add dashboard filter
      filtersReplaced.push({
                      "member": filterName,
                      "operator": "equals",
                      "values": [filterValue]
                    });
      console.log("replaceVizStateFilters: filtersReplaced - push new one");
      console.log(filtersReplaced);
                            

      // take vizState from beginning and delete all filters and add newly created filter array
      //delete vizState.query.filters;
      vizState.query.filters = filtersReplaced;
      console.log("replaceVizStateFilters: vizState - new");
      console.log(vizState);
      vizStateNew.query = vizState.query;
      //return vizState;
      return vizStateNew;
    } catch (err) {
      console.log("replaceVizStateFilters: error");
      console.log(err.message);
      return vizStateOriginal;
    }

  }

  
  const handleChangeSelectVA = (filterName, filterValue) =>{
    console.log("handleChangeSelectVA - filterName: " + filterName);
    console.log("handleChangeSelectVA - filterValue: " + filterValue);
    setDashboardFilter({"name":filterName, "value":filterValue}); 
  }


  return !data || data.dashboardItems.length  ? (
      <CubeProvider cubejsApi={cubejsApi}>
        <React.Fragment>
          <PageHeader
            //onBack={() => (window.location.href = "/")}
            title={data.dashboardName}
            subTitle=""
            //style={{ background: 'white' }}
            extra={[
              <Space>
                {!editable ? (
                    <Link onClick={(e) => { setEditable(true, e); }}>
                      <Tooltip title="Dashboard bearbeiten">
                        <EditOutlined />
                      </Tooltip>
                    </Link>
                  ) : (
                    <Link onClick={(e) => { setEditable(false, e); }}>
                      <Tooltip title="Änderungen speichern">
                        <SaveOutlined />
                      </Tooltip>
                    </Link>
                  )
                }
                <Link href="#">
                  <Tooltip title="Vollbild">
                    <Button type="text" icon={<FullscreenOutlined />} onClick={openFullscreen}/>
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
                {data.dashboardFilters && data.dashboardFilters.map((dashboardFilter) => { 
                  return (
                    dashboardFilter.type === 'lookup' ? <MemberSelect query={dashboardFilter.query} columnId={dashboardFilter.columnId} columnLabel={dashboardFilter.columnLabel} defaultValue={dashboardFilter.defaultValue} onChange={handleChangeSelectVA} /> : ""
                  )
                })}
                {data.data_status ? <ChartRenderer vizState={data.data_status.vizState} />  : "" }
              </Space>
            </Col>
          </Row>
          <Dashboard dashboardItems={data && data.dashboardItems} editable={editable} >
            {data && data.dashboardItems.map(dashboardItem)}
          </Dashboard>
          <DrilldownModal query={drillDownQuery} open={open} onClose={handleClose}/>
        </React.Fragment>
      </CubeProvider>
    ) : <Empty />;
};

export default DashboardPage;

// {data.dashboardFilter ? <MemberSelect query={data.dashboardFilter.query} columnId={data.dashboardFilter.columnId} columnLabel={data.dashboardFilter.columnLabel} defaultValue={data.dashboardFilter.defaultValue} onChange={handleChangeSelectVA} /> : ""}

//{data.data_status ? <ChartRenderer vizState={data.data_status.vizState} />  : "" }
//{data.data_status ? <ChartRenderer vizState={replaceVizStateFilters(data.data_status.vizState, dashboardFilter.name, dashboardFilter.value)} />  : "" }

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
              chart/statistic/...
              
              
              
              

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
              
              
              
              
              
*/