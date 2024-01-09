import React from "react";
import { Card, Menu, Typography, Dropdown, Modal} from "antd";
import { MenuOutlined, MoreOutlined } from "@ant-design/icons";
import styled from 'styled-components';
const { Link } = Typography;

const StyledCard = styled(Card)`
  box-shadow: 0px 2px 4px rgba(141, 149, 166, 0.1);
  border-radius: 4px;

  .ant-card-head {
    border: none;
  }
  .ant-card-body {
    padding-top: 12px;
  }
`

const DashboardItemDropdown = ({ itemId }) => {

  const dashboardItemDropdownMenu = (
    <Menu>
      <Menu.Item>
        <Link to={`/explore?itemId=${itemId}`}>Bearbeiten</Link>
      </Menu.Item>
      <Menu.Item
        onClick={() =>
          Modal.confirm({
            title: "Are you sure you want to delete this item?",
            okText: "Yes",
            okType: "danger",
            cancelText: "No",

            onOk() {
              /*removeDashboardItem({
                variables: {
                  id: itemId
                }
              });*/
            }
          })
        }
      >
        Löschen
      </Menu.Item>
    </Menu>
  );

  return (
    <Dropdown
      overlay={dashboardItemDropdownMenu}
      placement="bottomLeft"
      trigger={["click"]}
    >
      <MoreOutlined />
    </Dropdown>
  );

};

const DashboardItem = ({ itemId, children, title }) => (
  <StyledCard
    title={title}
    bordered={false}
    style={{
      height: "100%",
      width: "100%"
    }}
    //className="limitable"
    //bodyStyle={{ padding: "0px", marginTop: 20, width: "100%", height:"300px" }}
    extra={<DashboardItemDropdown itemId={itemId} />}
  >
    {children}
  </StyledCard>
);

export default DashboardItem;
