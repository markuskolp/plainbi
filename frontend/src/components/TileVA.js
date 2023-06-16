import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { Segmented, Select, Image, Table, Tag, message } from "antd";
import { Typography } from 'antd';
import { PageHeader } from "@ant-design/pro-layout";
const { Title, Link, Text } = Typography;


const TileVA = (props) => {

  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]); 
  const [selectedYear, setSelectedYear] = useState(); 
  const [selectedCategory, setSelectedCategory] = useState(); 
  const [availableYears, setAvailableYears] = useState(); 
  const [availableCategories, setAvailableCategories] = useState(); 

  useEffect(() => {
    setSelectedYear(new Date().getFullYear()); // set current year as initially selected year
    setSelectedCategory("Eigenveranstaltung");
    initializeApp();
  }, []);

  const initializeApp = async () => {
    await Axios.get("/api/crud/DWH.CONFIG.v_portal_veranstaltung?order_by=beginn_dt,ende_dt", {headers: {Authorization: props.token}}).then(
      (res) => {
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setData(resData);
        // get distinct years from all fair events
        setAvailableYears(
            getUniqueYears(resData).map((row) => ({
                value: row,
                label: row
              })
            )
        );
        // get distinct years from all fair events
        setAvailableCategories(
          getUniqueCategories(resData).map((row) => ({
              value: row,
              label: row
            })
          )
      );
      setLoading(false);
      }
    ).catch(
      function (error) {
        setError(true);
        setLoading(false);
        message.error('Es gab einen Fehler beim Laden der Daten.');
      }
    );
  };


  const getUniqueYears = (arr) =>  {
    // extract all years
    let tmpArr = arr.map((row) => ({ value: row.jahr}));
    //console.log("tmpArr-1: " + JSON.stringify(tmpArr));
    // get distinct years
    tmpArr = [...new Set(tmpArr.map(item => item.value))]
    //console.log("tmpArr-2: " + JSON.stringify(tmpArr));
    // sort
    tmpArr = tmpArr.sort((a, b) => a.value - b.value);
    return tmpArr;
  };

  const getUniqueCategories = (arr) =>  {
    // extract all categories
    let tmpArr = arr.map((row) => ({ value: row.kategorie}));
    //console.log("tmpArr-1: " + JSON.stringify(tmpArr));
    // get distinct categories
    tmpArr = [...new Set(tmpArr.map(item => item.value))]
    //console.log("tmpArr-2: " + JSON.stringify(tmpArr));
    // sort
    tmpArr = tmpArr.sort((a, b) => {
      let nameA = a.toUpperCase(); // ignore upper and lowercase
      let nameB = b.toUpperCase(); // ignore upper and lowercase
      if (nameA < nameB) {
        return -1;
      }
      if (nameA > nameB) {
        return 1;
      }
    
      // names must be equal
      return 0;
    });
    return tmpArr;
  };
  
  const columns = [
    {
      title: "Zeitraum",
      dataIndex: "zeitraum",
      key: "zeitraum",
      width: 200,
      render: (zeitraum, record) => (<React.Fragment><Text>{zeitraum}</Text></React.Fragment>)
    },
    {
      title: " ",
      dataIndex: "logo_url",
      key: "logo_url",
      //width: 140,
      //minwidth: 200,
      render: (logo_url) => (<Image preview={false} height={30} maxWidth={80} src={logo_url} fallback={"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="}/> )
    },
    {
      title: "Messe",
      dataIndex: "name",
      key: "name",
      width: 250,
      render: (name, record) => (
        <React.Fragment>
          <Link href={record.url} target='_blank'><b>{name}</b></Link>
        </React.Fragment>
        )
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 50,
      render: (status,) => (<React.Fragment><Tag color={(status === "aktiv" ? "blue" : (status === "geplant" ? "volcano" : ""))} >{status.toUpperCase()}</Tag></React.Fragment>)
    }

  ];


const onTableChange = (pagination, filters, sorter, extra) => {
  console.log('params', pagination, filters, sorter, extra);
};


const handleYearChange = (value) => {
  console.log('handleYearChange: ' + value);
  setSelectedYear(value);
};

const handleCategoryChange = (value) => {
  console.log('handleCategoryChange: ' + value);
  setSelectedCategory(value);
};

  return (
    <React.Fragment>
      <PageHeader
              //onBack={() => window.history.back()}
              title="Veranstaltungen"
              subTitle=""
              extra={[
                <React.Fragment>
                  <Select 
                    defaultValue="2023"
                    style={{
                      width: 120,
                    }}
                    onChange={handleYearChange}
                    options={availableYears}
                  />
                  <Segmented 
                    defaultValue="Eigenveranstaltung" 
                    options={availableCategories}
                    onChange={handleCategoryChange}
                  />
                </React.Fragment>
              ]}
            />
      
      <Table 
            pagination={false} 
            size="middle" 
            columns={columns}
            //dataSource={data} 
            dataSource={data && selectedYear && selectedCategory && data.filter((row) => (row.jahr == selectedYear && row.kategorie == selectedCategory))} // show fair events belonging to selected year
            onChange={onTableChange}
            loading={loading}
            rowKey="id"
            />
    </React.Fragment>
  );
};

export default TileVA;

/*
<h1>Veranstaltungen</h1>
      <br />
      <Space size="large">
        <Select 
          defaultValue="2023"
          style={{
            width: 120,
          }}
          onChange={handleYearChange}
          options={availableYears}
        />
        <Radio.Group 
          defaultValue="Eigenveranstaltung" 
          options={availableCategories}
          onChange={handleCategoryChange}
          optionType="button"
        />
      </Space>
*/