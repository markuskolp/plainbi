import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import {
  Button,
  Typography,
  Layout,
  Input,
  Space,
  Popconfirm,
  message,
  Tooltip,
  Pagination 
} from "antd";
import Table from "./Table";
import {Sorter} from "../utils/sorter";
import {
  CaretUpFilled,
  CaretDownFilled
} from '@ant-design/icons';
import { PageHeader } from "@ant-design/pro-layout";
import { EditOutlined, PlusOutlined, DeleteOutlined } from "@ant-design/icons";
import CRUDModal from "./CRUDModal";
const { Link, Text } = Typography;

/*
Enum datatype {
  text
  number
  date
  datetime
  boolean
}

Enum ui {
  hidden
  label
  textinput
  numberinput
  datepicker
  datetimepicker
  lookup
  lookupn (allow new values)
  textarea
  textarea_sql
  textarea_markdown
  switch
  password
  email
}
*/

const CRUDPage = ({ name, tableName, tableForList, tableColumns, pkColumns, allowedActions, versioned, datasource, isRepo, lookups, token }) => {
    
  const [loading, setLoading] = useState(true);
  const [tableData, setTableData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  //const [pkColumn, setPkColumn] = useState();
  const [currentPK, setCurrentPK] = useState();
  const [modalMode, setModalMode] = useState("new"); // new/edit
  const [offset, setOffset]=useState(0);
  const [limit, setLimit]=useState(20);
  const [order, setOrder]=useState("");
  const [totalCount, setTotalCount]=useState();
  const [filter, setFilter]=useState();
  const [tableParamChanged, setTableParamChanged]=useState(false);
  const [typingTimeout, setTypingTimeout]=useState(null);
  const [activateLookups, setActivateLookups]=useState(true);
  
  let api = "/api/crud/";
  api = isRepo === 'true' ? "/api/repo/" : "/api/crud/" + (datasource ? datasource+'/' : ''); // switch between repository tables and other datasources /api/crud/<db>/<table>
  
  const [lookupData, setLookupData] = useState([]);
  const [filteredTableData, setFilteredTableData] = useState(null);

  console.log("lookups: " + lookups);
  console.log("tableForList: " + tableForList);

  useEffect(() => {
    getTableData(tableName);
    lookups ? getLookupDataAll() : ""; // if lookups where delivered, then get all lookup values
    //setPkColumn(pkColumns); 
  }, [tableName, tableParamChanged]);

  // getTableData
  /*
  const getTableData = async (tableName) => {
    setTableData(null);
    await Axios.get(api+tableName+(versioned ? "?v" : ""), {headers: {Authorization: token}}).then(
    //await Axios.get(api+tableName+(versioned ? "?v" : "")+(versioned ? "&limit="+limit : "?limit="+limit), {headers: {Authorization: token}}).then(
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
  */
    const getTableData = async (tableName) => {

      setLoading(true);
      setTableData(null);

      const queryParams = new URLSearchParams();
      if(versioned) {
        queryParams.append("v", 1);
      }
      queryParams.append("offset", offset);
      queryParams.append("limit", limit);
      if(order && order.length > 0) {
        queryParams.append("order_by", order);
      }
      if(filter && filter.length > 0) {
        queryParams.append("filter", filter);
      }
      console.log("queryParams: " + queryParams.toString());
      var endpoint = api+tableName+'?'+queryParams;

      if(tableForList && tableForList.length > 0) {
        //queryParams.append("customsql", "select * from " + tableForList);
        //queryParams.append("customsql", tableForList);
        setActivateLookups(false);
        queryParams.delete("v"); // remove versioning
        endpoint = api+tableForList+'?'+queryParams; // change tableName to tableForList
      }

      console.log("endpoint: " + endpoint);

      await Axios.get(endpoint, {headers: {Authorization: token}}).then(
      //await Axios.get(api+tableName+'?'+queryParams, {headers: {Authorization: token}}).then(
        (res) => {
          const tc = (res.data.length === 0 || res.data.length === undefined ? res.data.total_count : res.total_count); // take data directly if exists, otherwise take "data" part in JSON response
          setTotalCount(tc);
          console.log("totalCount: " + tc);
          const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
          //console.log(JSON.stringify(resData));
          setTableData(resData);
          //console.log(JSON.stringify(tableData));
          setLoading(false);
        }
        ).catch(function (error) {
          setLoading(false);
          message.error('Es gab einen Fehler beim Laden der Daten.');
        }
        )
    };

  const handleChange = (pagination, filters, sorter) => {
    const offset = pagination.current * pagination.pageSize - pagination.pageSize;
    const limit = pagination.pageSize;
    const params = {};
    console.log("offset: " + offset);
    console.log("limit: " + limit);
    console.log("sorter: " + JSON.stringify(sorter));
    var order = "";
    console.log("order sorter.length: " + sorter.length);
    console.log("order sorter hasproperty column: " + sorter.hasOwnProperty("column"));
    console.log("order sorter.order: " + sorter.order);
    if (sorter.hasOwnProperty("column")) {
      //params.order = { field: sorter.field, dir: sorter.order };
      if (!sorter.length) {
        if(sorter.order) { // only if sorter order is not undefined
          // if only 1 sort column, then take the props directly
          console.log("one sorter order");
          order = sorter.field + (sorter.order == "descend" ? " desc" : "");
        }
      } 
    }
    if (sorter.length > 1) {
      // if more than 1 sort column, then loop through them and get props
      console.log("more than one sorter order");
      for (var i = 0; i < sorter.length; i++) {
        order += sorter[i].field;
        if (sorter[i].order == "descend") { // only append descend if defined - ascend is default and does not need to be set explicitly
          order += " desc";
        }
        order += ",";
      }
      order = order.slice(0,-1); // eliminate the last comma
    }
    console.log("sort order: " + order);
    setOffset(offset);
    setLimit(limit);
    setOrder(order);

    //auto refresh of table data because table params where changed - see useEffect()
    setTableParamChanged(!tableParamChanged);
    
  };

  // removeTableRow
  const removeTableRow = async (tableName, record, pk) => {
    setLoading(true);
    let endPoint = api+tableName+"/"+pk+(versioned ? "?v" : "")+(versioned ? "&pk="+getPKParamForURL(pkColumns) : "?pk="+getPKParamForURL(pkColumns));
    console.log("removeTableRow: endPoint: " + endPoint);
    await Axios.delete(endPoint
    , {  
        headers: { 
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': token
        },
        data: {
          record
        }
      }
      ).then( 
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

  const getPKForURL = (record, _pkColumn) => {
    var pkforurl = "";
    if (_pkColumn.length <= 1) {
      console.log("only 1 pk");
      // if only 1 pk take it directly
      pkforurl = record[_pkColumn[0]];
    } else {
      console.log("composite pk");
      // if composite key, then build url-specific pk string "(key=value:key=value:...)"
      pkforurl = "(";
      for (var i = 0; i < _pkColumn.length; i++) {
        pkforurl += _pkColumn[i] + ":" + record[_pkColumn[i]];
        pkforurl += ":";
      }
      pkforurl = pkforurl.replace(/^:+|:+$/g, ''); // trim ":" at beginning and end of string
      pkforurl += ")";
    }
    console.log("getPKForURL: " + pkforurl);
    return pkforurl;
  }
  
  const getPKParamForURL = (_pkColumn) => {
    var pkforurl = "";
    if (_pkColumn.length <= 1) {
      console.log("only 1 pk");
      // if only 1 pk take it directly
      pkforurl = _pkColumn[0];
    } else {
      console.log("composite pk");
      // if composite key, then build url-specific pk string "&pk=key1,key2,..."
      for (var i = 0; i < _pkColumn.length; i++) {
        pkforurl += _pkColumn[i];
        pkforurl += ",";
      }
      pkforurl = pkforurl.replace(/^,+|,+$/g, ''); // trim "," at beginning and end of string
    }
    console.log("getPKParamForURL: " + pkforurl);
    return pkforurl;
  }

    // deleteConfirm
    const deleteConfirm = (record) => {
      console.log("deleteConfirm for table: " + tableName);
      console.log(record);
      //pkColumns ? console.log(record[pkColumns[0]]) : console.log("no pk");
      //removeTableRow(tableName, record, record[pkColumns[0]]);
      removeTableRow(tableName, record, getPKForURL(record, pkColumns));
    };

    // showModal
    const showEditModal = (record) => {
      console.log("showEditModal for table: " + tableName);
      console.log(record);
      pkColumns ? console.log(record[pkColumns[0]]) : console.log("no pk");
      //setCurrentPK(record[pkColumns[0]]);
      setCurrentPK(getPKForURL(record, pkColumns));
      setModalMode("edit");
      setShowModal(true);
    };
    const showCreateModal = () => {
      setCurrentPK(null);
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
      fixed: "right",
      render: (_, record) => ([
        <Space>
          {deleteAllowed && pkColumns &&
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
          {updateAllowed && pkColumns &&
          <Link onClick={(e) => { showEditModal(record, e); }}>
            <EditOutlined style={{ fontSize: "18px" }} />
          </Link>
          }
        </Space>
      ])
    };
  }

  // getLookupData
  const getLookupData = (lookupid) => Axios.get("/api/repo/lookup/"+lookupid+"/data", {headers: {Authorization: token}}).then(
      (res) => {
        return {lookup: lookupid, lookupdata: (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data)}
      }
  );

  const getLookupDataAll = () => {
    Promise.all(lookups.map(getLookupData)).then( (data) => {
      console.log("data length: " + data.length);
      //console.log("data: " + JSON.stringify(data));
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
    //console.log("lookupData: " + JSON.stringify(lookupData));   
    //var relevantLookupData = lookupData; //[0].values; //.filter((row) => row.lookup == lookupid).values;   //
    var relevantLookupData = lookupData.filter((row) => row.lookup == lookupid)[0]; //.values;   //
    //console.log("relevantLookup: " + JSON.stringify(relevantLookupData));   
    //console.log("relevantLookupData data length: " + relevantLookupData.lookupdata);   
    for (var i = 0; i < relevantLookupData.lookupdata.length; i++) {
      //console.log("r: " + relevantLookupData.lookupdata[i].r + " / d: " + relevantLookupData.lookupdata[i].d);
      if (relevantLookupData.lookupdata[i].r == lookupreturnid) {
        //console.log("found - label:" + relevantLookupData.lookupdata[i].d);
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
  function getColumn(column_label, column_name, datatype) {
    return {
      //title: column_label
      title: ({ sortColumns }) => {
        const sortedColumn = sortColumns?.find(({ column }) => column.key === column_name);
        return (
          <div class="th-div-custom">
            <span class="th-div-custom-title">{column_label}</span>
            <span>{sortedColumn ? (
              sortedColumn.order === "ascend" ? (
                <CaretUpFilled style={{fontSize: '14px'}}/>
              ) : (
                sortedColumn.order === "descend" ? (
                  <CaretDownFilled style={{fontSize: '14px'}}/>
                ) :  <CaretUpFilled className="inactive" style={{fontSize: '14px'}} />
              )
            ) : <CaretUpFilled className="inactive" style={{fontSize: '14px'}} />}
            </span>
          </div>
        )
      }
      ,
      dataIndex: column_name,
      sorter: {
        compare: Sorter.DEFAULT,
        multiple: 3,
      },
      ellipsis: {
        showTitle: false,
      },
      render: (text, record) => (
        // if datetime then trim milliseconds
        // tooltip because of ellipsis above
        <Tooltip placement="topLeft" title={text}>          
          {(datatype === "datetime" && text) ? text.substring(0,19) : text} 
        </Tooltip>
      )
      , key: column_name
      , width: 100
    };
  }

    // return a column to be used as metadata for a Table component
    // this is from the type "lookup"
    const getLookupColumn = (column_label, column_name, lookupid) => {
      return {
        //title: column_label
      title: ({ sortColumns }) => {
        const sortedColumn = sortColumns?.find(({ column }) => column.key === column_name);
        return (
          <div class="th-div-custom">
            <span class="th-div-custom-title">{column_label}</span>
            <span>{sortedColumn ? (
              sortedColumn.order === "ascend" ? (
                <CaretUpFilled style={{fontSize: '14px'}}/>
              ) : (
                sortedColumn.order === "descend" ? (
                  <CaretDownFilled style={{fontSize: '14px'}}/>
                ) :  <CaretUpFilled className="inactive" style={{fontSize: '14px'}} />
              )
            ) : <CaretUpFilled className="inactive" style={{fontSize: '14px'}} />}
            </span>
          </div>
        )
      }
      ,
        dataIndex: column_name,
        sorter: {
          compare: Sorter.DEFAULT,
          multiple: 3,
        },
        key: column_name,
        width: 100,
        ellipsis: {
          showTitle: false,
        },
        render: (text, record, column_name) => (
          // tooltip because of ellipsis above
          <Tooltip placement="topLeft" title={getLookupValue(text, lookupid, column_name)}>   
            <Text>{getLookupValue(text, lookupid, column_name)}</Text>
          </Tooltip>
        )
      };
    }

    /*
    const searchData = (value) => {
      console.log("searching value: " + value );
      console.log(tableData);
 
      const tmpFilteredTableData = tableData.filter(o =>
        Object.keys(o).some(k =>
          String(o[k])
            .toLowerCase()
            .includes(value.toLowerCase())
        )
      );

      setFilteredTableData( tmpFilteredTableData );
    };
    */

    const searchData = (value) => {
      console.log("setting filter: " + value );
      setFilter(value);
      //auto refresh of table data because table params where changed - see useEffect()
      setTableParamChanged(!tableParamChanged);
    }

    const searchDataWithTimeout = (value) => {
      console.log("setting filter: " + value );
      if(typingTimeout) clearTimeout(typingTimeout);
      setTypingTimeout( 
        setTimeout(() => {
          setFilter(value);
          setOffset(0); // reset pagination to page 1 (offset=0) --> todo: Ant Table muss noch darauf reagieren -> optisch steht es noch auf einer anderen Page
          //auto refresh of table data because table params where changed - see useEffect()
          setTableParamChanged(!tableParamChanged);
        }, 600)
      );
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
                {lookupData && (
                  <React.Fragment>
                    <Input.Search
                      placeholder="Suche ..."
                      //enterButton
                      onSearch={(value) => {searchData(value)}}
                      onChange={(e) => {searchDataWithTimeout(e.target.value)}}
                      style={{marginBottom:20,width:500}}
                      allowClear 
                    />
                    <Table
                          size="small"
                          columns={tableColumns && tableColumns.filter((column) => !column.showdetailsonly) // show all columns, that are not limited to the detail view (modal) ...
                            .map((column) => {
                              return ((column.ui === "lookup" && activateLookups) ? getLookupColumn(column.column_label, column.column_name, column.lookup) : getColumn(column.column_label, column.column_name, column.datatype));
                            })
                            .concat(getColumnAction(allowedActions.includes("delete"), allowedActions.includes("update")))} // .. also add action buttons (delete, edit), if allowed

                          dataSource={filteredTableData == null ? tableData : filteredTableData}
                          //rowKey="key"
                          //dataSource={pageMetadataRelevant.name.table_columns}
                          //pagination={<Pagination  total={25} showTotal={(total) => `Gesamt ${total} Einträge`} defaultPageSize={25}/>}
                          //pagination={{position: 'topRight'}}
                          pagination={{ defaultPageSize: 20, total: totalCount, hideOnSinglePage: true, showTotal: (total) => `Gesamt: ${total}` }}
                          scroll={{ y: 'calc(100vh - 400px)', x: 'max-content' }} // change later from 400px dynamically to the height of the header, page header and footer
                          tableLayout="auto"
                          //pagination={false}
                          //scroll={{ y: 500 }}
                          //scroll={{ x: 300 }}
                          loading={loading}
                          /*locale={{
                            emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={'keine Daten'}/>,
                            triggerDesc: 'Klicken um absteigend zu sortieren',
                            triggerAsc: 'Klicken um aufsteigend zu sortieren', 
                            cancelSort: 'Klicken um Sortierung aufzuheben'
                          }}*/
                          onChange={handleChange}
                          //pagination={{
                          //  total: totalCount // total count returned from backend
                          //}}
                        />
                    </React.Fragment>
                  ) 
                }
            
            {showModal &&
            <CRUDModal tableColumns={tableColumns} handleCancel={closeModal} handleSave={closeAndRefreshModal} type={modalMode} tableName={tableName} pk={currentPK} pkColumns={pkColumns} versioned={versioned} datasource={datasource} isRepo={isRepo} token={token}/>
            }

            </React.Fragment>
    );

};

export default CRUDPage;

