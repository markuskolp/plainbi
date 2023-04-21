import React, { useState } from "react";
import { useParams } from "react-router-dom";
import {
  Divider,
  DatePicker,
  InputNumber,
  Switch,
  Select,
  Button,
  Form,
  Input,
  Radio,
  Typography,
  Space,
  Tooltip,
  Table,
  Tag,
  Modal,
  Tabs
} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import {
  DeleteOutlined,
  SaveOutlined,
  PaperClipOutlined,
  EditOutlined,
  PlusOutlined,
  ReloadOutlined
} from "@ant-design/icons";

const { TextArea } = Input;
const { Text, Link } = Typography;

const AppEdit = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  let { id } = useParams();
  let mode = id ? "edit" : "create";
  let title = id ? "Pflegeapplikation ändern" : "Pflegeapplikation erstellen";

  const showModal = () => {
    setIsModalOpen(true);
  };

  const handleOk = () => {
    setIsModalOpen(false);
  };

  const handleCancel = () => {
    setIsModalOpen(false);
  };

  const [form] = Form.useForm();
  const formValueAlias = Form.useWatch("alias", form);

  const layout = {
    labelCol: { span: 4 },
    wrapperCol: { span: 14 }
  };
  const layoutpage = {
    labelCol: { span: 4 },
    wrapperCol: { span: 14 }
  };

  const onReset = () => {
    //
  };

  const copyAliasToClipboard = () => {
    try {
      navigator.clipboard.writeText(formValueAlias);
      console.log("Content copied to clipboard");
    } catch (err) {
      console.error("Failed to copy: ", err);
    }
  };

  const dataPages = [
    {
      id: "1",
      name: "Mailingliste",
      alias: "mailing",
      allowed_actions: [
        "create",
        "update",
        "delete"
        /*{
          action: "create"
        },
        {
          action: "update"
        },
        {
          action: "delete"
        }
        */
      ],
      table: "PAR_MAILING_LIST"
      /*,
      table_columns: [
        {
          name: "ID_FAIREVENT",
          type: "lookup",
          lookup: "FAIREVENT"
        },
        {
          name: "SUBJECT",
          type: "text"
        }
      ]*/
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
  ];

  var color;

  const columnsPages = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
      width: 20
    },
    {
      title: "Seitenname",
      dataIndex: "name",
      key: "name",
      width: 50
    },
    {
      title: "Alias",
      dataIndex: "alias",
      key: "alias",
      width: 50
    },
    {
      title: "Tabelle",
      dataIndex: "table",
      key: "table",
      width: 100
    },
    {
      title: "Erlaubte Aktionen",
      dataIndex: "allowed_actions",
      key: "allowed_actions",
      width: 50,
      render: (_, { allowed_actions }) => (
        <React.Fragment>
          {allowed_actions.map((tag) => {
            if (tag === "create") {
              color = "green";
            }
            if (tag === "update") {
              color = "geekblue";
            }
            if (tag === "delete") {
              color = "volcano";
            }
            return (
              <Tag color={color} key={tag}>
                {tag.toUpperCase()}
              </Tag>
            );
          })}
        </React.Fragment>
      )
    },
    {
      title: " ",
      key: "action",
      width: 25,
      render: (_, record) => (
        <Link onClick={showModal}>
          <EditOutlined style={{ fontSize: "18px" }} />
        </Link>
      )
    }
  ];

  const items = [
    {
      key: "1",
      label: `Allgemein`,
      children: (
        <React.Fragment>
          <Form {...layout} layout="horizontal" form={form}>
            <Form.Item name="name" label="Name" rules={[{ required: true }]}>
              <Input placeholder="Applikationsname" />
            </Form.Item>
            <Form.Item name="alias" label="Alias" rules={[{ required: true }]}>
              <Input placeholder="eindeutige Alias" />
            </Form.Item>
            <Form.Item label="URL">
              <Space>
                <Text>/apps/{formValueAlias}</Text>
                <Link onClick={copyAliasToClipboard}>
                  <Tooltip title="in Zwischenablage kopieren">
                    <PaperClipOutlined />
                  </Tooltip>
                </Link>
              </Space>
            </Form.Item>
          </Form>
        </React.Fragment>
      )
    },
    {
      key: "2",
      label: `Seiten`,
      children: (
        <React.Fragment>
          <PageHeader
            title=" "
            subTitle=""
            extra={[
              <Button
                key="1"
                type="primary"
                icon={<PlusOutlined />}
                onClick={showModal}
              >
                Neue Seite
              </Button>
            ]}
          />
          <Table
            size="small"
            columns={columnsPages}
            dataSource={dataPages}
            //pagination={{ pageSize: 50 }}
            pagination={false}
            //scroll={{ y: 500 }}
          />
        </React.Fragment>
      )
    }
  ];

  const columnsTableColumns = [
    {
      title: "Name",
      dataIndex: "column_name",
      key: "column_name",
      width: 50
    },
    {
      title: "Anzeigename",
      dataIndex: "column_label",
      key: "column_label",
      width: 50
    },
    {
      title: "Datentyp",
      dataIndex: "datatype",
      key: "datatype",
      width: 50
    },
    {
      title: "UI",
      dataIndex: "ui",
      key: "ui",
      width: 50
    },
    {
      title: "Lookup",
      dataIndex: "lookup",
      key: "lookup",
      width: 50
    },
    {
      title: "Editerbar",
      dataIndex: "editable",
      key: "editable",
      width: 50,
      render: (editable) => <Switch checked={editable} />
    },
    {
      title: "Erforderlich",
      dataIndex: "required",
      key: "required",
      width: 50,
      render: (editable) => <Switch checked={editable} />
    }
  ];

  const dataTableColumns = [
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
      column_label: "",
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
  ];

  return (
    <React.Fragment>
      <PageHeader
        onBack={() => (window.location.href = "/apps")}
        title={title}
        subTitle=""
        extra={[
          <Button
            key="1"
            danger
            htmlType="button"
            icon={<DeleteOutlined />}
            onClick={onReset}
          >
            Löschen
          </Button>,
          //<Button key="2" htmlType="button" onClick={onReset}>Abbrechen</Button>,
          <Button
            key="3"
            type="primary"
            htmlType="submit"
            icon={<SaveOutlined />}
          >
            Speichern
          </Button>
        ]}
      />
      <br />
      <br />
      <Tabs defaultActiveKey="1" items={items} tabPosition="left" />

      <Modal
        title="Applikationsseite"
        open={isModalOpen}
        onOk={handleOk}
        onCancel={handleCancel}
        centered
        width={1000}
      >
        <Form {...layoutpage} layout="horizontal">
          <Form.Item name="page_id" label="ID">
            <Text>1</Text>
          </Form.Item>
          <Form.Item
            name="page_name"
            label="Seitenname"
            rules={[{ required: true }]}
          >
            <Input placeholder="Seitenname" />
          </Form.Item>
          <Form.Item
            name="page_alias"
            label="Alias"
            rules={[{ required: true }]}
          >
            <Input placeholder="eindeutige Alias" />
          </Form.Item>

          <Form.Item name="page_allowed_actions" label="Aktionen">
            <Select
              placeholder="erlaubte Aktionen"
              allowClear
              showSearch
              mode="multiple"
              options={[
                {
                  value: "create",
                  label: "Create"
                },
                {
                  value: "update",
                  label: "Update"
                },
                {
                  value: "delete",
                  label: "Delete"
                }
              ]}
            />
          </Form.Item>

          <Form.Item
            name="page_table"
            label="Tabelle"
            rules={[{ required: true }]}
          >
            <Space>
              <Select
                placeholder="Tabelle auswählen ..."
                allowClear
                showSearch
                style={{ width: 555 }}
                options={[
                  {
                    value: "mm_dwh_stage.dds.PAR_MAILING_LIST",
                    label: "mm_dwh_stage.dds.PAR_MAILING_LIST"
                  },
                  {
                    value: "mm_dwh_stage.dds.PAR_FAIREVENT_GENERAL",
                    label: "mm_dwh_stage.dds.PAR_FAIREVENT_GENERAL"
                  },
                  {
                    value: "...",
                    label: "..."
                  }
                ]}
              />
              <Button icon={<ReloadOutlined />} href="#">
                Spalten aktualisieren
              </Button>
            </Space>
          </Form.Item>
        </Form>

        <Divider
          orientation="left"
          orientationMargin={0}
          plain={true}
          style={{ fontWeight: "bold" }}
        >
          Spalten
        </Divider>
        <Table
          size="small"
          columns={columnsTableColumns}
          dataSource={dataTableColumns}
          //pagination={{ pageSize: 50 }}
          pagination={false}
          //scroll={{ y: 500 }}
        />
      </Modal>
    </React.Fragment>
  );
};

export default AppEdit;
