import React from "react";
import Table from "../components/Table";
import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { Alert, Button, notification, Form, Collapse } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { DownloadOutlined } from "@ant-design/icons";
import LoadingMessage from "../components/LoadingMessage";
import { message } from "antd";
import Axios from "axios";
import {Sorter} from "../utils/sorter";
import CRUDFormItem from "../components/CRUDFormItem";

const AdhocRuntime = (props) => {

  let { id } = useParams();
  const [queryParameters] = useSearchParams()
  let format = queryParameters.get("format");

  const navigate = useNavigate();
  
  const [adhoc, setAdhoc] = useState([]);
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [errorDetail, setErrorDetail] = useState('');
  
  const [paramData, setParamData] = useState([]);

  useEffect(() => {
    getAdhoc();
    // if format is Excel (XLSX) or CSV, then redirect to API call (to download file)
    if (format === 'XLSX' || format === 'CSV') {
      console.log("getting data as file ...");
      getBlobData(format);
      navigate("/");
    } else {
    // else show the data in the web page
      console.log("loading data ...");
      getData();
    }
  }, []);

  //TODO: pagination

  const getAdhoc = async () => {
    await Axios.get("/api/repo/adhoc/"+id, {headers: {Authorization: props.token}}).then(
      (res) => {
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setAdhoc(resData);
        //console.log(res);
      }
      ).catch(
        function (error) {
          setLoading(false);
          setError(true);
          setErrorMessage('Es gab einen Fehler beim Laden des Adhoc.');
          console.log("error.message: " + error.message);
          console.log("error.response: " + error.response);
          console.error('Request Failed:', error.config);
        }
      );
  };

  const getData = async () => {
    setLoading(true);
    setError(false);
    var _adhocparams = "";
    ///adhoc/<id>/data?params=param1:value1,param2:value2
    /* kurz auskommentiert
    if (id === "20" || id === "22" || id === "1" || id === "10" ) {
      //_adhocparams = "?params=LANDISO2:TR,LAND:Deutschland^Italien"; // LANDISO2, LAND
      _adhocparams = "?params=LANDISO2:"+paramData["land"]+",VERANSTALTUNG_NR:"+paramData["veranstaltung"]+",VERANSTALTUNGSREIHE_NR:"+paramData["veranstaltungsreihe"]+",JAHR:"+paramData["jahr"]; 
    }
    */
    console.log("getData uri: " + "/api/repo/adhoc/"+id+"/data"+_adhocparams);
    await Axios.get("/api/repo/adhoc/"+id+"/data"+_adhocparams, {headers: {Authorization: props.token}}).then(
      (res) => {
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        const resDataColumns = (res.data.length === 0 || res.data.length === undefined ? res.data.columns : res.columns); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setData(resData);
        console.log(JSON.stringify(resDataColumns));
        setColumns(resDataColumns);
        setLoading(false);
      }
      ).catch(
        function (error) {
          setLoading(false);
          setError(true);
          setErrorMessage('Es gab einen Fehler beim Laden der Daten');
          setErrorDetail(error.response.data.detail);
          console.log(error);
          console.log(error.response.data.message);
        }
      );  
  };

  
  const getBlobData = async (_format) => {
    const dt = new Date().toISOString().substring(0,19);

    var _adhocparams = "";
    ///adhoc/<id>/data?params=param1:value1,param2:value2
    /* kurz auskommentiert
    if (id === "20" || id === "22" || id === "1" || id === "10" ) {
      //_adhocparams = "?params=LANDISO2:TR,LAND:Deutschland^Italien"; // LANDISO2, LAND
      _adhocparams = "&params=LANDISO2:"+paramData["land"]+",VERANSTALTUNG_NR:"+paramData["veranstaltung"]+",VERANSTALTUNGSREIHE_NR:"+paramData["veranstaltungsreihe"]+",JAHR:"+paramData["jahr"]; 
    }
    */
    console.log("getBlobData uri: " + "/api/repo/adhoc/"+id+"/data?format="+_format+_adhocparams);

    console.log("111");
    await Axios.get("/api/repo/adhoc/"+id+"/data?format="+_format+_adhocparams, {responseType: 'blob', headers: {Authorization: props.token}}).then(
      (res) => {
        console.log("aaa");
        console.log(res.data);
        // create file link in browser's memory
        const href = URL.createObjectURL(res.data);
    
        // create "a" HTML element with href to file & click
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', 'Adhoc_'+id+"_"+dt+"."+_format.toLowerCase()); //or any other extension
        document.body.appendChild(link);
        link.click();
    
        // clean up "a" element & remove ObjectURL
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
      }
      ).catch(
        function (error) {
          setError(true);
          setErrorMessage('Es gab einen Fehler beim Laden der Daten als ' + _format);
          setErrorDetail(error.response.data.detail);
          console.log("getBlobData - error: " + error);
          console.log(error);
          console.log(error.response.data.message);
        }
      );  
  };

  const downloadData = (format) => {
    getBlobData(format);
  }
  ;


    // return a column to be used as metadata for a Table component
    function getColumn(column_label, column_name) {
      return {
        title: column_label,
        dataIndex: column_name,
        sorter: {
          compare: Sorter.DEFAULT,
          multiple: 3,
        },
        //key: column_name
        width: column_label.length * 10 // width of column relative to column_label
        //render
      };
    }

//    let title = "A_" + id + ": t.b.d.";

  const handleParamChange = (key, value) =>{
    setParamData({...paramData, [key]: value}); 
    console.log("paramData: " + JSON.stringify(paramData));
    console.log("handleParamChange - key: " + key + " / value: " + value);
  }

  
  const handleOk = () => {
    getData();
  };

  const layoutpage = {
    labelCol: { span: 4 },
    wrapperCol: { span: 8 }
  };

  const filterCollapse = [
    {
      key: '1',
      label: 'Filter',
      children: 'text',
    }
  ];
  //<Collapse items={filterCollapse} bordered={false} defaultActiveKey={['1']} />


  return (
    <React.Fragment>
       
      <PageHeader
        onBack={() => (window.location.href = "/")}
        title={adhoc.name}
        subTitle=""
        extra={[
          <Button key="1" type="primary" icon={<DownloadOutlined />} onClick={() => downloadData("CSV")}> 
            CSV
          </Button>,
          <Button key="2" type="primary" icon={<DownloadOutlined />} onClick={() => downloadData("XLSX")}> 
            Excel
          </Button>
        ]}
      />
      <br />
      <div>
        {loading ? 
        (
          <LoadingMessage />
        ) : 
        (
          error ? 
          (
            <Alert
              message={errorMessage}
              description={errorDetail}
              type="error"
              showIcon
            />
          ) : 
          ( data && columns && 
            
            <Table 
              size="small"
              //columns={columns}
              columns={columns.map((column) => {
                  return getColumn(column, column); 
                })
              }
              dataSource={data}
              pagination={{ pageSize: 50 }}
              //scroll={{ y: 'calc(100vh - 400px)' }} // change later from 400px dynamically to the height of the header, page header and footer
              scroll={{ y: 'calc(100vh - 400px)', x: 'max-content'  }} // change later from 400px dynamically to the height of the header, page header and footer
              loading={loading}
              rowKey="id"
            />
            )
        )
        }
      </div>
    </React.Fragment>
  );
};

export default AdhocRuntime;

/*

      { (id === "20" || id === "22" || id === "1" || id === "10" ) ? (
          <Form {...layoutpage} layout="horizontal">
            {
              (id === "20" ) ? (
                <React.Fragment>
                  <CRUDFormItem type="new" name="veranstaltung" label="Veranstaltung" required="false" isprimarykey="true" editable="true" lookupid="veranstaltung_fuer_av" ui="lookup" defaultValue="" onChange={handleParamChange} tooltip="" token={props.token}/>
                  <CRUDFormItem type="new" name="land" label="Land" required="false" isprimarykey="true" editable="true" lookupid="land_gesichert" ui="lookup" defaultValue="" onChange={handleParamChange} tooltip="" token={props.token}/>
                </React.Fragment>
              ) : ""
            }
            {
              (id === "22" ) ? (
                <React.Fragment>
                  <CRUDFormItem type="new" name="land" label="Land" required="false" isprimarykey="true" editable="true" lookupid="land" ui="lookup" defaultValue="" onChange={handleParamChange} tooltip="" token={props.token}/>
                </React.Fragment>
              ) : ""
            }
            {
              (id === "1" ) ? (
                <React.Fragment>
                  <CRUDFormItem type="new" name="veranstaltungsreihe" label="Veranstaltungsreihe" required="false" isprimarykey="true" editable="true" lookupid="veranstaltungsreihe_fuer_messestat" ui="lookup" defaultValue="" onChange={handleParamChange} tooltip="" token={props.token}/>
                </React.Fragment>
              ) : ""
            }
            {
              (id === "10" ) ? (
                <React.Fragment>
                  <CRUDFormItem type="new" name="veranstaltungsreihe" label="Veranstaltungsreihe" required="false" isprimarykey="true" editable="true" lookupid="veranstaltungsreihe_fuer_messestat" ui="lookup" defaultValue="" onChange={handleParamChange} tooltip="" token={props.token}/>
                  <CRUDFormItem type="new" name="jahr" label="Jahr" required="false" isprimarykey="true" editable="true" lookupid="jahr_fuer_messestat" ui="lookup" defaultValue="" onChange={handleParamChange} tooltip="" token={props.token}/>
                </React.Fragment>
              ) : ""
            }
            <Form.Item
              wrapperCol={{
                offset: 4,
                span: 8,
              }}
            >
              <Button type="primary" htmlType="submit" onClick={handleOk}>Ausführen</Button>
            </Form.Item>
          </Form>
        ) : ""
      }
      */