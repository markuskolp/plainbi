import React from "react";
import { Button, Result } from "antd";

const NoPage = () => {
  return (
    <Result
      status="404"
      title="404 - Seite nicht gefunden"
      subTitle="Sorry, die Seite welche angefragt wurde existiert nicht."
      extra={
        <Button type="primary" href="/">
          zurück zur Startseite
        </Button>
      }
    />
  );
};

export default NoPage;
