import React from "react";
import { Button, Empty } from "antd";

const Map = () => {
  return (
    <React.Fragment>
      <Empty description={<span>Dieser Bereich wird noch entwickelt.</span>}>
        <Button type="primary" href="/">
          zurück zur Startseite
        </Button>
      </Empty>
    </React.Fragment>
  );
};

export default Map;
