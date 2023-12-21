import React from "react";
import Table from "../components/Table";
import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { Alert, Button, notification, Form, Collapse, Typography,Tooltip, Card , Col, Row, Select, Space, DatePicker, Menu, Dropdown, Input} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { FullscreenOutlined, MoreOutlined, HistoryOutlined } from "@ant-design/icons";
import LoadingMessage from "../components/LoadingMessage";
import { message } from "antd";
import Axios from "axios";
import GridLayout from "react-grid-layout";
import DashboardItem from "../components/DashboardItem";

import dayjs from 'dayjs';

const { Title, Link, Text } = Typography;
import "../css/dashboard.css";

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

const DashboardPage = (props) => {

  const [dashboard, setDashboard] = useState([]);
  dashboard.name = 'Tickets';

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


  return (
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
    </React.Fragment>
  );
};

export default DashboardPage;

/*

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