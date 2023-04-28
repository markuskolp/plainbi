import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ThemeLayout from "./pages/ThemeLayout";
import Home from "./pages/Home";
import Apps from "./pages/Apps";
import AppRuntime from "./pages/AppRuntime";
import AdhocRuntime from "./pages/AdhocRuntime";
import NoPage from "./pages/NoPage";
import Settings from "./pages/Settings";
import UserProfile from "./pages/UserProfile";
import "antd/dist/reset.css";
import "./css/index.css";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ThemeLayout />}>
          <Route index element={<Home />} />
          <Route path="settings" element={<Settings />} />
          <Route path="profile" element={<UserProfile />} />
          <Route path="adhoc/:id" element={<AdhocRuntime />} />
          <Route path="apps" element={<Apps />} />
          <Route path="apps/:id" element={<AppRuntime />} />
          <Route path="*" element={<NoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

const root = createRoot(document.getElementById("root"));
root.render(<App />);

//<Route path="apps/edit" element={<AppEdit />} />
//<Route path="apps/edit/:id" element={<AppEdit />} />
//import AppEdit from "./pages/apps/edit";
