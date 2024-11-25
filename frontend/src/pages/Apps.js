import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Button, Typography, Card, Col, Row, message, Flex, Avatar, Tooltip, Alert } from "antd";
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

  const [loading, setLoading] = useState(true);
  const [apps, setApps] = useState([]); // metadata of all apps
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [errorDetail, setErrorDetail] = useState('');

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
        setLoading(false);
        setError(true);
        if (error.response.status === 401) {
          props.removeToken()
          message.error('Session ist abgelaufen');
        } else {
          setErrorMessage('Es gab einen Fehler beim Laden der Applikationen');
          setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
         }
        console.log(error);
        console.log(error.response.data.message);
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
          (
            <Alert
              message={errorMessage}
              description={errorDetail}
              type="error"
              showIcon
            />
          )  :
          <Flex gap="middle"  wrap>            
            {apps && apps.map((app) => {
              return (
                  <Tooltip title={app.name}>
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
                  </Tooltip>
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