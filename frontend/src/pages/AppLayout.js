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

const AppLayout = () => {
  const {
    token: { colorBgContainer }
  } = theme.useToken();

  return (
    <React.Fragment>
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: "rgb(106, 145, 206)",
            colorSuccess: "#91c311",
            colorError: "#b31013",
            colorInfo: "#3b80e0",
            fontSize: 13
          }
        }}
      >
        <Layout className="layout">
          <Header>
            <Space size={"middle"}>
              <Link href="/">
                <Image id="logo" src="/logo" preview={false} />
              </Link>
              <Link href="/">
                <Title>Data & BI</Title>
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
            ©2023 created by Data & BI
          </Footer>
        </Layout>
      </ConfigProvider>
    </React.Fragment>
  );
};

export default AppLayout;
