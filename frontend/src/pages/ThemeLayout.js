import React from "react";
import { useState, useEffect } from "react";
import { Avatar, ConfigProvider, Tooltip, Image, Space, Dropdown } from "antd";
import { useNavigate } from "react-router-dom";
import { Layout, theme, Button } from "antd";
import { message, Typography } from "antd";
import LoadingMessage from "../components/LoadingMessage";
import Axios from "axios";
import {
  AppstoreOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined 
} from "@ant-design/icons";
import "antd/dist/reset.css";
import "../css/index.css";
import { Outlet } from "react-router-dom";
import EnvironmentBanner from "../components/EnvironmentBanner";
//import logo from "./logo";

const { Title, Link, Text } = Typography;
const { Header, Content, Footer } = Layout;

const ThemeLayout = (props) => {
  const {
    token: { colorBgContainer }
  } = theme.useToken();
  const navigate = useNavigate();
  const { defaultAlgorithm, darkAlgorithm } = theme;
  const [isDarkMode, setIsDarkMode] = useState(false);
  const handleDarkModeSwitch = () => {
    setIsDarkMode((previousValue) => !previousValue);
   };
  const userRole = localStorage.getItem('role');
  
  //const [app_title, setApp_title] = useState(); // global settings
  const [header_title, setHeader_title] = useState(); 
  const [footer, setFooter] = useState(); 
  const [color_primary, setColor_primary] = useState(); 
  const [color_success, setColor_success] = useState(); 
  const [color_error, setColor_error] = useState(); 
  const [color_info, setColor_info] = useState(); 
  const [font_size, setFont_size] = useState(); 
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
        //console.log("/settings response: " + JSON.stringify(resData));
        //console.log("/settings app_title: " + getSetting(resData, 'app_title') );
        // set document title if given
        //document.title = getSetting('app_title') ? getSetting('app_title') : 'plainbi';
        document.title = getSetting(resData, 'app_title') ? getSetting(resData, 'app_title') : 'plainbi';
        setHeader_title(getSetting(resData, 'header_title'));
        setFooter(getSetting(resData, 'footer'));
        setColor_primary(getSetting(resData, 'color_primary'));
        setColor_success(getSetting(resData, 'color_success'));
        setColor_error(getSetting(resData, 'color_error'));
        setColor_info(getSetting(resData, 'color_info'));
        setFont_size(getSetting(resData, 'font_size'));
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
   
  const logMeOut = () => {
    Axios({
      method: "POST",
      url:"/api/logout",
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

  const logout = () => {
    localStorage.removeItem("role");
    props.removeToken();
    //props.setRole(null);
  }

  const items = [
    /*{
      label: <React.Fragment><b style={{color:'#000'}}>kolp</b></React.Fragment>,
      key: '0',
      //icon: <UserOutlined />,
      disabled: true,
    },
    */
    {
      label: 'Benutzerprofil',
      key: '1',
      //icon: <UserOutlined />,
    },
    {
      label: 'Abmelden',
      key: '2',
      //icon: <LogoutOutlined />,
    },
  ];

  const handleMenuClick = (e) => {
    console.log('click', e);
    if (e.key === '1') {
      navigate("/myprofile");
    }
    if (e.key === '2') {
      logout();
    }
  };
  
  const menuProps = {
    items,
    onClick: handleMenuClick,
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
              fontSize: isNaN(font_size) ? 13 : Number(font_size)
            }
          }}
        >
          <Layout className="layout">
          { environment_banner_text ? <EnvironmentBanner text={environment_banner_text} backgroundColor={environment_banner_color} /> : ""}
            <Header>
              <Space size={"middle"}>
                <Link href="/">
                  <Image id="header_logo" src="/api/static/logo" preview={false} />
                </Link>
                <Link href="/">
                  <Title>{header_title ? header_title : ' '}</Title>
                </Link>
              </Space>
              <Space size={"middle"} className="right">
                {userRole == 'ADMIN' && 
                  <Link href="/settings">
                    <Tooltip title="Einstellungen">
                      <SettingOutlined />
                    </Tooltip>
                  </Link>
                }
                <Link href="/apps">
                  <Tooltip title="Applikationen">
                    <AppstoreOutlined />
                  </Tooltip>
                </Link>
                <Dropdown menu={menuProps} >
                  <UserOutlined /> 
                </Dropdown>
              </Space>
            </Header>
            <Content style={{ padding: "0px 50px" }}>
              <div
                className="site-layout-content"
                //style={{ background: colorBgContainer }}
                //style={{ background: environment_banner_color }}
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

/*
            <div
              className="site-layout-content"
              style={{ background: colorBgContainer }}
            >
            </div>
*/
/*

              <Link href="/profile">
                <Tooltip title="Benutzerprofil">
                  <UserOutlined />
                </Tooltip>
              </Link>
              <Link href="" onClick={logout}>
                <Tooltip  title="Abmelden">
                  <LogoutOutlined />
                </Tooltip>
              </Link>
              */