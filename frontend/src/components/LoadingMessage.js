import React from "react";
import { Spin, Space } from "antd";

const LoadingMessage = () => {
  return (
    <React.Fragment>
      <Space>
        <Spin key="spin" size="small">
          <div className="content" />
        </Spin>
      </Space>
    </React.Fragment>
  );
};

export default LoadingMessage;
