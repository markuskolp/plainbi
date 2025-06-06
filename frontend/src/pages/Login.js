import React, { useRef, useEffect, useState } from "react";
import { Form, Input, Button, Checkbox,Image, Space, message, Typography  } from 'antd';
import Icon from '@ant-design/icons';
import Axios from "axios";
import EnvironmentBanner from "../components/EnvironmentBanner";
//import { useParams, useLocation, useNavigate } from "react-router-dom";
const { Link, Text, Title } = Typography;

const Login = (props) => {

  const header_title = window.HEADER_TITLE;
  const environment_banner_text = window.ENVIRONMENT_BANNER_TEXT;
  const environment_banner_color = window.ENVIRONMENT_BANNER_COLOR;
  const sso_signin_link = window.SSO_SIGNIN_LINK;
  console.log("SSO Signin Link: " + sso_signin_link);

  //const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);

  const [loginForm, setloginForm] = useState({
    username: "",
    password: ""
  })


  function logMeIn(event) {
    setLoading(true);
    console.log("logmein referrer "+document.referrer);


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

  /*
  const navigateSSO = () => {
    //navigate(sso_signin_link, { replace: true });
    window.location.href(sso_signin_link);
  }
  */
  

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
          {sso_signin_link ? (
              <Form.Item>
                <Link href={sso_signin_link} target='_top'>
                  <Button
                    color="default"
                    htmlType="button"
                    //type="link"
                    className="login-form-button filled"
                    //onClick={navigateSSO}
                    //target={sso_signin_link}
                  >
                    Anmelden mit Single Sign-On (SSO)
                  </Button>
                </Link>
              </Form.Item>
            ) : null
          }
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