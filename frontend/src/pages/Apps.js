import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
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

const Apps = () => {

  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [apps, setApps] = useState([]); // metadata of all apps

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    // get app metadata
    await Axios.get("/api/repo/application.json").then(
      (res) => {
        setApps(res.data);
        setLoading(false);
      }
    ).catch(
      function (error) {
        setError(true);
        setLoading(false);
      }
    );
  };

  return (
    
    <React.Fragment>
      <PageHeader
        onBack={() => window.history.back()}
        title="Applikationen"
        subTitle=""
        /*extra={[
          <Button
            href="/apps/edit"
            key="1"
            type="primary"
            icon={<PlusOutlined />}
          >
            Neu
          </Button>
        ]}*/
      />
      <br />
      {loading ? 
        <h1>Lädt...</h1> : 
        (error ? 
          <h1>Es konnten keine Applikationen gefunden werden.</h1> :
          <Row gutter={16}>
            
            {apps.map((app) => {
              return (
                <Col span={6}>
                  <Link href={"/apps/"+app.alias}>
                    <Card
                      style={{ maxWidth: 300, marginTop: 16 }}
                      bodyStyle={{ display: "none" }}
                      type="inner"
                      bordered={true}
                      hoverable={true}
                      title={app.name}
                    />
                  </Link>
                </Col>
              )
              })
            }
          </Row>
        )
                }
    </React.Fragment>
  );
};
//<Meta title="Adhoc Konfiguration" />
export default Apps;


/*

            <Col span={6}>
              <Link href="/apps/dwh_admin">
                <Card
                  style={{ maxWidth: 300, marginTop: 16 }}
                  bodyStyle={{ display: "none" }}
                  type="inner"
                  bordered={true}
                  hoverable={true}
                  title="DWH Administration"
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
                    />
                  </Link>
                </Col>
                <Col span={6}>
                  <Link href="/apps/ext_res">
                    <Card
                      style={{ maxWidth: 300, marginTop: 16 }}
                      bodyStyle={{ display: "none" }}
                      type="inner"
                      bordered={true}
                      hoverable={true}
                      title="Externe Ressourcen"
                    />
                  </Link>
                </Col>
*/