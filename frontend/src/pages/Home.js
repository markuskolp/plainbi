import React from "react";
import { Row, Col, Card } from "antd";
import Resources from "../components/Resources";
import TileVA from "../components/TileVA";

const Home = (props) => {

  const host = window.location.host;
  //const isHostMMG = (host.match(/mmgmuc.de/gi) || host.match(/localhost/gi)) ? true : false;
  const isHostMMG = host.match(/mmgmuc.de/gi) ? true : false; // if host is mmgmuc.de then show TileVA
  
  return (
        <React.Fragment>
          <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
            {isHostMMG ? (
                <React.Fragment>
                  <Col span={12}>
                    <Resources token={props.token} removeToken={props.removeToken}/>
                  </Col>          
                  <Col span={12}> 
                    <TileVA token={props.token}/>
                  </Col>
                </React.Fragment>
              ) : (
                <React.Fragment>
                  <Col span={24}>
                    <Resources token={props.token} removeToken={props.removeToken}/>
                  </Col>          
                </React.Fragment>
              )
            }
          </Row>
      </React.Fragment>
  );
};

export default Home;

