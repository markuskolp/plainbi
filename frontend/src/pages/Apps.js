import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Button, Typography, Card, Col, Row, message, Flex, Avatar } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import {
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  PlusOutlined,
  AppstoreOutlined
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
        let resDataSorted = resData.sort((a, b) => {
          let nameA = a.name.toUpperCase(); // ignore upper and lowercase
          let nameB = b.name.toUpperCase(); // ignore upper and lowercase
          if (nameA < nameB) {
            return -1;
          }
          if (nameA > nameB) {
            return 1;
          }
          // names must be equal
          return 0;
        });
        setApps(resDataSorted);
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
          <Flex gap="middle"  wrap>            
            {apps && apps.map((app) => {
              return (
                  <Link key={app.alias} href={"/apps/"+app.alias}> 
                    <Card
                      style={{ maxWidth: 300, minWidth: 300 }}
                      bordered={true}
                      hoverable={true}
                      >
                        <Card.Meta
                              avatar={ 
                                <Avatar 
                                  icon={<AppstoreOutlined />} 
                                  style={{backgroundColor: '#fff', color: '#000', marginTop: '-5px' }}
                                />
                              }
                        title={app.name}
                      />
                    </Card>
                  </Link>
              )
              })
            }
          </Flex>
        )
                }
    </React.Fragment>
  );
};
//<Meta title="Adhoc Konfiguration" />
export default Apps;

// app.alias}>