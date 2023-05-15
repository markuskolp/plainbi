import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import {
  Table,
  Button,
  Typography,
  Layout,
  Input,
  Space,
  Popconfirm,
  message
} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { EditOutlined, PlusOutlined, DeleteOutlined } from "@ant-design/icons";
import CRUDModal from "./CRUDModal";
const { Link, Text } = Typography;

/*
Enum datatype {
  text
  number
  date
  boolean
}

Enum ui {
  hidden
  label
  textinput
  numberinput
  datepicker
  lookup
  textarea
  textarea_sql
  textarea_markdown
  switch
  password
  email
}
*/

const CRUDPage = ({ name, tableName, tableColumns, pkColumns, allowedActions, versioned, isRepo, lookups }) => {
    
  const [loading, setLoading] = useState(true);
  const [tableData, setTableData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [pkColumn, setPkColumn] = useState();
  const [currentPK, setCurrentPK] = useState();
  const [modalMode, setModalMode] = useState("new"); // new/edit
  let api = "/api/crud/";
  api = isRepo === 'true' ? "/api/repo/" : "/api/crud/"; // switch between repository tables and other datasources
  
  const [lookupData, setLookupData] = useState([]);

  console.log("lookups: " + lookups);

  useEffect(() => {
    getTableData(tableName);
    lookups ? getLookupDataAll() : ""; // if lookups where delivered, then get all lookup values
    setPkColumn(pkColumns); // set first column from pk list // TODO: take all pk columns if composite key
  }, [tableName]);

  // getTableData
  const getTableData = async (tableName) => {
    setTableData(null);
    //await Axios.get("/api/data/table/"+tableName).then(
    await Axios.get(api+tableName+(versioned ? "?v" : "")).then(
      (res) => {
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setTableData(resData);
        console.log(JSON.stringify(tableData));
        setLoading(false);
      }
      ).catch(function (error) {
        setLoading(false);
        message.error('Es gab einen Fehler beim Laden der Daten.');
      }
      )
  };

  // removeTableRow
  const removeTableRow = async (tableName, record, pk) => {
    setLoading(true);
    await Axios.delete(api+tableName+"/"+pk+(versioned ? "?v" : ""), {  
        headers: { 
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        data: {
          record
        }
      }).then( 
      (res) => {
        getTableData(tableName);
        message.success('Erfolgreich gelöscht.');
      }
      ).catch(function (error) {
        setLoading(false);
        message.error('Es gab einen Fehler beim Löschen.');
      }
      )
  };

    // deleteConfirm
    const deleteConfirm = (record) => {
      console.log("deleteConfirm for table: " + tableName);
      console.log(record);
      pkColumn ? console.log(record[pkColumn[0]]) : console.log("no pk");
      removeTableRow(tableName, record, record[pkColumn[0]]);
    };

    // showModal
    const showEditModal = (record) => {
      console.log("showEditModal for table: " + tableName);
      console.log(record);
      pkColumn ? console.log(record[pkColumn[0]]) : console.log("no pk");
      setModalMode("edit");
      setCurrentPK(record[pkColumn[0]]);
      setShowModal(true);
    };
    const showCreateModal = () => {
      setModalMode("new");
      setShowModal(true);
    };
    // closeModal
    const closeModal = () => {
      setShowModal(false);
    }
    // closeAndRefreshModal
    const closeAndRefreshModal = () => {
      setShowModal(false);
      getTableData(tableName);
    }
    
    // add action buttons to a table record
   function getColumnAction( deleteAllowed, updateAllowed) {
    return {
      title: " ",
      key: "action",
      width: 100,
      render: (_, record) => ([
        <Space>
          {deleteAllowed && pkColumn &&
            <Popconfirm
            title="Löschen"
            description="Wirklich löschen?"
            onConfirm={(e) => { deleteConfirm(record, e); }}
            //onCancel={cancel}
            okText="Ja"
            cancelText="Nein"
            //<Link onClick={(e) => { this.onDelete(record.key, e); }}>
            >
            <DeleteOutlined style={{ fontSize: "18px" }} />
            </Popconfirm>
          }
          {updateAllowed && pkColumn &&
          <Link onClick={(e) => { showEditModal(record, e); }}>
            <EditOutlined style={{ fontSize: "18px" }} />
          </Link>
          }
        </Space>
      ])
    };
  }

  // getLookupData
  /*
  const getLookupData = async () => {

    for(var i = 0; i< lookups.length; i++) {

      //console.log("getLookupData for id: " + lookups[i]);
      
        await Axios.get("/api/repo/lookup/"+lookups[i]+"/data").then(
        (res) => {
          //const resData = res.data; 
          //const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0]); // take data directly if exists, otherwise take "data" part in JSON response
          const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
          //console.log("getLookupData result: " + JSON.stringify(resData));          
   
          return resData.map((row) => ({
            value: row.r,
            label: row.d
          }));

          // add fetched lookup data to the array of fetched lookups
          /*
          setLookupData([...lookupData, {pos: i, values: resData.map((row) => ({
                value: row.r,
                label: row.d
              }))
            }
          ]
          );
          */
          /*
          setLookupData([...lookupData, {
              lookup: lookups[i],
              values: resData.map((row) => ({
                  value: row.r,
                  label: row.d
                }))
              }
            ]
          );
          *//*
        }
      );
    }
  };
  */

  const getLookupData = (lookupid) => Axios.get("/api/repo/lookup/"+lookupid+"/data").then(
      (res) => {
        return {lookup: lookupid, lookupdata: (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data)}
      }
  );

  const getLookupDataAll = () => {
    Promise.all(lookups.map(getLookupData)).then( (data) => {
      console.log("data length: " + data.length);
      console.log("data: " + JSON.stringify(data));
      /*
      var tmpArray = [];
      for(var i = 0; i< data.length; i++) {
        const resData = data[i];
        console.log("resData: " + JSON.stringify(resData));
        tmpArray.push(resData);
      }
      console.log("tmpArray: " + JSON.stringify(tmpArray));
      */
      setLookupData(data);
    });
  }


  function getLookupValue(lookupreturnid, lookupid, column_name) {
    let displayValue = "";
    try {
    //getLookupData(lookupid);
    //console.log("getLookupValue for column: " + column_name + " / lookupreturnid: " + lookupreturnid + " / lookupid: " + lookupid);
    console.log("lookupData length: " + lookupData.length);   
    console.log("lookupData: " + JSON.stringify(lookupData));   
    //var relevantLookupData = lookupData; //[0].values; //.filter((row) => row.lookup == lookupid).values;   //
    var relevantLookupData = lookupData.filter((row) => row.lookup == lookupid)[0]; //.values;   //
    console.log("relevantLookup: " + JSON.stringify(relevantLookupData));   
    console.log("relevantLookupData data length: " + relevantLookupData.lookupdata);   
    for (var i = 0; i < relevantLookupData.lookupdata.length; i++) {
      console.log("r: " + relevantLookupData.lookupdata[i].r + " / d: " + relevantLookupData.lookupdata[i].d);
      if (relevantLookupData.lookupdata[i].r == lookupreturnid) {
        console.log("found - label:" + relevantLookupData.lookupdata[i].d);
        displayValue = relevantLookupData.lookupdata[i].d;
        break;
      }
    }
  } catch (error) {
    console.log("error in getLookupValue");
  }
    //return "lookupreturnid: " + lookupreturnid + " / lookupid: " + lookupid;
    return displayValue ? displayValue : lookupreturnid; // find displayValue otherwise return the delivered returnValue (id) of a lookup
  }

  // return a column to be used as metadata for a Table component
  function getColumn(column_label, column_name) {
    return {
      title: column_label,
      dataIndex: column_name,
      //key: column_name
      //width: 50,
    };
  }

    // return a column to be used as metadata for a Table component
    // this is from the type "lookup"
    const getLookupColumn = (column_label, column_name, lookupid) => {
      return {
        title: column_label,
        dataIndex: column_name,
        //key: column_name
        //width: 50,
        render: (text, record, column_name) => (
          <Text>{getLookupValue(text, lookupid, column_name)}</Text>
        )
      };
    }

    return (
      <React.Fragment>
      <PageHeader
              //onBack={() => window.history.back()}
              title=""
              subTitle=""
              extra={[
                allowedActions.includes("create") && 
                <Button
                  //href="/apps/edit"
                  onClick={showCreateModal}
                  key="1"
                  type="primary"
                  icon={<PlusOutlined />}
                >
                  Neu
                </Button>
                
              ]}
            />
                {lookupData && <Table
                  size="small"
                  columns={tableColumns && tableColumns.filter((column) => !column.showdetailsonly) // show all columns, that are not limited to the detail view (modal) ...
                    .map((column) => {
                      return (column.ui === "lookup" ? getLookupColumn(column.column_label, column.column_name, column.lookup) : getColumn(column.column_label, column.column_name));
                    })
                    .concat(getColumnAction(allowedActions.includes("delete"), allowedActions.includes("update")))} // .. also add action buttons (delete, edit), if allowed

                  dataSource={tableData}
                  //dataSource={pageMetadataRelevant.name.table_columns}
                  //pagination={{ pageSize: 50 }}
                  pagination={false}
                  //scroll={{ y: 500 }}
                  //scroll={{ x: 300 }}
                  loading={loading}
            /> }
            
            {showModal &&
            <CRUDModal tableColumns={tableColumns} handleCancel={closeModal} handleSave={closeAndRefreshModal} type={modalMode} tableName={tableName} pk={currentPK} versioned={versioned} isRepo={isRepo}/>
            }

            </React.Fragment>
    );

};

export default CRUDPage;
