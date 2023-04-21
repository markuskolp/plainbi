import React from "react";
import { useState } from "react";
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
  DatePicker
} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import NoPage from "./utils/NoPage";
import { EditOutlined, PlusOutlined } from "@ant-design/icons";
const { Header, Content, Sider } = Layout;

const { Text, Link } = Typography;

const AppRun = () => {
  let { id } = useParams();
  let id_type = Number.isNaN(id * 1) ? "alias" : "id";

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
              required: false
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
          table_columns: []
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

  function getColumn(column_label, column_name) {
    return {
      title: column_label,
      //dataIndex: column_name,
      key: column_name
      //width: 50,
      //render
    };
  }

  const columnItems = pageMetadataRelevant.table_columns.map((column) => {
    return getColumn(column.column_label, column.column_name);
  });
  //    .push(getColumnAction());

  function getColumnAction() {
    return {
      title: " ",
      key: "action",
      width: 25,
      render: (_, record) => (
        <Link onClick={showModal}>
          <EditOutlined style={{ fontSize: "18px" }} />
        </Link>
      )
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
            />
          </Sider>
          <Content style={{ background: "#FFF" }}>
            <PageHeader
              //onBack={() => window.history.back()}
              title=""
              subTitle=""
              extra={[
                <Button
                  //href="/apps/edit"
                  onClick={showModal}
                  key="1"
                  type="primary"
                  icon={<PlusOutlined />}
                >
                  Neu
                </Button>
                //todo: check if "create" action is allowed
              ]}
            />
            <Table
              size="small"
              columns={columnItems}
              dataSource={pageMetadataRelevant.name.table_columns}
              //pagination={{ pageSize: 50 }}
              pagination={false}
              //scroll={{ y: 500 }}
            />
            <Modal
              title={pageMetadataRelevant.name}
              open={isModalOpen}
              onOk={handleOk}
              onCancel={handleCancel}
              centered
              width={1000}
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
                            options={[
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
                            ]}
                          />
                        ) : column.ui === "hidden" ? (
                          ""
                        ) : column.ui === "numberinput" ? (
                          <InputNumber />
                        ) : column.ui === "textarea" ? (
                          <Input />
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

/*
    - Tabs left vertical with pages (<appname> and then the <pagenames>) -> add routing !
    - Breadcrumb (<appname> / <pagename>) (first page is default entry point)
    - Page header (pagename) + New button
    - Table + Edit button
    - Modal dialog with all columns as form items
                  datatype: "number", //text/number/date/boolean
              ui: "lookup", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch

*/

export default AppRun;

// <Text>url param: {id}</Text>
