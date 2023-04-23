import React from "react";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Table,
  Button,
  Typography,
  Layout,
  Menu,
  Modal,
  Switch,
  Form,
  Input,
  Select,
  InputNumber,
  DatePicker,
  Space,
  Popconfirm,
  message
} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import NoPage from "./utils/NoPage";
import { EditOutlined, PlusOutlined, ExclamationCircleFilled, DeleteOutlined } from "@ant-design/icons";
import Axios from "axios";
import Title from "antd/es/skeleton/Title";
import getData from "./utils/getData";
const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Text, Link } = Typography;

const AppRun = () => {
  let { id } = useParams(); // get URL parameters - here the "id" of a app
  let id_type = Number.isNaN(id * 1) ? "alias" : "id"; // check whether the "id" refers to the real "id" of the app or its "alias"

  const [lookupdata, setlookupdata] = useState([]);
  const [tabledata, settabledata] = useState([]);
  const [loading, setloading] = useState(true);
  const [page, setPage] = useState(true);

  useEffect(() => {
    getLookupData();
    getTableData();
  }, []);
  
  const getLookupData = async () => {
//    async function getLookupData(lookupid) {
    //console.log('fetching lookup', lookupid);
    await Axios.get("/api/data/lookup/ADHOC_AUSGABEFORMAT.json").then(
      (res) => {
        setlookupdata(
          res.data.map((row) => ({
            value: row.r,
            label: row.d
          }))
        );
        //setloading(false);
      }
    );
  };

  /*
  const tableData = () => {  
    const { data } = getData("/api/data/table/KFG_ADHOC.json");
    return data;
  }
  */

  const getTableData = async () => {
    
        await Axios.get("/api/data/table/"+appMetadataRelevant.pages[page-1].table+".json").then(
          (res) => {
            console.log(JSON.stringify(res.data));
            settabledata(res.data);
            console.log(JSON.stringify(tabledata));
            setloading(false);
          }
        );
      };

  const [isModalOpen, setIsModalOpen] = useState(false);

  const showModal = () => {
    setIsModalOpen(true);
  };

  const handleOk = () => {
    setIsModalOpen(false);
  };

  const handleCancel = () => {
    setIsModalOpen(false);
  };


  const deleteConfirm = (e) => {
    console.log(e);
    message.success('Wurde gelöscht.');
  };



  //const [form] = Form.useForm();
  //const formValueAlias = Form.useWatch("alias", form);

  const layout = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 }
  };
  const layoutpage = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 }
  };

  const onReset = () => {
    //
  };


  // metadata of all applications
  // todo: fetch this from API !
  const appMetadata = [
    {
      id: "1",
      name: "DWH Administration",
      alias: "dwh_admin",
      pages: [
        {
          id: "1",
          name: "Mailingliste",
          alias: "mailing",
          allowed_actions: ["create", "update", "delete"],
          table: "PAR_MAILING_LIST",
          table_columns: [
            {
              column_name: "ID_FAIREVENT",
              column_label: "Veranstaltung",
              datatype: "number", //text/number/date/boolean
              ui: "lookup", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              lookup: "VERANSTALTUNG",
              editable: true,
              required: true
            },
            {
              column_name: "SUBJECT",
              column_label: "Thema",
              datatype: "text", //text/number/date/boolean
              ui: "textinput", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              editable: true,
              required: true
            },
            {
              column_name: "RECIPIENT",
              column_label: "E-mail Empfänger",
              datatype: "text", //text/number/date/boolean
              ui: "textinput", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              editable: true,
              required: true
            },
            {
              column_name: "RECIPIENT_CC",
              column_label: "E-mail CC",
              datatype: "text", //text/number/date/boolean
              ui: "textinput", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              editable: true,
              required: false
            },
            {
              column_name: "ACTIVE",
              column_label: "ist aktiv",
              datatype: "boolean", //text/number/date/boolean
              ui: "switch", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              editable: true,
              required: true
            },
            {
              column_name: "...",
              column_label: "...",
              datatype: "...", //text/number/date/boolean
              ui: "...", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              editable: false,
              required: false,
              showdetailsonly: true
            }
          ]
        },
        {
          id: "2",
          name: "Veranstaltungen",
          alias: "va",
          allowed_actions: ["update"],
          table: "PAR_FAIREVENT_GENERAL"
        },
        {
          id: "3",
          name: "Veranstaltungen - Golden Gate",
          alias: "va_gg",
          allowed_actions: ["update"],
          table: "PAR_FAIREVENT_GOLDEN_GATE"
        }
      ]
    },
    {
      id: "2",
      name: "Adhoc Konfiguration",
      alias: "adhoc",
      pages: [
        {
          id: "1",
          name: "Adhocs",
          alias: "all",
          allowed_actions: ["create", "update", "delete"],
          table: "KFG_ADHOC",
          table_columns: [
            {
              column_name: "adhoc_id",
              column_label: "ID",
              datatype: "number", //text/number/date/boolean
              editable: false,
              required: true
            },
            {
              column_name: "adhoc_name",
              column_label: "Adhoc Name",
              datatype: "text", //text/number/date/boolean
              ui: "textinput", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              editable: true,
              required: true
            },
            {
              column_name: "sql_query",
              column_label: "SQL Abfrage",
              datatype: "text", //text/number/date/boolean
              ui: "textarea", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              editable: true,
              required: true,
              showdetailsonly: true,
            },
            {
              column_name: "output_format",
              column_label: "Ausgabeformat",
              ui: "lookup", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch
              lookup: "ADHOC_AUSGABEFORMAT",
              datatype: "text", //text/number/date/boolean
              editable: true,
              required: true
            },
          ]
        }
      ]
    }
  ];

  let appIndex = -1;
  let pageIndex = 0;
  if (id_type === "id") {
    console.log("type id");
    appIndex = appMetadata.findIndex((x) => x.id === id);
    console.log(appIndex);
  } else {
    console.log("type alias");
    appIndex = appMetadata.findIndex((x) => x.alias === id);
    console.log(appIndex);
  }

  const appMetadataRelevant = appMetadata[appIndex === -1 ? 0 : appIndex];
  const pageMetadataRelevant = appMetadataRelevant.pages[pageIndex];

  const create_allowed = pageMetadataRelevant.allowed_actions.includes("create");
  const edit_allowed = pageMetadataRelevant.allowed_actions.includes("edit");
  const delete_allowed = pageMetadataRelevant.allowed_actions.includes("delete");

  function getColumn(column_label, column_name) {
    return {
      title: column_label,
      dataIndex: column_name,
      //key: column_name
      //width: 50,
      //render
    };
  }

  const columnItems = pageMetadataRelevant.table_columns.map((column) => {
    return getColumn(column.column_label, column.column_name);
  });
  const columnItemsForSummary = pageMetadataRelevant.table_columns
    .filter((column) => !column.showdetailsonly) // show all columns, that are not limited to the detail view (modal)
    .map((column) => {
      return getColumn(column.column_label, column.column_name);
    })
    .concat(getColumnAction(true, true))
  ;
  
  //    .push(getColumnAction(true, true));

  function getColumnAction(delete_allowed, edit_allowed) {
    return {
      title: " ",
      key: "action",
      width: 100,
      render: (_, record) => ([
        <Space>
          {delete_allowed && 
            <Popconfirm
            title="Löschen"
            description="Wirklich löschen?"
            onConfirm={deleteConfirm}
            //onCancel={cancel}
            okText="Ja"
            cancelText="Nein"
            //<Link onClick={(e) => { this.onDelete(record.key, e); }}>
            >
            <DeleteOutlined style={{ fontSize: "18px" }} />
            </Popconfirm>
          }
          {edit_allowed && 
          <Link onClick={showModal}>
            <EditOutlined style={{ fontSize: "18px" }} />
          </Link>
          }
        </Space>
      ])
    };
  }

  function getItem(label, key, icon, children, type) {
    return {
      key,
      icon,
      children,
      label,
      type
    };
  }
  const pageItems = appMetadataRelevant.pages.map((page) => {
    return getItem(page.name, page.id);
  });

  const [mode, setMode] = useState("inline");
  const [theme, setTheme] = useState("light");


  const menuOnClick = (e) => {
    console.log('set page to id: ', e.key);
    setPage(e.key);
    getTableData();
    //setPagemetadatarelevant(appmetadatarelevant.pages[page-1])
  };

  return appIndex === -1 ? (
    <NoPage />
  ) : (
    <React.Fragment>
      <Layout className="layout">
        <Header className="pageheader">{appMetadataRelevant.name}</Header>
        <Layout>
          <Sider width={250} theme={theme}>
            <Menu
              style={{ width: 250, marginTop: "25px" }}
              defaultSelectedKeys={["1"]}
              defaultOpenKeys={["1"]}
              mode={mode}
              theme={theme}
              items={pageItems}
              onClick={menuOnClick}
            />
          </Sider>
          <Content style={{ background: "#FFF" }}>
            <PageHeader
              //onBack={() => window.history.back()}
              title=""
              subTitle=""
              extra={[
                create_allowed && 
                <Button
                  //href="/apps/edit"
                  onClick={showModal}
                  key="1"
                  type="primary"
                  icon={<PlusOutlined />}
                >
                  Neu
                </Button>
                
              ]}
            />
                <Table
                  size="small"
                  columns={columnItemsForSummary} 
                  dataSource={tabledata}
                  //dataSource={pageMetadataRelevant.name.table_columns}
                  //pagination={{ pageSize: 50 }}
                  pagination={false}
                  //scroll={{ y: 500 }}
                  //loading={loading}
            /> 
            
            <Modal
              title={pageMetadataRelevant.name}
              open={isModalOpen}
              onOk={handleOk}
              onCancel={handleCancel}
              centered
              width={1000}
              footer={[
                /*delete_allowed && <Button
                  key="1"
                  danger
                  htmlType="button"
                  icon={<DeleteOutlined />}
                  onClick={showDeleteConfirm}
                >Löschen</Button>,
                */
                <Button
                  key="2"
                  htmlType="button"
                  onClick={handleCancel}
                >Abbrechen</Button>,
                <Button
                  key="3"
                  type="primary"
                  htmlType="submit"
                  onClick={handleOk}
                >Speichern</Button>
              ]}
              
            >
              <Form {...layoutpage} layout="horizontal">
                {pageMetadataRelevant.table_columns.map((column) => {
                  return (
                    <React.Fragment>
                      <Form.Item
                        name={column.column_name}
                        label={column.column_label}
                        rules={[{ required: column.required }]}
                      >
                        {!column.editable ? (
                          <Text>...</Text>
                        ) : column.ui === "lookup" ? (
                          <Select
                            placeholder="bitte auswählen ..."
                            allowClear
                            showSearch
                            options={lookupdata}
                              /*[
                              {
                                value: "f.re.e 2023",
                                label: ""
                              },
                              {
                                value: "LOPEC 2023",
                                label: ""
                              },
                              {
                                value: "...",
                                label: "..."
                              }
                              ]
                          }*/
                          />
                        ) : column.ui === "hidden" ? (
                          ""
                        ) : column.ui === "numberinput" ? (
                          <InputNumber />
                        ) : column.ui === "textarea" ? (
                          <TextArea rows={6} />
                        ) : column.ui === "textinput" ? (
                          <Input />
                        ) : column.ui === "datepicker" ? (
                          <DatePicker />
                        ) : column.ui === "switch" ? (
                          <Switch />
                        ) : (
                          <Text>?</Text>
                        )}
                      </Form.Item>
                    </React.Fragment>
                  );
                })}
              </Form>
            </Modal>
          </Content>
        </Layout>
      </Layout>
    </React.Fragment>
  );
};


export default AppRun;

