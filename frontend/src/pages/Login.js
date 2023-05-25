import React, { useRef, useEffect, useState } from "react";
import { Form, Input, Button, Checkbox,Image, Space, message, Typography  } from 'antd';
import Icon from '@ant-design/icons';
import axios from "axios";
const { Title } = Typography;

const Login = (props) => {

  const header_title = window.HEADER_TITLE;

  const [loading, setLoading] = useState(false);

  const [loginForm, setloginForm] = useState({
    username: "",
    password: ""
  })

  function logMeIn(event) {
    setLoading(true);
    axios({
      method: "POST",
      url:"/login",
      data:{
        username: loginForm.username,
        password: loginForm.password
       }
    })
    .then((response) => {
      props.setToken(response.data.access_token)
  
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
      <div className="login">
        <div>
          <Space size={"middle"}>
            <Image id="header_logo" src="/logo" preview={false} />
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
            >
              Anmelden
            </Button>
          </Form.Item>
        </Form>
      </div>
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