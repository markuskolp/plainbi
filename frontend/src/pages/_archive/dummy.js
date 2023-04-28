import React from "react";
import {
  DatePicker,
  InputNumber,
  Switch,
  Select,
  Button,
  Form,
  Input,
  Radio
} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { DeleteOutlined, SaveOutlined } from "@ant-design/icons";
const { TextArea } = Input;

const Dummy = () => {
  const layout = {
    labelCol: { span: 4 },
    wrapperCol: { span: 14 }
  };

  const onReset = () => {
    //
  };
  return (
    <React.Fragment>
      <PageHeader
        onBack={() => (window.location.href = "/apps")}
        title="Neue Pflegeapplikation erstellen"
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
          <Button key="2" htmlType="button" onClick={onReset}>
            Abbrechen
          </Button>,
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
      <Form {...layout} layout="horizontal">
        <Form.Item label="Text">
          <Input placeholder="input placeholder" />
        </Form.Item>
        <Form.Item label="Radio">
          <Radio.Group>
            <Radio value="apple"> Apple </Radio>
            <Radio value="pear"> Pear </Radio>
          </Radio.Group>
        </Form.Item>
        <Form.Item name="lookup" label="Lookup" rules={[{ required: true }]}>
          <Select
            placeholder="Select a option and change input text above"
            allowClear
            showSearch
            options={[
              {
                value: "jack",
                label: "Jack"
              },
              {
                value: "lucy",
                label: "Lucy"
              },
              {
                value: "tom",
                label: "Tom"
              }
            ]}
          />
        </Form.Item>
        <Form.Item label="DatePicker">
          <DatePicker />
        </Form.Item>
        <Form.Item label="InputNumber">
          <InputNumber />
        </Form.Item>
        <Form.Item label="TextArea">
          <TextArea rows={4} />
        </Form.Item>
        <Form.Item label="Switch" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item label="Form Size" name="size">
          <Radio.Group defaultValue="small">
            <Radio.Button value="small">Small</Radio.Button>
            <Radio.Button value="default">Default</Radio.Button>
            <Radio.Button value="large">Large</Radio.Button>
          </Radio.Group>
        </Form.Item>
      </Form>
    </React.Fragment>
  );
};

export default Dummy;
