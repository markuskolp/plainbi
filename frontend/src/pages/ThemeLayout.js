import React from "react";
import { useState } from "react";
import { ConfigProvider, Tooltip, Image, Space } from "antd";
import { Layout, theme, Button } from "antd";
import { Typography } from "antd";
import axios from "axios";
import {
  AppstoreOutlined,
  SettingOutlined,
  UserOutlined
} from "@ant-design/icons";
import "antd/dist/reset.css";
import "../css/index.css";
import { Outlet } from "react-router-dom";
//import logo from "./logo";

const { Title, Link } = Typography;
const { Header, Content, Footer } = Layout;

// config.js
const app_title = window.APP_TITLE;
const header_title = window.HEADER_TITLE;
const footer = window.FOOTER;
const color_primary = window.THEME_COLOR_PRIMARY;
const color_success = window.THEME_COLOR_SUCCESS;
const color_error = window.THEME_COLOR_ERROR;
const color_info = window.THEME_COLOR_INFO;
const font_size = window.THEME_FONT_SIZE;

// set document title if given
document.title = app_title ? app_title : 'plainbi';


const ThemeLayout = (props) => {
  const {
    token: { colorBgContainer }
  } = theme.useToken();

  const { defaultAlgorithm, darkAlgorithm } = theme;

  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleDarkModeSwitch = () => {
    setIsDarkMode((previousValue) => !previousValue);
   };

   
  const logMeOut = () => {
    axios({
      method: "POST",
      url:"/logout",
    })
    .then((response) => {
       props.token()
    }).catch((error) => {
      if (error.response) {
        console.log(error.response)
        console.log(error.response.status)
        console.log(error.response.headers)
        }
    })
  };

  return (
    <React.Fragment>
      <ConfigProvider
        theme={{
          algorithm: isDarkMode ? darkAlgorithm : defaultAlgorithm,
          token: {
            colorPrimary: color_primary ? color_primary : "#333333",
            colorSuccess: color_success ? color_success : "#91c311",
            colorError: color_error ? color_error : "#b31013",
            colorInfo: color_info ? color_info : "#3b80e0",
            fontSize: font_size ? font_size : 13
          }
        }}
      >
        <Layout className="layout">
          <Header>
            <Space size={"middle"}>
              <Link href="/">
                <Image id="header_logo" src="/logo" preview={false} />
              </Link>
              <Link href="/">
                <Title>{header_title ? header_title : ' '}</Title>
              </Link>
            </Space>
            <Space size={"middle"} className="right">
              <Link href="/settings">
                <Tooltip title="Einstellungen">
                  <SettingOutlined />
                </Tooltip>
              </Link>
              <Link href="/apps">
                <Tooltip title="Applikationen">
                  <AppstoreOutlined />
                </Tooltip>
              </Link>
              <Link href="/profile">
                <Tooltip title="Benutzerprofil">
                  <UserOutlined />
                </Tooltip>
              </Link>
              <Button onClick={logMeOut}> 
                Abmelden
              </Button>
            </Space>
          </Header>
          <Content style={{ padding: "0 50px" }}>
            <div
              className="site-layout-content"
              style={{ background: colorBgContainer }}
            >
              <Outlet />
            </div>
          </Content>
          <Footer style={{ textAlign: "center" }}>
            {footer ? footer : 'created by the plainbi team with love'}
          </Footer>
        </Layout>
      </ConfigProvider>
    </React.Fragment>
  );
};

export default ThemeLayout;

/*

              <Button onClick={handleDarkModeSwitch}>
                Change Theme to {isDarkMode ? "Light" : "Dark"}
              </Button>
*/