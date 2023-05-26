import React from "react";
import { Row, Col, Card } from "antd";
import Resources from "../components/Resources";
import TileVA from "../components/TileVA";

const Home = (props) => {

  return (
        <React.Fragment>
          <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
            <Col span={12}>
              <Resources token={props.token}/>
            </Col>
            <Col span={12}> 
              <TileVA token={props.token}/>
            </Col>
          </Row>
      </React.Fragment>
  );
};

export default Home;

