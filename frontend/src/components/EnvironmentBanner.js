import React from "react";
import { Layout, Typography } from "antd";
const { Text } = Typography;
const { Header , Content} = Layout;

const EnvironmentBanner = ({text, backgroundColor}) => {
  return (
    <React.Fragment>
          <div style={{backgroundColor:'rgb(0, 128, 128)', height:'30px', lineHeight:'30px', paddingInline:'50px', textAlign:'center' }}>
            <Text style={{color:'white'}}>{text}</Text>
          </div>
    </React.Fragment>
  );
};

export default EnvironmentBanner;

//style={{backgroundColor: {backgroundColor} }}