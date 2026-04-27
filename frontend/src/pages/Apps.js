import React, { useState, useEffect } from "react";
import { Button, Typography, Card, Flex, Avatar, Tooltip, Alert } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { AppstoreOutlined } from "@ant-design/icons";
import LoadingMessage from "../components/LoadingMessage";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData, sortByName } from "../utils/dataUtils";

const { Title, Link } = Typography;

const Apps = () => {
  const { loading, setLoading, error, errorMessage, errorDetail, setApiError } = useApiState(true);
  const [apps, setApps] = useState([]);

  useEffect(() => {
    apiClient.get("/api/repo/application")
      .then((res) => {
        setApps(sortByName(extractResponseData(res)));
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Applikationen', err));
  }, []);

  return (
    <React.Fragment>
      <PageHeader
        onBack={() => window.history.back()}
        title="Applikationen"
        subTitle=""
      />
      <br />
      {loading ? (
        <LoadingMessage />
      ) : error ? (
        <Alert message={errorMessage} description={errorDetail} type="error" showIcon />
      ) : (
        <Flex gap="middle" wrap>
          {apps.map((app) => (
            <Tooltip key={app.alias} title={app.name}>
              <Link href={"/apps/" + app.alias}>
                <Card style={{ maxWidth: 300, minWidth: 300 }} bordered hoverable>
                  <Card.Meta
                    avatar={
                      <Avatar
                        icon={<AppstoreOutlined />}
                        style={{ backgroundColor: '#fff', color: '#000', marginTop: '-5px' }}
                      />
                    }
                    title={app.name}
                  />
                </Card>
              </Link>
            </Tooltip>
          ))}
        </Flex>
      )}
    </React.Fragment>
  );
};

export default Apps;
