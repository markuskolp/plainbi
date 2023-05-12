import React from "react";
import Table from "../components/Table";
import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { Button, notification } from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { DownloadOutlined } from "@ant-design/icons";
import { LoadingMessage } from "../components/LoadingMessage";
import { message } from "antd";
import Axios from "axios";
import {Sorter} from "../utils/sorter";

const AdhocRuntime = () => {

  let { id } = useParams();
  const [queryParameters] = useSearchParams()
  let format = queryParameters.get("format");

  const navigate = useNavigate();
  
  const [adhoc, setAdhoc] = useState([]);
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);

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
    await Axios.get("/api/repo/adhoc/"+id).then(
      (res) => {
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
        //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setAdhoc(resData);
      }
      ).catch(
        function (error) {
          setLoading(false);
          message.error('Es gab einen Fehler beim Laden des Adhoc.');
        }
      );  
  };

  const getData = async () => {
    setLoading(true);
    await Axios.get("/api/repo/adhoc/"+id+"/data").then(
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
          message.error('Es gab einen Fehler beim Laden der Daten.');
        }
      );  
  };

  
  const getBlobData = async (_format) => {
    const dt = new Date().toISOString().substring(0,19);
    await Axios.get("/api/repo/adhoc/"+id+"/data?format="+_format, {responseType: 'blob'}).then(
      (res) => {
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
            message.error('Es gab einen Fehler beim Laden der Daten als ' + _format);
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
        //width: 50,
        //render
      };
    }

//    let title = "A_" + id + ": t.b.d.";

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
        {loading ? (
          <h1>Lädt...</h1>
        ) : ( data && columns && 
          //<LoadingMessage />
          <Table 
            size="small"
            //columns={columns}
            columns={columns.map((column) => {
                return getColumn(column, column); 
              })
            }
            dataSource={data}
            pagination={{ pageSize: 50 }}
            scroll={{ y: 'calc(100vh - 400px)' }} // change later from 400px dynamically to the height of the header, page header and footer
            loading={loading}
          />
        )}
      </div>
    </React.Fragment>
  );
};

export default AdhocRuntime;
