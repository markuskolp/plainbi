import React, { useRef, useEffect, useState } from "react";
import { Form, Input, Button, Checkbox,Image, Space, message, Typography  } from 'antd';
import Icon from '@ant-design/icons';
import Axios from "axios";
import EnvironmentBanner from "../components/EnvironmentBanner";
const { Title } = Typography;

const Login = (props) => {

  const [loading, setLoading] = useState(false);

  const [loginForm, setloginForm] = useState({
    username: "",
    password: ""
  })

  const [header_title, setHeader_title] = useState(); 
  const [environment_banner_text, setEnvironment_banner_text] = useState(); 
  const [environment_banner_color, setEnvironment_banner_color] = useState(); 
    
  useEffect(() => {
    initializeGlobalSettings();
  }, []);

  function getSetting(settings, name) {
    let found = settings.find(({ setting_name }) => setting_name === name);
    //console.log("getSetting() - name: " + name + " - found:");
    //console.log(found);
    return found ? found.setting_value : null;
  }

  const initializeGlobalSettings = async () => {
    await Axios.get("/api/settings", {headers: {Authorization: props.token}}).then(
      (res) => {
        //console.log(JSON.stringify(res));
        const resData = res.data.data;
        // set document title if given
        //document.title = getSetting('app_title') ? getSetting('app_title') : 'plainbi';
        document.title = getSetting(resData, 'app_title') ? getSetting(resData, 'app_title') : 'plainbi';
        setHeader_title(getSetting(resData, 'header_title'));
        setEnvironment_banner_text(getSetting(resData, 'environment_banner_text'));
        setEnvironment_banner_color(getSetting(resData, 'environment_banner_color'));
        //setApp_title(getSetting(resData, 'app_title') ? getSetting(resData, 'app_title') : 'plainbi');
        //console.log("app_title: " + app_title);
      }
    ).catch(
      function (error) {
        console.error(error);
        //message.error('Es gab einen Fehler beim Laden von übergreifenden Einstellungen.');
      }
    );
  };

  function logMeIn(event) {
    setLoading(true);
    Axios({
      method: "POST",
      url:"/api/login",
      data:{
        username: loginForm.username,
        password: loginForm.password
       }
    })
    .then((response) => {
      props.setToken(response.data.access_token)
      //props.setRole(response.data.role ? response.data.role.toUpperCase() : 'ADMIN')
      localStorage.setItem('role', response.data.role ? response.data.role.toUpperCase() : 'USER')
      //localStorage.setItem('role', 'ADMIN');
      //props.setRole('ADMIN');
  
    }).catch((error) => {
      if (error.response) {
        console.log(error.response)
        console.log(error.response.status)
        console.log(error.response.headers)
        }
        setLoading(false);
        message.error('Fehler: ' + error.response.data.message);
        setloginForm(({
          username: "",
          password: ""}))
    
      })

    event.preventDefault()
  }

  function handleChange(event) { 
    const {value, name} = event.target
    setloginForm(prevNote => ({
        ...prevNote, [name]: value})
    )}


/*  const userInput = useRef(null);

  useEffect(() => {
    if (userInput.current) {
      // or, if Input component in your ref, then use input property like:
      // userInput.current.input.focus();
      userInput.current.focus();
    }
  }, [userInput]);

  const handleSubmit = (e) => {
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        console.log('Received values of form: ', values);
      }
    });
  };
*/

  return (
    <React.Fragment>
      { environment_banner_text ? <EnvironmentBanner text={environment_banner_text} backgroundColor={environment_banner_color} /> : ""}
      <div className="login">
        <div>
          <Space size={"middle"}>
            <Image id="header_logo" src="/api/static/logo" preview={false} />
            <Title level={5}>{header_title ? header_title : ' '}</Title>
          </Space>
          </div>
          <div>
          <br/>
          </div>
        <Form layout="horizontal">
          <Form.Item
            rules={[{ required: true, message: 'Bitte Username eingeben.' }]}
          >
            <Input
              prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />}
              placeholder="Username"
              name="username"
              value={loginForm.username}
              onChange={handleChange} 
            />
          </Form.Item>
          <Form.Item
            rules={[{ required: true, message: 'Bitte Passwort eingeben.' }]}
          >
            <Input
              prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
              type="password"
              name="password"
              value={loginForm.password}
              placeholder="Passwort"
              onChange={handleChange} 
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="login-form-button"
              onClick={logMeIn}
              loading={loading}
            >
              Anmelden
            </Button>
          </Form.Item>
        </Form>
      </div>
      </React.Fragment>
  );
};

export default Login;


/*
<input onChange={handleChange} 
type="text"
text={loginForm.username} 
name="username" 
placeholder="username" 
value={loginForm.username} />
<input onChange={handleChange} 
type="password"
text={loginForm.password} 
name="password" 
placeholder="Password" 
value={loginForm.password} />

<button onClick={logMeIn}>Login</button>*/