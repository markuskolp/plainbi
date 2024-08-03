import React from "react";

import { Alert, Tabs, Card, Avatar, Form, Input, Button, Space , Typography } from "antd";
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { PageHeader } from "@ant-design/pro-layout";
import UnderConstruction from "../components/UnderConstruction";
import CRUDPage from "../components/CRUDPage";

const { Text, Link } = Typography;
const { Meta } = Card;
const { TextArea } = Input;

const Settings = (props) => {

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
  Globale Einstellungen
  Globale Logos
  Lookups für Applikationen
  Applikationen
  Rollen
  User
  Gruppen
  User zu Gruppen (Zuordnung)
  Applikationen zu Gruppen (Zuordnung)
  */

  
  const lookupSqlDescription = (
    <React.Fragment>
    <p>Das hinterlegte SQL muss genau 2 Spalten zurückliefern:</p>
    <ul><li>d: display</li><li>r: return</li></ul>
    <p>'display' wird zur <b>Anzeige</b> und 'return' wird zur <b>Speicherung</b> verwendet.</p>
    <span>Beispiel: </span><br/><b>select product_id as r, product_name as d from d_product;</b>
    </React.Fragment>
  )
  ;

  const crudDefinitions = [
    {
      id:"1", name:"Datenquellen", alias:"datasources",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"datasource",
      pk_columns:["id"],
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "alias", column_label: "Alias", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_type", column_label: "Datenbanktyp", datatype: "text", ui: "lookup", lookup: "db_type", editable: true, required: true },
        { column_name: "db_host", column_label: "Host", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_port", column_label: "Port", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_name", column_label: "Datenbank", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_user", column_label: "User", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "db_pass_hash", column_label: "Passwort", datatype: "text", ui: "password_nomem", editable: true, required: true, showdetailsonly:true  },
      ]
    }, 
    {
      id:"2", name:"Globale Einstellungen", alias:"settings",
      allowed_actions:["update"],
      datasource:"repo",
      table:"settings",
      pk_columns:["setting_name"],
      table_columns: [
        { column_name: "setting_name", column_label: "Einstellung", datatype: "text", ui: "textinput", editable: false, required: true },
        { column_name: "setting_value", column_label: "Wert", datatype: "text", ui: "textinput", editable: true, required: true }
      ]
    }, 
    {
      id:"3", name:"Globale Logos", alias:"logos",
      allowed_actions:["update"],
      datasource:"repo",
      table:"static_file",
      pk_columns:["id"],
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false, showdetailsonly:true },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: false, required: true },
        { column_name: "alias", column_label: "Alias", datatype: "text", ui: "textinput", editable: false, required: true, showdetailsonly:true },
        { column_name: "mimetype", column_label: "MIME-Typ", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "content_base64", column_label: "Inhalt (als base64)", datatype: "text", ui: "textarea_base64", editable: true, required: true, showdetailsonly:true  },
      ]
    }, 
    {
      id:"4", name:"Lookups für Applikationen", alias:"lookups",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"lookup",
      pk_columns:["id"],
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "alias", column_label: "Alias", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "sql_query", column_label: "SQL", datatype: "text", ui: "textarea", editable: true, required: true, showdetailsonly:true, tooltip:lookupSqlDescription  },
        { column_name: "datasource_id", column_label: "Datenquelle", datatype: "number", ui: "lookup",  lookup: "datasource", editable: true, required: true },
      ]
    }, 
    {
      id:"5", name:"Applikationen", alias:"apps",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"application",
      pk_columns:["id"],
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "alias", column_label: "Alias", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "spec_json", column_label: "Spezifikation (als JSON)", datatype: "text", ui: "textarea", editable: true, required: true, showdetailsonly:true },
        { column_name: "datasource_id", column_label: "Datenquelle", datatype: "number", ui: "lookup",  lookup: "datasource", editable: true, required: true },
      ]
    }, 
    {
      id:"6", name:"Rollen", alias:"roles",
      allowed_actions:[], //"create", "update", "delete"],
      datasource:"repo",
      table:"role",
      pk_columns:["id"],
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
      ]
    }, 
    {
      id:"7", name:"User", alias:"users",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"user",
      pk_columns:["id"],
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "username", column_label: "Username", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "email", column_label: "E-Mail", datatype: "text", ui: "email", editable: true, required: true },
        { column_name: "fullname", column_label: "Name (vollständig)", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "password_hash", column_label: "Passwort", datatype: "text", ui: "password_nomem", editable: true, required: true, showdetailsonly:true  },
        { column_name: "role_id", column_label: "Rolle", datatype: "number", ui: "lookup",  lookup: "role", editable: true, required: true },
      ]
    }, 
    {
      id:"8", name:"Gruppen", alias:"groups",
      allowed_actions:["create", "update", "delete"],
      datasource:"repo",
      table:"group",
      pk_columns:["id"],
      table_columns: [
        { column_name: "id", column_label: "ID", datatype: "number", editable: false, required: false },
        { column_name: "name", column_label: "Name", datatype: "text", ui: "textinput", editable: true, required: true },
        { column_name: "alias", column_label: "Alias", datatype: "text", ui: "textinput", editable: true, required: true },
      ]
    }, 
    {
      id:"9", name:"User zu Gruppen", alias:"users2groups",
      allowed_actions:["create", "delete"],
      datasource:"repo",
      table_for_list:"v_user_to_group",
      table:"user_to_group",
      pk_columns:["user_id","group_id"],
      table_columns: [ 
        { column_name: "user_id", column_label: "User", datatype: "number", ui: "lookup",  lookup: "user", editable: true, required: true, showdetailsonly: true  },
        { column_name: "group_id", column_label: "Gruppe", datatype: "number", ui: "lookup",  lookup: "group", editable: true, required: true, showdetailsonly: true },
        { column_name: "user_name", column_label: "User", datatype: "text", ui: "label", editable: false, required: false, showsummaryonly: true },
        { column_name: "group_name", column_label: "Gruppe", datatype: "text", ui: "label", editable: false, required: false, showsummaryonly: true },
      ]
    }, 
    {
      id:"10", name:"Applikationen zu Gruppen", alias:"apps2groups",
      allowed_actions:["create", "delete"],
      datasource:"repo",
      table_for_list:"v_application_to_group",
      table:"application_to_group",
      pk_columns:["application_id","group_id"],
      table_columns: [
        { column_name: "application_id", column_label: "Applikation", datatype: "number", ui: "lookup",  lookup: "application", editable: true, required: true, showdetailsonly: true },
        { column_name: "group_id", column_label: "Gruppe", datatype: "number", ui: "lookup",  lookup: "group", editable: true, required: true, showdetailsonly: true },
        { column_name: "application_name", column_label: "Applikation", datatype: "text", ui: "label", editable: false, required: false, showsummaryonly: true },
        { column_name: "group_name", column_label: "Gruppe", datatype: "text", ui: "label", editable: false, required: false, showsummaryonly: true },
      ]
    }
  ]
  ;

  
  function getLookups(table_columns) {
    const lookups = table_columns.filter((column) => column.ui === "lookup").map((column) => ( 
        column.lookup
      )
    );
    console.log("getLookups: " + lookups);
    return lookups;
  };


  const items = crudDefinitions.map((obj) => {
    return getItem(obj.name // label
        , obj.id // key
        , null // icon
        , <CRUDPage key={obj.name} name={obj.name} tableName={obj.table} tableForList={obj.table_for_list} tableColumns={obj.table_columns} pkColumns={obj.pk_columns} allowedActions={obj.allowed_actions} datasource={obj.datasource} isRepo="true" lookups={getLookups(obj.table_columns)} token={props.token}/>
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
