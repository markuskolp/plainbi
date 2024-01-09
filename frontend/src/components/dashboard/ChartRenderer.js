import React from "react";
import { useState, useEffect, useRef, useLayoutEffect  } from "react";
import PropTypes from "prop-types";
import { useCubeQuery } from "@cubejs-client/react";
import { Spin, Row, Col, Statistic } from "antd";
import {
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  LineChart,
  Line,
  LabelList
} from "recharts";
import styled from 'styled-components';
import "./recharts-theme.less";
import moment from "moment";
import Table from "../Table";
import Map from "./Map";

const numberFormatter = item => item.toLocaleString("de-DE"); 
const dateFormatter = item => moment(item).format("MMM YY");
const colors = ["#7DB3FF", "#49457B", "#FF7C78"];
const xAxisFormatter = (item) => {
  return item;
  if (moment(item).isValid()) {
    return dateFormatter(item)
  } else {
    return item;
  }
}

//  interval=0 = draw all labels
// todo: margin bei verticalbar nur, damit die labels bei der y-achse links genug platz haben ?!

const CartesianChart = ({ resultSet, children, ChartComponent, height, layout }) => (
  <ResponsiveContainer width="100%" height={height}>
    {layout === "vertical" ? ( 
      <ChartComponent data={resultSet.chartPivot()} layout="vertical" overflow="visible" margin={{ top: 0, right: 40, left: 40, bottom: 0 }} >
        <Tooltip cursor={{ fill:  'rgba(206, 206, 206, 0.5)' }} />
        <YAxis dataKey="x" type="category"  interval={0}/> 
        <XAxis type="number" />
        <CartesianGrid vertical={true} horizontal={false} />
        { children }
        <Legend />
      </ChartComponent>
    ) : (
      <ChartComponent margin={{ left: -10 }} data={resultSet.chartPivot()}>
        <Tooltip cursor={{ fill:  'rgba(206, 206, 206, 0.5)' }} />
        <XAxis axisLine={false} tickLine={false} tickFormatter={xAxisFormatter} dataKey="x" minTickGap={20} />
        <YAxis axisLine={false} tickLine={false} tickFormatter={numberFormatter} />
        <CartesianGrid vertical={false}/>
        { children }
        <Legend />
      </ChartComponent>
    )
    }
  </ResponsiveContainer>
);

//<Tooltip labelFormatter={dateFormatter} formatter={numberFormatter} />


const formatTableData = (columns, data) => {
  function flatten(columns = []) {
    return columns.reduce((memo, column) => {
      if (column.children) {
        return [...memo, ...flatten(column.children)];
      }

      return [...memo, column];
    }, []);
  }

  const typeByIndex = flatten(columns).reduce((memo, column) => {
    return { ...memo, [column.dataIndex]: column };
  }, {});

  function formatValue(value, { type, format } = {}) {
    if (value == undefined) {
      return value;
    }

    if (type === 'boolean') {
      if (typeof value === 'boolean') {
        return value.toString();
      } else if (typeof value === 'number') {
        return Boolean(value).toString();
      }

      return value;
    }

    if (type === 'number' && format === 'percent') {
      return [parseFloat(value).toFixed(2), '%'].join('');
    }

    return value.toString();
  }

  function format(row) {
    return Object.fromEntries(
      Object.entries(row).map(([dataIndex, value]) => {
        return [dataIndex, formatValue(value, typeByIndex[dataIndex])];
      })
    );
  }

  return data.map(format);
};

const TypeToChartComponent = {
  line: ({ resultSet, height }) => (
    <CartesianChart resultSet={resultSet} height={height} ChartComponent={LineChart}>
      {resultSet.seriesNames().map((series, i) => (
        <Line
          key={series.key}
          stackId="a"
          dataKey={series.key}
          name={series.title}
          stroke={colors[i]}
        />
      ))}
    </CartesianChart>
  ),
  bar: ({ resultSet, height, pivotConfig  }) => (
    //columns={resultSet.tableColumns(pivotConfig).map(c => ({ ...c, dataIndex: c.key, title: c.shortTitle, sorter: true}))}
    //dataSource={formatTableData(resultSet.tableColumns(pivotConfig), resultSet.tablePivot(pivotConfig))}
    //{resultSet.series(pivotConfig).map((series, i) => (
      //{resultSet.seriesNames().map((series, i) => (
        <CartesianChart resultSet={resultSet} height={height} ChartComponent={BarChart}>
      {resultSet.seriesNames().map((series, i) => (
        <Bar
          key={series.key}
          stackId="a"
          dataKey={series.key}
          name={series.title}
          fill={colors[i]}
        />
      ))}
    </CartesianChart>
  ),
  verticalbar: ({ resultSet, height, pivotConfig }) => (
    <CartesianChart resultSet={resultSet} height={height} ChartComponent={BarChart} layout="vertical">
      {resultSet.seriesNames().map((series, i) => (
        <Bar
          key={series.key}
          //stackId="a"
          dataKey={series.key}
          name={series.title}
          fill={colors[i]}
        >
          <LabelList dataKey={series.key} position="right" />
        </Bar>
      ))}
    </CartesianChart>
  ),
  area: ({ resultSet, height }) => (
    <CartesianChart resultSet={resultSet} height={height} ChartComponent={AreaChart}>
      {resultSet.seriesNames().map((series, i) => (
        <Area
          key={series.key}
          stackId="a"
          dataKey={series.key}
          name={series.title}
          stroke={colors[i]}
          fill={colors[i]}
        />
      ))}
    </CartesianChart>
  ),
  pie: ({ resultSet, height }) => (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          isAnimationActive={false}
          data={resultSet.chartPivot()}
          nameKey="x"
          dataKey={resultSet.seriesNames()[0].key}
          fill="#8884d8"
        >
          {resultSet.chartPivot().map((e, index) => (
            <Cell key={index} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Legend />
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  ),
  table: ({ resultSet }) => (
    <Table
      pagination={false}
      columns={resultSet.tableColumns().map(c => ({ ...c, dataIndex: c.key, title: c.shortTitle, sorter: true}))} // take shortTitle (that means without name of data model (cube))
      dataSource={resultSet.tablePivot()}
      size="small"
      //scroll={{ y: 'calc(100vh - 400px)', x: 'max-content' }}
      //scroll={{ x: true }}
      //scroll={{ y: tableHeight }}
      scroll={{ y: 'auto', x: '100%' }}
      //scroll={{ y: 'auto', x: 'auto' }}
      //tableLayout="auto"
    />
  ),
  pivottable: ({ resultSet, pivotConfig }) => (
      <Table
        pagination={false}
        columns={resultSet.tableColumns(pivotConfig).map(c => ({ ...c, dataIndex: c.key, title: c.shortTitle, sorter: true}))}
        dataSource={formatTableData(resultSet.tableColumns(pivotConfig), resultSet.tablePivot(pivotConfig))}
        size="small"
        scroll={{ y: 'auto', x: '100%' }}
      />
  ),
  number: ({ resultSet }) => (
    <Row
      type="flex"
      justify="center"
      align="middle"
      style={{
        height: "100%"
      }}
    >
      <Col>
        {resultSet.seriesNames().map(s => (
          <Statistic value={numberFormatter(resultSet.totalRow()[s.key])} />
        ))}
      </Col>
    </Row>
  ),
  map: ({ resultSet }) => (
    <Map />
  )
};
const TypeToMemoChartComponent = Object.keys(TypeToChartComponent)
  .map(key => ({
    [key]: React.memo(TypeToChartComponent[key])
  }))
  .reduce((a, b) => ({ ...a, ...b }));

const SpinContainer = styled.div`
  text-align: center;
  padding: 30px 50px;
  margin-top: 30px;
`
const Spinner = () => (
  <SpinContainer>
    <Spin size="large"/>
  </SpinContainer>
)

const renderChart = Component => ({ resultSet, error, height, pivotConfig }) =>
  (resultSet && <Component height={height} pivotConfig={pivotConfig} resultSet={resultSet} />) ||
  (error && error.toString()) || <Spinner />;

const ChartRenderer = ({ vizState, chartHeight }) => {
  const { query, chartType, pivotConfig } = vizState;
  const component = TypeToMemoChartComponent[chartType];
  const renderProps = useCubeQuery(query); // const { resultSet, isLoading, error, progress }
  
  /*
  const [tableHeight, setTableHeight] = useState(600);
  // ref is the Table ref.
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const node = ref.current;
    const { top } = node.getBoundingClientRect();

    // normally TABLE_HEADER_HEIGHT would be 55.
    setTableHeight(window.innerHeight - top - 55); //TABLE_HEADER_HEIGHT);
  }, [ref]);
  */

  return component && renderChart(component)({ height: chartHeight, pivotConfig: pivotConfig, ...renderProps });
};

ChartRenderer.propTypes = {
  vizState: PropTypes.object,
  cubejsApi: PropTypes.object
};

ChartRenderer.defaultProps = {
  vizState: {},
  chartHeight: '100%', // 300
  cubejsApi: null
};

export default ChartRenderer;