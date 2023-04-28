import React from "react";
import { Button, Typography, Card, Col, Row } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import {
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  PlusOutlined
} from "@ant-design/icons";

const { Meta } = Card;
const { Title, Link } = Typography;

const onClick = () => console.log("Works!");

const Apps = () => {
  return (
    <React.Fragment>
      <PageHeader
        onBack={() => window.history.back()}
        title="Applikationen"
        subTitle=""
        extra={[
          <Button
            href="/apps/edit"
            key="1"
            type="primary"
            icon={<PlusOutlined />}
          >
            Neu
          </Button>
        ]}
      />
      <br />
      <Row gutter={16}>
        <Col span={6}>
          <Link href="/apps/dwh_admin">
            <Card
              style={{ maxWidth: 300, marginTop: 16 }}
              bodyStyle={{ display: "none" }}
              type="inner"
              bordered={true}
              hoverable={true}
              title="DWH Administration"
              /*extra={
                <a href="/apps/edit/1">
                  <EditOutlined />
                </a>
              }*/
            />
          </Link>
        </Col>
        <Col span={6}>
          <Link href="/apps/adhoc">
            <Card
              style={{ maxWidth: 300, marginTop: 16 }}
              bodyStyle={{ display: "none" }}
              type="inner"
              bordered={true}
              hoverable={true}
              title="Adhoc Konfiguration"
              /*extra={
                <a href="/apps/edit/2">
                  <EditOutlined />
                </a>
              }*/
            />
          </Link>
        </Col>
      </Row>
    </React.Fragment>
  );
};
//<Meta title="Adhoc Konfiguration" />
export default Apps;
