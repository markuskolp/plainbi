import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { message, Typography, Tag, Space } from "antd";
import LoadingMessage from "../components/LoadingMessage";
import UnderConstruction from "../components/UnderConstruction";
const { Text, Link, Title  } = Typography;

const UserProfile = (props) => {

  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]); // profile data
  const [errorMessage, setErrorMessage] = useState('');
  const [errorDetail, setErrorDetail] = useState('');

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    await Axios.get("/api/profile", {headers: {Authorization: props.token}}).then(
      (res) => {
        //console.log(JSON.stringify(res));
        const resData = res.data;
        console.log("/profile response: " + JSON.stringify(resData));
        setData(resData);
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
          setErrorMessage('Es gab einen Fehler beim Laden der Profildaten.');
          setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
         }
        console.log(error);
        console.log(error.response.data.message);
      }
    );
  };


  return (
    <React.Fragment>
      {loading ? (
          <LoadingMessage />
        ) : 
        (
          error ? 
          (
            <Alert
              message={errorMessage}
              description={errorDetail}
              type="error"
              showIcon
            />
          ) : ( 
            <React.Fragment>
              <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
                <Title level={3}>{data.fullname ? data.fullname + " (" + data.username + ")" : data.username}</Title> 
                <Link href={"mailto:"+data.email} >{data.email}</Link> 
                <Title level={5}>Rolle:</Title> 
                <Text>{data.role}</Text> 
                <Title level={5}>Gruppen:</Title> 
                {data.groups && data.groups.map((group) => {console.log(group);return <Text>{group.name}</Text>})}
              </Space>
            </React.Fragment>
          )
        )
      }
    </React.Fragment>
  );

};

export default UserProfile;

/*email
      username
      fullname
      groups
      role
      <Text>{group.name}</Text>
*/