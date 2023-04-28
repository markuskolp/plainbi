import React from "react";

import { Alert, Tabs, Card, Avatar, Form, Input, Button, Space , Typography } from "antd";
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { PageHeader } from "@ant-design/pro-layout";
import UnderConstruction from "../components/UnderConstruction";
import CRUDPage from "../components/CRUDPage";

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

  /*
  Datenquellen
  Lookups für Applikationen
  Applikationen
  Rollen
  User
  Gruppen
  User zu Gruppen (Zuordnung)
  Applikationen zu Gruppen (Zuordnung)
  */

  const crudDefinitions = [
    {
      id:"1", name:"Datenquellen", alias:"datasources",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"datasource",
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_type", column_label: "Datenbanktyp", datatype: "text", ui: "lookup", lookup: "db_type", editable: true, required: true },
        { column_name: "db_host", column_label: "Host", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_port", column_label: "Port", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_name", column_label: "Datenbank", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_user", column_label: "User", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_pass_hash", column_label: "Passwort", datatype: "text", ui: "password", editable: true, required: true, showdetailsonly:true  },
      ]
    }, 
    {
      id:"2", name:"Lookups für Applikationen", alias:"lookups",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"lookup",
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "sql_query", column_label: "SQL", datatype: "text", ui: "textarea_sql", editable: true, required: true, showdetailsonly:true  },
        { column_name: "datasource_id", column_label: "Datenquelle", datatype: "number", ui: "lookup",  lookup: "datasource", editable: true, required: true },
      ]
    }, 
    {
      id:"3", name:"Applikationen", alias:"apps",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"application",
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "alias", column_label: "Alias", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "spec_json", column_label: "Spezifikation (als JSON)", datatype: "text", ui: "textarea_json", editable: true, required: true, showdetailsonly:true },
        { column_name: "datasource_id", column_label: "Datenquelle", datatype: "number", ui: "lookup",  lookup: "datasource", editable: true, required: true },
      ]
    }, 
    {
      id:"4", name:"Rollen", alias:"roles",
      allowed_actions:[], //"create", "update", "delete"],
      datasource:"repo",
      table:"role",
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
      ]
    }, 
    {
      id:"5", name:"User", alias:"users",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"user",
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "username", column_label: "Username", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "email", column_label: "E-Mail", datatype: "text", ui: "email", editable: true, required: true },
        { column_name: "fullname", column_label: "Name (vollständig)", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "password_hash", column_label: "Passwort", datatype: "text", ui: "password", editable: true, required: true, showdetailsonly:true  },
        { column_name: "role_id", column_label: "Rolle", datatype: "number", ui: "lookup",  lookup: "role", editable: true, required: true },
      ]
    }, 
    {
      id:"6", name:"Gruppen", alias:"groups",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"group",
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
      ]
    }, 
    {
      id:"7", name:"User zu Gruppen (Zuordnung)", alias:"users2groups",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"user_to_group",
      table_columns: [
        { column_name: "user_id", column_label: "User", datatype: "number", ui: "lookup",  lookup: "user", editable: true, required: true },
        { column_name: "group_id", column_label: "Gruppe", datatype: "number", ui: "lookup",  lookup: "group", editable: true, required: true },
      ]
    }, 
    {
      id:"8", name:"Applikationen zu Gruppen (Zuordnung)", alias:"apps2groups",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"application_to_group",
      table_columns: [
        { column_name: "application_id", column_label: "Applikation", datatype: "number", ui: "lookup",  lookup: "application", editable: true, required: true },
        { column_name: "group_id", column_label: "Gruppe", datatype: "number", ui: "lookup",  lookup: "group", editable: true, required: true },
      ]
    }
  ]
  ;

  const items = crudDefinitions.map((obj) => {
    return getItem(obj.name // label
        , obj.id // key
        , null // icon
        , <CRUDPage name={obj.name} table={obj.table} tableColumns={obj.table_columns} allowedActions={obj.allowed_actions} /> // children
        , null // type
        );
  })

  // return a item to be rendered in a Menu component
  function getItem(label, key, icon, children, type) {
    return {
      key,
      icon,
      children,
      label,
      type
    };
  }


/*
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
      label: `Datenquellen`,
      children: <React.Fragment>
          <Card style={{ backgroundColor: 'rgb(220,220,220,0.3)', border:'none', width: 200, marginTop: 16, marginLeft: 160 }} hoverable={true} type="inner" cover={<img alt="Logo MS SQL Server" src="/static/mssql.svg" height="50"/>}>
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
      label: `Applikationen`,
      children: <React.Fragment>
                    {crudDefinitionApplication && 
                    <CRUDPage name={crudDefinitionApplication.name} table={crudDefinitionApplication.table} tableColumns={crudDefinitionApplication.table_columns} allowedActions={crudDefinitionApplication.allowed_actions} />
                    }
                </React.Fragment>
    },
    {
      key: '4',
      label: `Rollen`,
      children: <React.Fragment>
                    {crudDefinitionRole && 
                    <CRUDPage name={crudDefinitionRole.name} table={crudDefinitionRole.table} tableColumns={crudDefinitionRole.table_columns} allowedActions={crudDefinitionRole.allowed_actions} />
                    }
                </React.Fragment>
    },
    {
      key: '5',
      label: `User`,
      children: <React.Fragment><UnderConstruction /></React.Fragment>
    },
    {
      key: '6',
      label: `Gruppen`,
      children: <React.Fragment><UnderConstruction /></React.Fragment>
    },
    {
      key: '7',
      label: `User zu Gruppen (Zuordnung)`,
      children: <React.Fragment><UnderConstruction /></React.Fragment>
    },
    {
      key: '8',
      label: `Applikationen zu Gruppen (Zuordnung)`,
      children: <React.Fragment><UnderConstruction /></React.Fragment>
    }
  ];
*/

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
