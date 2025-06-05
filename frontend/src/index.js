import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ThemeLayout from "./pages/ThemeLayout";
import Home from "./pages/Home";
import Apps from "./pages/Apps";
import AppRuntime from "./pages/AppRuntime";
import AdhocRuntime from "./pages/AdhocRuntime";
import NoPage from "./pages/NoPage";
import Settings from "./pages/Settings";
import DashboardPage from "./pages/DashboardPage";
import UserProfile from "./pages/UserProfile";
import useToken from "./components/useToken";
import "antd/dist/reset.css";
import "./css/index.css";
import Login from "./pages/Login";
import LoginSSO from "./pages/LoginSSO";
import { ConfigProvider } from 'antd';
import deDE from 'antd/locale/de_DE';
import ERD from "./pages/ERD";

const App = () => {
  const { token, removeToken, setToken } = useToken();
  const userRole = localStorage.getItem('role');
  const pathname = window.location.pathname;
  console.log("pathname",pathname);

  return (
    <ConfigProvider locale={deDE}>
      <BrowserRouter>
      { console.log("brouwserrouter loc="+pathname) }
      { 
        (pathname.startsWith("/getSSOToken")) ? ( <LoginSSO setToken={setToken} /> ) 
      : 
      (

      !token && token!=="" &&token!== undefined ?  
        (
          
          <Login setToken={setToken} />
        ) :
        (
          <Routes>
            <Route path="/" element={<ThemeLayout removeToken={removeToken} />} >
              <Route index element={<Home token={token} setToken={setToken} removeToken={removeToken}/>} />
              {userRole == 'ADMIN' && <Route path="settings" element={<Settings token={token} setToken={setToken} removeToken={removeToken} />} /> }
              <Route path="myprofile" element={<UserProfile token={token} setToken={setToken} removeToken={removeToken}/>} />
              <Route path="adhoc/:id" element={<AdhocRuntime token={token} setToken={setToken} removeToken={removeToken}/>} />
              <Route path="apps" element={<Apps token={token} setToken={setToken} removeToken={removeToken}/>} />
              <Route path="apps/:id/:page_id?" element={<AppRuntime token={token} setToken={setToken} removeToken={removeToken} />} />
              <Route path="apps/:id/:page_id?/:pk?" element={<AppRuntime token={token} setToken={setToken} removeToken={removeToken} />} />
              <Route path="dashboard/:id" element={<DashboardPage token={token} setToken={setToken} />} />
              <Route path="erd" element={<ERD token={token} setToken={setToken} />} />
              <Route path="*" element={<NoPage />} />
            </Route>
          </Routes>
        )
      )
      }
      </BrowserRouter>
    </ConfigProvider>
  );
};

const root = createRoot(document.getElementById("root"));
root.render(<App />);

//<Route path="apps/edit" element={<AppEdit />} />
//<Route path="apps/edit/:id" element={<AppEdit />} />
//import AppEdit from "./pages/apps/edit";

// <LoginPage setToken={setToken} /> 
/*
<Route path="/" element={<ThemeLayoutNoHeader />}>
          <Route path="login" element={<LoginPage setToken={setToken} />} />
        </Route>
        */