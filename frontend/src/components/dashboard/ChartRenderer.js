import React from "react";
import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useCubeQuery } from "@cubejs-client/react";
import { Spin, Row, Col, Statistic, Modal, Typography, Image } from "antd";
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
import cubejs from "@cubejs-client/core";
import { useQuery } from "./hooks/useQuery.js";
const { Title, Link, Text } = Typography;


const numberFormatter = item => item.toLocaleString("de-DE"); 
const dateFormatter = item => moment(item).format("MMM YY");
const datetimeFormatter = item => moment(item).format("DD.MM.YYYY HH:mm");
const colors = ["#6a91ce","#7DB3FF", "#49457B", "#FF7C78"];
const xAxisFormatter = (item) => {
  return item;
  if (moment(item).isValid()) {
    return dateFormatter(item)
  } else {
    return item;
  }
}


const handleLineClick = (event, resultSet, xValue, yValues, handleDrill) => {
  console.log("handleLineClick()");
  console.log("xValue");
  console.log(xValue);
  if (yValues != null) {
      console.log("yValues != null");
      console.log("yValues");
      console.log(yValues);
      console.log("event.xValues");
      console.log(event.xValues);
      const drillQuery = resultSet.drillDown(
        {
          xValues: event.xValues,
          yValues: yValues
        }
      );
      console.log("drillQuery");
      console.log(drillQuery);
      handleDrill(drillQuery);
      //setOpen(true);
  }
};
  
const handleBarClick = (event, resultSet, yValues, handleDrill) => {
  console.log("handleBarClick()");
  if (event.xValues != null) {
      console.log("event.xValues != null");
      console.log("event.xValues");
      console.log(event.xValues);
      console.log("yValues");
      console.log(yValues);
      const drillQuery = resultSet.drillDown(
        {
          xValues: event.xValues,
          yValues
        }
      );
      console.log("drillQuery");
      console.log(drillQuery);
      handleDrill(drillQuery);
      //setOpen(true);
  }
};
  

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
  line: ({ resultSet, height, handleDrill }) => (
    <CartesianChart resultSet={resultSet} height={height} ChartComponent={LineChart}>
      {resultSet.seriesNames().map((series, i) => (
        <Line
          key={series.key}
          stackId="a"
          dataKey={series.key}
          name={series.title}
          stroke={colors[i]}
          dot={false} 
          strokeWidth={2}
          activeDot={{ onClick: event => handleLineClick(event, resultSet, resultSet.series(), series.yValues, handleDrill) }} // todo: rausfinden wie man die richtige Linie erwischt und dann den Wert der x-Achse
        />
      ))}
    </CartesianChart>
  ),
  bar: ({ resultSet, height, pivotConfig, handleDrill  }) => (
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
          onClick={event => handleBarClick(event, resultSet, series.yValues, handleDrill)}
        />
      ))}
    </CartesianChart>
  ),
  verticalbar: ({ resultSet, height, pivotConfig, handleDrill }) => (
    <CartesianChart resultSet={resultSet} height={height} ChartComponent={BarChart} layout="vertical">
      {resultSet.seriesNames().map((series, i) => (
        <Bar
          key={series.key}
          //stackId="a"
          dataKey={series.key}
          name={series.title}
          fill={colors[i]}
          onClick={event => handleBarClick(event, resultSet, series.yValues, handleDrill)}
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
  table: ({ resultSet, handleDrill }) => (
    <Table
      pagination={false}
      columns={resultSet.tableColumns().map(c => ({ ...c, dataIndex: c.key, title: c.shortTitle, sorter: true}))} // take shortTitle (that means without name of data model (cube))
      //columns={resultSet.tableColumns().map(c => ({ ...c, dataIndex: c.key, title: c.shortTitle, sorter: true, render:(text, row)=><Link>{text + row["Eingang.eingangstorGruppe"]}</Link>}))} // take shortTitle (that means without name of data model (cube))
      dataSource={resultSet.tablePivot()}
      size="small"
      //scroll={{ y: 'calc(100vh - 400px)', x: 'max-content' }}
      //scroll={{ x: true }}
      //scroll={{ y: tableHeight }}
      scroll={{ y: 'auto', x: '100%' }}
      //scroll={{ y: 'auto', x: 'auto' }}
      //onClick={event => handleBarClick(event, resultSet, series.yValues, handleDrill)}
      //tableLayout="auto"
      //          
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
  data_status: ({ resultSet }) => (
    <Text style={{fontSize:"smaller"}}>Datenstand: {datetimeFormatter(resultSet.tablePivot()[0][resultSet.seriesNames()[0].key])}</Text>
  ),
  map: ({ resultSet }) => (
    <Map resultSet={resultSet} />
  ),
  image: ({ resultSet }) => (
    //console.log(resultSet.chartPivot()[0].x),
    <Image
      //width={200}
      //height={200}
      src={resultSet.chartPivot()[0] ? resultSet.chartPivot()[0].x : ""}
        fallback="data:image/png;base64,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"
    />
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

const renderChart = Component => ({ resultSet, error, height, pivotConfig, handleDrill }) =>
(resultSet && <Component height={height} pivotConfig={pivotConfig} resultSet={resultSet} handleDrill={handleDrill} />) ||
(error && error.toString()) || <Spinner />;

const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDI2NjYzNDcsImV4cCI6MTcwMjc1Mjc0N30.D8iCMGAH72GgOjNm6dWuFWHStlrzVVAEpomOk4eKK5Y';
//const cubejsApi = cubejs(token, { apiUrl: 'http://localhost:4000/cubejs-api/v1' });
const cubejsApi = cubejs(token, { apiUrl: '/cubejs-api/v1' });

const ChartRenderer = ({ vizState, chartHeight, handleDrill }) => {

  const [querystate, setQuerystate] = useState(); 
  const { query, chartType, pivotConfig } = vizState;

  const component = TypeToMemoChartComponent[chartType];
  //const renderProps = useCubeQuery(query, {resetResultSetOnChange: true}); // const { resultSet, isLoading, error, progress }
  const renderProps = useQuery(query, {cubejsApi: cubejsApi, resetResultSetOnChange: true}); // const { resultSet, isLoading, error, progress }
  
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

  return component && renderChart(component)({ height: chartHeight, pivotConfig: pivotConfig, ...renderProps, handleDrill });
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

/*
  console.log("ChartRenderer - vizState");
  console.log(vizState);
  console.log("ChartRenderer - renderProps");
  console.log(renderProps.resultSet);

*/