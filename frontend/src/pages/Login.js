import React from "react";
import { Form, Input, Button, Checkbox,Image, Space  } from 'antd';
import Icon from '@ant-design/icons';

const LoginPage = () => {

  const handleSubmit = (e) => {
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        console.log('Received values of form: ', values);
      }
    });
  };

  return (
      <div className="login">
        <div>
          <Image id="logo" src="/logo" preview={false} />
          </div>
          <div>
          <br/>
          <h1>Bitte anmelden ...</h1>
          <br />
          </div>
        <Form layout="horizontal">
          <Form.Item
            rules={[{ required: true, message: 'Bitte Username eingeben.' }]}
          >
            <Input
              prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />}
              placeholder="Username"
            />
          </Form.Item>
          <Form.Item
            rules={[{ required: true, message: 'Bitte Passwort eingeben.' }]}
          >
            <Input
              prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
              type="password"
              placeholder="Passwort"
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="login-form-button"
            >
              Login
            </Button>
          </Form.Item>
        </Form>
      </div>
  );
};

export default LoginPage;