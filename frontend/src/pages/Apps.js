import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Button, Typography, Card, Col, Row, message } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import {
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  PlusOutlined
} from "@ant-design/icons";
import LoadingMessage from "../components/LoadingMessage";
const { Meta } = Card;
const { Title, Link } = Typography;

const Apps = (props) => {

  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [apps, setApps] = useState([]); // metadata of all apps

  console.log("apps / token: " + props.token);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    // get app metadata
    await Axios.get("/api/repo/application", {headers: {Authorization: props.token}}).then(
      (res) => {
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setApps(resData);
        setLoading(false);
      }
    ).catch(
      function (error) {
        setError(true);
        setLoading(false);
        message.error('Es gab einen Fehler beim Laden der Applikationen.');
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
        
        <LoadingMessage /> :
        (error ? 
          <h1>Es konnten keine Applikationen gefunden werden.</h1> :
          <Row gutter={16}>
            
            {apps && apps.map((app) => {
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

// app.alias}>