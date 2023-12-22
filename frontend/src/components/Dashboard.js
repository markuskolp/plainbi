import React, { useState } from "react";
import RGL, { WidthProvider } from "react-grid-layout";
//import { useMutation } from "@apollo/react-hooks";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
//import { GET_DASHBOARD_ITEMS } from "../graphql/queries";
//import { UPDATE_DASHBOARD_ITEM } from "../graphql/mutations";
import dragBackground from "./drag-background.svg";
import styled from 'styled-components';
const ReactGridLayout = WidthProvider(RGL);

const defaultDashboardItems = [{"vizState":"{\"query\":{\"measures\":[\"Orders.count\"],\"timeDimensions\":[{\"dimension\":\"Orders.createdAt\",\"granularity\":\"month\"}],\"dimensions\":[\"Orders.status\"]},\"chartType\":\"bar\",\"sessionGranularity\":\"month\"}","name":"Orders by Status Over Time","id":"10","layout":"{\"x\":9,\"y\":8,\"w\":15,\"h\":8}"},{"vizState":"{\"query\":{\"measures\":[\"LineItems.cumulativeTotalRevenue\"],\"timeDimensions\":[{\"dimension\":\"LineItems.createdAt\",\"granularity\":\"month\",\"dateRange\":\"Last year\"}]},\"chartType\":\"area\",\"sessionGranularity\":\"month\"}","name":"Revenue Growth Last Year","id":"14","layout":"{\"x\":0,\"y\":0,\"w\":13,\"h\":8}"},{"vizState":"{\"query\":{\"measures\":[\"Orders.count\"],\"timeDimensions\":[{\"dimension\":\"Orders.completedAt\",\"granularity\":\"day\",\"dateRange\":\"Last 30 days\"}],\"filters\":[{\"dimension\":\"Orders.status\",\"operator\":\"equals\",\"values\":[\"completed\"]}]},\"chartType\":\"line\"}","name":"Completed Orders Last 30 days","id":"15","layout":"{\"x\":13,\"y\":0,\"w\":11,\"h\":8}"},{"vizState":"{\"query\":{\"measures\":[\"Orders.count\"],\"timeDimensions\":[{\"dimension\":\"Orders.completedAt\"}],\"dimensions\":[\"ProductCategories.name\"]},\"chartType\":\"bar\"}","name":"Orders by Product Category Name","id":"16","layout":"{\"x\":0,\"y\":16,\"w\":24,\"h\":8}"},{"vizState":"{\"query\":{\"dimensions\":[\"Orders.amountTier\"],\"timeDimensions\":[{\"dimension\":\"Orders.completedAt\"}],\"measures\":[\"Orders.count\"],\"filters\":[{\"dimension\":\"Orders.amountTier\",\"operator\":\"notEquals\",\"values\":[\"$0 - $100\"]}]},\"chartType\":\"pie\"}","name":"Orders by Price Tiers","id":"17","layout":"{\"x\":0,\"y\":8,\"w\":9,\"h\":8}"}];

export const getDashboardItems = () =>
  JSON.parse(window.localStorage.getItem("dashboardItems")) ||
  defaultDashboardItems;

export const setDashboardItems = items =>
  window.localStorage.setItem("dashboardItems", JSON.stringify(items));

const DragField = styled(ReactGridLayout)`
  margin: 16px 28px 50px 28px;
  ${props => props.isDragging ? `
    background: url(${dragBackground});
    background-repeat: repeat-y;
    background-position: 0px -4px;
    background-size: 100% 52px;
  `: ''};
`

const Dashboard = ({ children, dashboardItems }) => {
  const [isDragging, setIsDragging] = useState(false);
  /*const [updateDashboardItem] = useMutation(UPDATE_DASHBOARD_ITEM, {
    refetchQueries: [
      {
        query: GET_DASHBOARD_ITEMS
      }
    ]
  });*/

  const onLayoutChange = newLayout => {
    newLayout.forEach(l => {
      const item = dashboardItems.find(i => i.id.toString() === l.i);
      const toUpdate = JSON.stringify({
        x: l.x,
        y: l.y,
        w: l.w,
        h: l.h
      });

      if (item && toUpdate !== item.layout) {
        /*updateDashboardItem({
          variables: {
            id: item.id,
            input: {
              layout: toUpdate
            }
          }
        });*/
        //console.log("must update item: " + item + " to layout: " + toUpdate);
      }
    });
  };

  return (
    <DragField
      margin={[12, 12]}
      containerPadding={[0, 0]}
      onDragStart={() => setIsDragging(true)}
      onDragStop={() => setIsDragging(false)}
      onResizeStart={() => setIsDragging(true)}
      onResizeStop={() => setIsDragging(false)}
      cols={24}
      rowHeight={40}
      onLayoutChange={onLayoutChange}
      isDragging={isDragging}
     >
      {children}
    </DragField>
  );
};

export default Dashboard;