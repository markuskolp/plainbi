import React from "react";
import { Row, Col } from "antd";
import Resources from "../components/Resources";

const Home = () => {

  return (
        <React.Fragment>
          <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
            <Col span={12}>
              <Resources />
            </Col>
            <Col span={12}> 
            </Col>
          </Row>
      </React.Fragment>
  );
};

export default Home;

