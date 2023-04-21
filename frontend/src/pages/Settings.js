import React from "react";

import { Alert, Tabs, Card, Avatar, Form, Input, Button, Space , Typography } from "antd";
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { PageHeader } from "@ant-design/pro-layout";
import UnderConstruction from "./utils/UnderConstruction";

const { Text, Link } = Typography;
const { Meta } = Card;
const { TextArea } = Input;

const Settings = () => {

  const [form] = Form.useForm();

  const layout = {
    labelCol: { span: 4 },
    wrapperCol: { span: 14 }
  };
  const tailLayout = {
    wrapperCol: { offset: 4, span: 16 },
  };
  
  
  const descriptionSQL = (
    <React.Fragment>
    <p>Das hinterlegte SQL muss genau 2 Spalten zurückliefern:</p>
    <ul><li>d: display</li><li>r: return</li></ul>
    <p>'display' wird zur <b>Anzeige</b> und 'return' wird zur <b>Speicherung</b> verwendet.</p>
    <span>Beispiel: </span><Text keyboard>select product_id as r, product_name as d from d_product;</Text>
    </React.Fragment>
  )

  const items = [
    {
      key: '1',
      label: `Datenquelle`,
      children: <React.Fragment>
          <Card style={{ backgroundColor: 'rgb(220,220,220,0.3)', border:'none', width: 200, marginTop: 16, marginLeft: 160 }} hoverable={true} type="inner" cover={<img alt="Logo MS SQL Server" src="static/mssql.svg" height="50"/>}>
            <Meta
              //avatar={<Avatar src="/mssql.svg" />}
              title="MS SQL Server"
              description=""
              style={{textAlign:'center'}}
            />
          </Card>
          <br/>
          <br/>
          <Form {...layout} layout="horizontal" form={form}>
            <Form.Item name="hostname" label="Hostname" rules={[{ required: true }]}>
              <Input placeholder="Hostname" defaultValue="vntsv147"/>
            </Form.Item>
            <Form.Item name="port" label="Port" rules={[{ required: true }]}>
              <Input placeholder="Port" defaultValue="1533"/>
            </Form.Item>
            <Form.Item name="database" label="Database" rules={[{ required: true }]}>
              <Input placeholder="Database" defaultValue="MM_DWH_STAGE"/>
            </Form.Item>
            <Form.Item name="username" label="Username" rules={[{ required: true }]}>
              <Input placeholder="Username" defaultValue="portal_user"/>
            </Form.Item>
            <Form.Item name="password" label="Password" rules={[{ required: true }]}>
              <Input.Password placeholder="Password" />
            </Form.Item>
            <Form.Item {...tailLayout}>
              <Space size="middle">
                <Button htmlType="button" >
                  Verbindung testen
                </Button>
                <Button type="primary" htmlType="submit">
                  Speichern
                </Button>
              </Space>
            </Form.Item>
          </Form>

      </React.Fragment>
    },
    {
      key: '2',
      label: `Lookups für Applikationen`,
      children: <React.Fragment>
       <Form
    name="dynamic_form_lookup_items"
    //onFinish={onFinish}
    style={{
      maxWidth: 600,
    }}
    autoComplete="off"
  >
    <Form.List name="lookups" initialValue={[
              { lookup: "Veranstaltungen", sql: "select \n  df.id_fairevent as r, \n  df.fairevent_name_year as d \nfrom mm_dwh_dev.dds.dim_fairevent df \nwhere 1=1 \nand df.active = 1 \norder by 2 " },
            ]}>
      {(fields, { add, remove }) => (
        <React.Fragment>
          {fields.map(({ key, name, ...restField }) => (
            <Space
              key={key}
              style={{
                display: 'flex',
                marginBottom: 8,
              }}
              align="start"
            >
              <Form.Item
                {...restField}
                name={[name, 'lookup']}
                rules={[
                  {
                    required: true,
                    message: 'Name für Lookup fehlt',
                  },
                ]}
              >
                <Input placeholder="Name für Lookup" style={{width: 300}}/>
              </Form.Item>
              <Form.Item
                {...restField}
                name={[name, 'sql']}
                rules={[
                  {
                    required: true,
                    message: 'SQL fehlt',
                  },
                ]}
              >
                <TextArea className="sqlcode" rows={8} placeholder="SQL (max. 4000 Zeichen)" maxLength={4000} style={{width: 400 }}/>
              </Form.Item>
              <MinusCircleOutlined onClick={() => remove(name)} />
            </Space>
          ))}
          <Form.Item>
            <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
              Lookup hinzufügen
            </Button>
          </Form.Item>
        </React.Fragment>
      )}
    </Form.List>
    <Form.Item>
      <Button type="primary" htmlType="submit">
        Speichern
      </Button>
    </Form.Item>
  </Form>
  <Alert
      description={descriptionSQL}
      type="info"
      showIcon
    />
      </React.Fragment>
    },
    {
      key: '3',
      label: `Gruppen`,
      children: <React.Fragment><UnderConstruction /></React.Fragment>
    },
    {
      key: '4',
      label: `User`,
      children: <React.Fragment><UnderConstruction /></React.Fragment>
    },
    {
      key: '5',
      label: `...`,
      children: <React.Fragment><UnderConstruction /></React.Fragment>
    }
  ];

  return (
    <React.Fragment>
      <PageHeader
        onBack={() => window.history.back()}
        title="Einstellungen"
        subTitle=""
      />
      <br/>
      <br/>
      <Tabs defaultActiveKey="1" items={items} tabPosition='left' />
    </React.Fragment>
  );
};

export default Settings;
