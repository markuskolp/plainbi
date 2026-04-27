import React from "react";
import { useEffect } from "react";
import { Alert, Typography, Tag, Space } from "antd";
import LoadingMessage from "../components/LoadingMessage";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";

const { Text, Link, Title } = Typography;

const UserProfile = () => {

  const { loading, setLoading, error, errorMessage, errorDetail, setApiError, data, setData } = useApiState(true);
  const [profileData, setProfileData] = React.useState({});

  useEffect(() => {
    apiClient.get("/api/profile")
      .then((res) => {
        setProfileData(res.data);
        setLoading(false);
      })
      .catch((err) => setApiError('Es gab einen Fehler beim Laden der Profildaten.', err));
  }, []);

  return (
    <React.Fragment>
      {loading ? (
        <LoadingMessage />
      ) : error ? (
        <Alert message={errorMessage} description={errorDetail} type="error" showIcon />
      ) : (
        <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
          <Title level={3}>{profileData.fullname ? profileData.fullname + " (" + profileData.username + ")" : profileData.username}</Title>
          <Link href={"mailto:" + profileData.email}>{profileData.email}</Link>
          <Title level={5}>Rolle:</Title>
          <Text>{profileData.role}</Text>
          <Title level={5}>Gruppen:</Title>
          {profileData.groups && profileData.groups.map((group) => <Text key={group.id}>{group.name}</Text>)}
        </Space>
      )}
    </React.Fragment>
  );
};

export default UserProfile;
