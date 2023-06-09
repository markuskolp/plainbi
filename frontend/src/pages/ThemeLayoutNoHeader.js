import React from "react";
import { ConfigProvider, Tooltip, Image, Space } from "antd";
import { Layout, theme } from "antd";
import { Typography } from "antd";
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


const ThemeLayout = () => {
  const {
    token: { colorBgContainer }
  } = theme.useToken();

  return (
    <React.Fragment>
      <ConfigProvider
        theme={{
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
