import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "./pages/AppLayout";
import Home from "./pages/Home";
import Apps from "./pages/apps/list";
import AppEdit from "./pages/apps/edit";
import AppRun from "./pages/AppRun";
import AppsAdhocView from "./pages/AppsAdhocView";
import NoPage from "./pages/utils/NoPage";
import Settings from "./pages/Settings";
import UserProfile from "./pages/UserProfile";
import "antd/dist/reset.css";
import "./css/index.css";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Home />} />
          <Route path="settings" element={<Settings />} />
          <Route path="profile" element={<UserProfile />} />
          <Route path="adhoc/:id" element={<AppsAdhocView />} />
          <Route path="apps" element={<Apps />} />
          <Route path="apps/edit" element={<AppEdit />} />
          <Route path="apps/edit/:id" element={<AppEdit />} />
          <Route path="apps/:id" element={<AppRun />} />
          <Route path="*" element={<NoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

const root = createRoot(document.getElementById("root"));
root.render(<App />);

//<Route path="blogs" element={<Blogs />} />
//<Route path="contact" element={<Contact />} />
//<Route path="*" element={<NoPage />} />
//          <Route path="apps/adhoc" element={<AppsAdhoc />} />
