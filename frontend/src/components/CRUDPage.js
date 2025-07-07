import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import {
  Button,
  Typography,
  Layout,
  Input,
  Space,
  Popconfirm,
  message,
  Tooltip,
  Pagination ,
  Breadcrumb, Alert
} from "antd";
import Table from "./Table";
import {Sorter} from "../utils/sorter";
import {
  CaretUpFilled,
  CaretDownFilled
} from '@ant-design/icons';
import { PageHeader } from "@ant-design/pro-layout";
import { EditOutlined, PlusOutlined, DeleteOutlined, CopyOutlined, DownloadOutlined } from "@ant-design/icons";
import dayjs from 'dayjs';
import CRUDModal from "./CRUDModal";
import TableModal from "./TableModal";
import { useSearchParams } from 'react-router-dom';
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
  password_nomem
  email
  html (only in tabular view)
  modal_json_to_table (only in tabular view)
}
*/

const CRUDPage = ({ name, tableName, tableForList, tableColumns, pkColumns, userColumn, defaultOrderBy, allowedActions, versioned, datasource, isRepo, lookups, token, sequence, breadcrumbItems, removeToken, externalActions }) => {
    
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [errorDetail, setErrorDetail] = useState('');

  const [tableData, setTableData] = useState([]);
  const [showModal, setShowModal] = useState(false);

  const [showTableModal, setShowTableModal] = useState(false);
  const [tableModalData, setTableModalData] = useState([]);
  const [tableModalColumns, setTableModalColumns] = useState([]);

  const [username, setUsername] = useState("plainbi"); 

  //const [pkColumn, setPkColumn] = useState();
  const [currentPK, setCurrentPK] = useState();
  const [modalMode, setModalMode] = useState("new"); // new/edit
  const [offset, setOffset]=useState(0);
  const [limit, setLimit]=useState(20);
  const [order, setOrder]=useState("");
  const [defaultOrderInactive, setDefaultOrderInactive]=useState(false);
  const [totalCount, setTotalCount]=useState();
  const [filter, setFilter]=useState();
  const [tableParamChanged, setTableParamChanged]=useState(false);
  const [typingTimeout, setTypingTimeout]=useState(null);
  const [externalActionTimeout, setExternalActionTimeout]=useState(null);
  const [activateLookups, setActivateLookups]=useState(true);
  const [searchParams, setSearchParams] = useSearchParams();
  console.log("searchParams: " + searchParams);
  let { pk } = useParams(); // get URL parameters - here the "pk" (primary key) of a record - if provided, then immediately open edit dialog for this record
  console.log("CRUDPage - pk: " + pk);
  console.log("CRUDPage - pkColumns: " + pkColumns);
  let record_pk = (pk ? pk.toString() : null);
  let recordForPKLoaded = false;
  //console.log("CRUDPage - tableColumns: " + JSON.stringify(tableColumns));
  console.log("defaultOrderBy: " + JSON.stringify(defaultOrderBy));
  console.log("allowedActions: " + JSON.stringify(allowedActions));
  console.log("externalActions: " + JSON.stringify(externalActions));

  const navigate = useNavigate();
  const location = useLocation();
  const {pathname} = location;
  const parentpath = pathname.substring(0, pathname.lastIndexOf('/'));
  console.log("location: " + location);
  console.log("location pathname: " + pathname);
  console.log("location parent path: " + parentpath);

  let api = "/api/crud/";
  api = isRepo === 'true' ? "/api/repo/" : "/api/crud/" + (datasource ? datasource+'/' : ''); // switch between repository tables and other datasources /api/crud/<db>/<table>
  
  const [lookupData, setLookupData] = useState([]);
  const [filteredTableData, setFilteredTableData] = useState(null);

  console.log("lookups: " + lookups);
  console.log("tableForList: " + tableForList);

  function findIndexByKeyValue(arr, key, value) {
    return arr.reduce((index, obj, i) => (obj[key] == value ? i : index), -1);
  }

  useEffect(() => {
    getTableData(tableName);
    getUsername();
    // if pk was provided in URL, then retrieve record from enpoint and open edit dialog (modal) for this record
    if (record_pk && allowedActions.includes("update") && !recordForPKLoaded) {
      console.log("CRUDPage - pk provided and update allowed");
      getPKRecordOpenModal(tableName);
    }
      lookups ? getLookupDataAll() : ""; // if lookups where delivered, then get all lookup values
    //setPkColumn(pkColumns); 
  }, [tableName, tableParamChanged]);

  const getUsername = async () => {
    await Axios.get("/api/profile", {headers: {Authorization: token}}).then(
      (res) => {
        //console.log(JSON.stringify(res));
        const resData = res.data;
        console.log("/profile response: " + JSON.stringify(resData));
        setUsername(resData.username);
        console.log("setUsername: " + resData.username)
      }
    ).catch(
      function (error) {
        console.log(error);
        console.log(error.response.data.message);
      }
    );
  }

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


      // set ordering
      // from the user selection (when clicking on column header) ...
      if(order && order.length > 0) {
        console.log("queryParams - userOrderBy: " + order);
        queryParams.append("order_by", order);
        // or take the default sort from the page definition
      } else if (defaultOrderBy && defaultOrderBy.length > 0 && !defaultOrderInactive) { // defaultOrderInactive is set when user selected the column header to sort -- even if every sort is disabled by the user, the default order should not be used
          let _order = "";
          for (var i = 0; i < defaultOrderBy.length; i++) {
            _order += defaultOrderBy[i].column_name;
            try {
              if (defaultOrderBy[i].direction == "descend" || defaultOrderBy[i].direction == "desc") { // only append descend if defined - ascend is default and does not need to be set explicitly
                _order += " desc";
              }
            } catch(err) {}
            _order += ",";
          }
          _order = _order.slice(0,-1); // eliminate the last comma
          console.log("queryParams - defaultOrderBy: " + _order);
          queryParams.append("order_by", _order);
      }

      if(filter && filter.length > 0) {
        queryParams.append("q", filter);
      }
      let _searchParams = searchParams.toString().replaceAll("&", ",").replaceAll("=", ":"); // <key>=<value>&<key>:<value>&... --> <key>:<value>,<key>:<value>,...
      //console.log("searchParams: " + searchParams);
      //console.log(searchParams.toString());
      //console.log(searchParams.entries());
      //console.log(Array.from(searchParams.entries()));
      //searchParams.split("&").map((param) => { return param.replace("=", ":"); })

      if(_searchParams && _searchParams.length > 0) {
        queryParams.append("filter", _searchParams); 
      }

      let _cols = getColsParamForURL(tableColumns);
      queryParams.append("cols", _cols); 

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
          setError(true);
          if (error.response.status === 401) {
            try{removeToken();}catch(err){}
            message.error('Session ist abgelaufen');
            setErrorMessage('Es gab einen Fehler beim Laden der Daten');
            setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
          } else {
            setErrorMessage('Es gab einen Fehler beim Laden der Daten');
            setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
          }
          console.log(error);
          console.log(error.response.data.message);
        }
        )
    };


    const getPKRecordOpenModal = async (tableName) => {

      const queryParams = new URLSearchParams();
      queryParams.append("filter", pkColumns + ":" + record_pk); 
      console.log("getPKRecord queryParams: " + queryParams.toString());
      var endpoint = api+tableName+'?'+queryParams;
      console.log("getPKRecord endpoint: " + endpoint);

      await Axios.get(endpoint, {headers: {Authorization: token}}).then(
        (res) => {
          const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response                
          //let pos = findIndexByKeyValue(resData, pkColumns, record_pk); // TODO: also solution for composite key - not just single key
          //console.log("CRUDPage - pk - position in result: " + pos);
          //console.log("CRUDPage get pk record: " + JSON.stringify(resData));
          //console.log("CRUDPage get pk record length: " + resData.length);
          if(resData && resData.length > 0) {
            showEditModal(resData[0]);
            recordForPKLoaded = true;
          } else {
            setLoading(false);
            setErrorMessage('Es gab einen Fehler mit der aufgerufenen URL.');
            setErrorDetail('Ein Eintrag mit dieser ID existiert nicht: ' + record_pk);  
            setError(true)
          }
        }
        ).catch(function (error) {
          setLoading(false);
          setErrorMessage('Es gab einen Fehler beim Laden der Daten');
          setError(true);
          console.log(error);
          //console.log(error.response.data.message);
        }
        )
    };

    
  const getBlobData = async (tableName, _format) => {
    //setLoading(true);
    //setError(false);
    const dt = new Date().toISOString().substring(0,19);
    
    const queryParams = new URLSearchParams();
    if(versioned) {
      queryParams.append("v", 1);
    }
    //queryParams.append("offset", offset); // no offset - download all records
    //queryParams.append("limit", limit); // no limit - download all records
    if(order && order.length > 0) {
      queryParams.append("order_by", order);
    }
    if(filter && filter.length > 0) {
      queryParams.append("q", filter);
    }
    let _searchParams = searchParams.toString().replaceAll("&", ",").replaceAll("=", ":"); // <key>=<value>&<key>:<value>&... --> <key>:<value>,<key>:<value>,...
    if(_searchParams && _searchParams.length > 0) {
      queryParams.append("filter", _searchParams); 
    }

    let _cols = getColsParamForURL(tableColumns);
    queryParams.append("cols", _cols); 

    queryParams.append("format", _format); 

    console.log("queryParams: " + queryParams.toString());
    var endpoint = api+tableName+'?'+queryParams;

    if(tableForList && tableForList.length > 0) {
      //queryParams.append("customsql", "select * from " + tableForList);
      //queryParams.append("customsql", tableForList);
      setActivateLookups(false);
      queryParams.delete("v"); // remove versioning
      endpoint = api+tableForList+'?'+queryParams; // change tableName to tableForList
    }

    console.log("getBlobData - endpoint: " + endpoint);

    await Axios.get(endpoint, {responseType: 'blob', headers: {Authorization: token}}).then(
    //await Axios.get("/api/repo/adhoc/"+id+"/data?format="+_format, {responseType: 'blob', headers: {Authorization: token}}).then(
      (res) => {
        console.log(res.data);

        const _filename = 'export_'+tableName+"_"+dt+"."+_format.toLowerCase();
        // create file link in browser's memory
        const href = URL.createObjectURL(res.data);
    
        // create "a" HTML element with href to file & click
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', _filename); //or any other extension
        document.body.appendChild(link);
        link.click();
    
        // clean up "a" element & remove ObjectURL
        document.body.removeChild(link);
        URL.revokeObjectURL(href);

        message.success("Excel erfolgreich heruntergeladen - siehe Downloads > " + _filename)

      }
      ).catch(
        function (error) {
          //setLoading(false);
          //setError(true);
          console.log("getBlobData - error: " + error);
          console.log(error);
          console.log(error.response.data.message);
          if (error.response.status === 401) {
            try{removeToken();}catch(err){}
            message.error('Session ist abgelaufen');
            setErrorMessage('Es gab einen Fehler beim Laden der Daten');
            setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
          } else {
            setErrorMessage('Es gab einen Fehler beim Laden der Daten als ' + _format);
            setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
           }
        }
      );  
  };


    const getDsdbExport = async (_type, _id, _filename) => {
      //setLoading(true);
      //setError(false);
      //const dt = new Date().toISOString().substring(0,19);

      if (_type != 'application' && _type != 'lookup') {
        message.error("kein valider Typ für DSDB-Export: " + _type)
        return
      }
  
      const blobUri = "/api/repo/"+_type+"/"+_id+"/dsdb"; //?filenam="+_filename;
      console.log("getDsdbExport uri: " + blobUri);
  
      await Axios.get(blobUri, {responseType: 'blob', headers: {Authorization: token}}).then(
        (res) => {
          console.log(res.data);
          // create file link in browser's memory
          const href = URL.createObjectURL(res.data);
      
          // create "a" HTML element with href to file & click
          const link = document.createElement('a');
          link.href = href;
          link.setAttribute('download', _filename); 
          document.body.appendChild(link);
          link.click();
      
          // clean up "a" element & remove ObjectURL
          document.body.removeChild(link);
          URL.revokeObjectURL(href);
          
          message.success(".dsdb erfolgreich heruntergeladen - siehe Downloads > " + _filename)
  
        }
        ).catch(
          function (error) {
            //setLoading(false);
            console.log("getDsdbExport - error: " + error);
            message.error('Es gab einen Fehler beim Laden der Daten');
            //setErrorMessage('Es gab einen Fehler beim Laden der Daten');
            //setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
            //setError(true);
            //console.log(error);
            //console.log(error.response.data.message);
          }
        );  
    };
  
    const downloadDsdb = (record, e) => {
      console.log("downloadDsdb - getDsdbExport for " + tableName + " " + record.id + " " + record.alias+'.dsdb');
      getDsdbExport(tableName, record.id, record.alias.toLowerCase()+'.dsdb');
    }
    

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

    const queryParams = new URLSearchParams();
    
    if(versioned) {
      queryParams.append("v", 1);
    }

    queryParams.append("pk", getPKParamForURL(pkColumns));
    
    if(userColumn) {
      queryParams.append("usercol", userColumn);
    }

    console.log("queryParams: " + queryParams.toString());
    var endpoint = api+tableName+'/' + pk + '?'+queryParams;

    console.log("removeTableRow: endPoint: " + endpoint);
    await Axios.delete(endpoint
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
        setErrorMessage('Es gab einen Fehler beim Löschen');
        try{setErrorDetail(error.toString());}catch(err){}
        setError(true);
        console.log(error);
      }
      )
  };

  // ToBinary for Latin1, etc. characters
  const ToBinary = (str) => {
      let result="";
      str=encodeURIComponent(str);
      for(let i=0;i<str.length;i++)
          if(str[i]=="%")
          {
              result+=String.fromCharCode(parseInt(str.substring(i+1,i+3),16));
              i+=2;
          }
          else
              result+=str[i];
      return result;
  }

  // base64 encoded for "crud" endpoint, not for "repo" endpoint
  const base64UrlSafeEncode = (input) => {
    if(isRepo === 'true') {
      return input;
    } 
    let base64=btoa(ToBinary(input)); 
    return "[base64@" + base64.replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'') + "]";
  }    

  const getPKForURL = (record, _pkColumn) => {
    var pkforurl = "";
    if (_pkColumn.length <= 1) {
      console.log("only 1 pk");
      // if only 1 pk take it directly
      //pkforurl = record[_pkColumn[0]];
      pkforurl = base64UrlSafeEncode(record[_pkColumn[0]]); 
    } else {
      console.log("composite pk");
      // if composite key, then build url-specific pk string "(key=value:key=value:...)"
      pkforurl = "(";
      for (var i = 0; i < _pkColumn.length; i++) {
        //pkforurl += _pkColumn[i] + ":" + record[_pkColumn[i]];
        pkforurl += _pkColumn[i] + ":" + base64UrlSafeEncode(record[_pkColumn[i]]) ; 
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
      //pkforurl =  base64UrlSafeEncode(_pkColumn[0]); 
    } else {
      console.log("composite pk");
      // if composite key, then build url-specific pk string "&pk=key1,key2,..."
      for (var i = 0; i < _pkColumn.length; i++) {
        pkforurl += _pkColumn[i];
        //pkforurl += base64UrlSafeEncode(_pkColumn[i]); 
        pkforurl += ",";
      }
      pkforurl = pkforurl.replace(/^,+|,+$/g, ''); // trim "," at beginning and end of string
    }
    console.log("getPKParamForURL: " + pkforurl);
    return pkforurl;
  }

  const pkExists = (value) => {
    for (var i = 0; i < pkColumns.length; i++) {
      if (pkColumns[i].toLowerCase() === value.toLowerCase() ) {
        return true;
      }
    }
    return false;
  }

  const getColsParamForURL = (_cols) => {
    var colsforurl = "";
    if (_cols.length <= 1) {
      console.log("only 1 column");
      // if only 1 column take it directly
      colsforurl = _cols[0].column_name;
    } else {
      console.log("several columns");
      // if several columns, then build url-specific string "&cols=<column_name1>,<column_name2>,..."
      for (var i = 0; i < _cols.length; i++) {
        // ignore columns with "showdetailsonly", but not the ones that are part of the primary key
        if (_cols[i].showdetailsonly == 'true' && !pkExists(_cols[i].column_name)) {
          // do nothing
          console.log("getColsParamForURL - not PK and showdetailsonly: " + _cols[i].showdetailsonly + " - ignore column: " + _cols[i].column_name);
        } else {
          colsforurl += _cols[i].column_name;
          colsforurl += ",";
        }
      }
      colsforurl = colsforurl.replace(/^,+|,+$/g, ''); // trim "," at beginning and end of string
    }
    console.log("getColsParamForURL: " + colsforurl);
    return colsforurl;
  }

    // deleteConfirm
    const deleteConfirm = (record) => {
      console.log("deleteConfirm for table: " + tableName);
      console.log(record);
      //pkColumns ? console.log(record[pkColumns[0]]) : console.log("no pk");
      //removeTableRow(tableName, record, record[pkColumns[0]]);
      removeTableRow(tableName, record, getPKForURL(record, pkColumns));
    };

    // if PK for a record was set in URL, then navigate to parent URL path on close (so it gets rid of the delivered PK)
    const handelPkModalNavigation = () => {
      if (record_pk && allowedActions.includes("update")) {
        console.log("Modal closing and navigating to parentpah (because PK was provided for direct editing).");
        navigate(parentpath);
      }
    }

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
    const showDuplicateModal = (record) => { // same as create modal, but gets values of selected row and prefills the form with it
      console.log("showDuplicateModal for table: " + tableName);
      console.log(record);
      pkColumns ? console.log(record[pkColumns[0]]) : console.log("no pk");
      //setCurrentPK(record[pkColumns[0]]);
      setCurrentPK(getPKForURL(record, pkColumns));
      setModalMode("duplicate");
      setShowModal(true);
    };
    // closeModal
    const closeModal = () => {
      setShowModal(false);
      handelPkModalNavigation();
    };
    // closeAndRefreshModal
    const closeAndRefreshModal = () => {
      setShowModal(false);
      handelPkModalNavigation();
      getTableData(tableName);
    };

    // return a item to be rendered in a Menu component
    function getTableColumnDefinition(title, dataIndex, key) {
      return {
        title,
        dataIndex,
        key
      };
    }

    const openTableModal = (tableName, jsonData) => {
      console.log("openTableModal - tableName: " + tableName);
      console.log("openTableModal - jsonData: " + jsonData);
      try {
        // JSON as Text converted to Javascript Object
        let parsedJsonData = JSON.parse(jsonData);
        setTableModalData(parsedJsonData);
        // extract columns
        let parsedJsonDataColumns = Object.keys(parsedJsonData[0]).map((columnName) => { 
          return getTableColumnDefinition(columnName,columnName,columnName); 
        })
        setTableModalColumns(parsedJsonDataColumns);
        setShowTableModal(true);
      } catch(er) {
        setTableModalData([]);
        setTableModalColumns([]);
        console.log("openTableModal - JSON.parse(jsonData) - error: " + er);
        message.error("Fehler beim Anzeigen der Daten");
      }
    };
    const closeTableModal = () => {
      setTableModalData([]);
      setTableModalColumns([]);
      setShowTableModal(false);
    }; 

    
  /*  
  const tableModalData = [
    {
      key: '1',
      name: 'Mike',
      age: 32,
      address: '10 Downing Street',
    },
    {
      key: '2',
      name: 'John',
      age: 42,
      address: '10 Downing Street',
    },
  ];

  const tableModalColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Age',
      dataIndex: 'age',
      key: 'age',
    },
    {
      title: 'Address',
      dataIndex: 'address',
      key: 'address',
    },
  ];
  */

    // add action buttons to a table record
   function getColumnAction( deleteAllowed, updateAllowed, duplicateAllowed, exportdsdbAllowed) {
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
          <Link title="Editieren" onClick={(e) => { showEditModal(record, e); }}>
            <EditOutlined style={{ fontSize: "18px" }} />
          </Link>
          }
          {duplicateAllowed && pkColumns &&
          <Link title="Duplizieren" onClick={(e) => { showDuplicateModal(record, e); }}>
            <CopyOutlined style={{ fontSize: "18px" }} />
          </Link>
          }
          {exportdsdbAllowed && pkColumns &&
          <Link title="als .dsdb exportieren" onClick={(e) => { downloadDsdb(record, e); }}>
            <DownloadOutlined style={{ fontSize: "18px" }} />
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
  ).catch(function (error) {
    setLoading(false);
    setError(true);
    if (error.response.status === 401) {
      try{removeToken();}catch(err){}
      message.error('Session ist abgelaufen');
    } else {
      setErrorMessage('Es gab einen Fehler beim Laden der Daten');
      setErrorDetail((typeof error.response.data.message !== 'undefined' && error.response.data.message ? error.response.data.message : "") + (typeof error.response.data.detail !== 'undefined' && error.response.data.detail ? ": " + error.response.data.detail : ""));
    }
    console.log(error);
    console.log(error.response.data.message);
  }
  );

  const getLookupDataAll = () => {
    try {
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
    } catch(error) {
      console.log("error in getLookupDataAll");
      console.log(error);
      message.error('Es gab einen Fehler beim Laden der Lookup Werte.');
    }
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
  function getColumn(column_label, column_name, datatype, ui) {
    return {
      //title: column_label
      title: ({ sortColumns, sortColumn, sortOrder }) => {
        console.log("getColumn - sortColumns: " + JSON.stringify(sortColumns));
        console.log("getColumn - defaultOrderBy: " + JSON.stringify(defaultOrderBy));
        //console.log("getColumn(column_label, column_name, datatype, ui): " + column_label + " / " + column_name + " / " + datatype + " / " + ui);
        //console.log("getColumn - sortColumn: " + JSON.stringify(sortColumn) + " - sortOrder: " + sortOrder);
        const sortedColumn = sortColumns?.find(({ column }) => column.key === column_name);
        const defaultSortedColumn = defaultOrderBy?.find(( column ) => column.column_name === column_name);

        let _isSorted = false;
        let _sortDirection = "";

        if(sortedColumn) { 
          setDefaultOrderInactive(true); 
          _isSorted = true;
          _sortDirection = sortedColumn.order;
        } else if (defaultSortedColumn && !defaultOrderInactive){
          _isSorted = true;
          _sortDirection = defaultSortedColumn.direction ? defaultSortedColumn.direction : "ascend";          
        }
        console.log("getColumn - _isSorted: " + _isSorted + " - _sortDirection: " + _sortDirection);

        return (
          <div class="th-div-custom">
            <span class="th-div-custom-title">{column_label}</span>
            <span>{_isSorted ? (
              (_sortDirection === "ascend" || _sortDirection === "asc") ? (
                <CaretUpFilled style={{fontSize: '14px'}}/>
              ) : (
                (_sortDirection === "descend" || _sortDirection === "desc") ? (
                  <CaretDownFilled style={{fontSize: '14px'}}/>
                ) :  <CaretUpFilled className="inactive" style={{fontSize: '14px'}} />
              )
            ) : <CaretUpFilled className="inactive" style={{fontSize: '14px'}} />}
            </span>
          </div>
        )
      },
      //defaultSortOrder: null, // not setting default sort direction here, because it triggers a refresh and does not allow to reckon the sequence of the columns to be sorted // "ascend" or "descend"
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
        <Tooltip placement="topLeft" title={(ui === "html" && text) ? '' : ( (ui === "modal_json_to_table" && text) ? '' : text ) }> 
          {
            (datatype === "datetime" && text) ? 
              dayjs(text).format("YYYY-MM-DD HH:mm:ss") : 
              (
                (ui === "html" && text) ? 
                  <div dangerouslySetInnerHTML={{__html: text}} /> : 
                  (
                    (ui === "modal_json_to_table" && text) ? 
                      <Button
                      onClick={(e) => { openTableModal(tableName, text); }}
                      size="small"
                      key="1"
                      >
                        ...
                      </Button> : 
                      text
                  )
              )
          }  
        </Tooltip>
      )
      , key: column_name
      , width: 100
    };
  }
  //{(datatype === "datetime" && text) ? dayjs(text,'YYYY-MM-DD HH:mm') : text} 
  // e.g. Tue, 05 Dec 2023 14:28:48 GMT -- .replace(' GMT', ''),'ddd, D MMM YYYY hh:mm:ss'

    // return a column to be used as metadata for a Table component
    // this is from the type "lookup"
    const getLookupColumn = (column_label, column_name, lookupid) => {
      return {
        //title: column_label
      title: ({ sortColumns }) => {
        console.log("getLookupColumn - sortColumns: " + JSON.stringify(sortColumns));
        console.log("getLookupColumn - defaultOrderBy: " + JSON.stringify(defaultOrderBy));
        //console.log("getColumn(column_label, column_name, datatype, ui): " + column_label + " / " + column_name + " / " + datatype + " / " + ui);
        //console.log("getColumn - sortColumn: " + JSON.stringify(sortColumn) + " - sortOrder: " + sortOrder);
        const sortedColumn = sortColumns?.find(({ column }) => column.key === column_name);
        const defaultSortedColumn = defaultOrderBy?.find(( column ) => column.column_name === column_name);

        let _isSorted = false;
        let _sortDirection = "";

        if(sortedColumn) { 
          setDefaultOrderInactive(true); 
          _isSorted = true;
          _sortDirection = sortedColumn.order;
        } else if (defaultSortedColumn && !defaultOrderInactive){
          _isSorted = true;
          _sortDirection = defaultSortedColumn.direction ? defaultSortedColumn.direction : "ascend";          
        }
        console.log("getLookupColumn - _isSorted: " + _isSorted + " - _sortDirection: " + _sortDirection);

        return (
          <div class="th-div-custom">
            <span class="th-div-custom-title">{column_label}</span>
            <span>{_isSorted ? (
              _sortDirection === "ascend" ? (
                <CaretUpFilled style={{fontSize: '14px'}}/>
              ) : (
                _sortDirection === "descend" ? (
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

    const callStoredProcedure = (id, wait_repeat_in_ms = 1000, name, body) => {
      console.log("callStoredProcedure with id: " + id);
      if(externalActionTimeout) {
        message.info("Sie müssen " + wait_repeat_in_ms / 1000 + " Sekunden warten, bevor die Aktion wiederholt werden darf.")
        console.log("external action already called ... waiting for timeout to allow repeat"); // do nothing // clearTimeout(externalActionTimeout);
      } else {
        console.log("calling external action");
        message.info("Aktion wird ausgelöst")

        // replace placeholders in body - ${username}
        body = body.replaceAll('${username}', username);
        console.log("replaced body ${username} with " + username);

        const url = '/api/exec/' + (datasource ? datasource+'/' : '') + name;
        console.log("callStoredProcedure with url: " + url);

        Axios.defaults.headers.post['Content-Type'] ='application/json;charset=utf-8';
        Axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
        //header.Add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        Axios.post(url, body, {headers: {Authorization: token}}).then(   // await // 
            (res) => {
              console.log(JSON.stringify(res));
              const resData = (res.data.error === undefined ? res : res.data); 
              console.log(JSON.stringify(resData));
              if (resData.error) { // response might be "200 OK", but still check for error in response body
                message.error(JSON.stringify(resData.error));
              } else {
                message.success('Erfolgreich ausgelöst.');
              }
            }
          ).catch(function (error) {
            message.error('Es gab einen Fehler beim Auslösen der Aktion');
            console.log(error);
          }
          )

        setExternalActionTimeout( 
          setTimeout(() => {
            console.log("timeout over")
            setExternalActionTimeout(null)
            clearTimeout(externalActionTimeout)
          }, wait_repeat_in_ms)
        );
        console.log("timeout for repeat set to " + wait_repeat_in_ms + " ms");
      }
    }

    const callRestAPI = (id, wait_repeat_in_ms = 1000, url, body) => {
      console.log("callRestAPI with id: " + id);
      if(externalActionTimeout) {
        message.info("Sie müssen " + wait_repeat_in_ms / 1000 + " Sekunden warten, bevor die Aktion wiederholt werden darf.")
        console.log("external action already called ... waiting for timeout to allow repeat"); // do nothing // clearTimeout(externalActionTimeout);
      } else {
        console.log("calling external action");
        message.info("Aktion wird ausgelöst")

        // todo: check method and switch between them. only allowed: get, post ?
        // todo: check for contenttype

        // replace placeholders in body - ${username}
        body = body.replaceAll('${username}', username);
        console.log("replaced body ${username} with " + username);

        Axios.defaults.headers.post['Content-Type'] ='application/json;charset=utf-8';
        Axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
        //header.Add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        Axios.post(url, body).then(   // await // , {headers: {Authorization: token}}
            (res) => {
              console.log(JSON.stringify(res));
              const resData = (res.data.error === undefined ? res : res.data); 
              console.log(JSON.stringify(resData));
              if (resData.error) { // response might be "200 OK", but still check for error in response body
                message.error(JSON.stringify(resData.error));
              } else {
                message.success('Erfolgreich ausgelöst.');
              }
            }
          ).catch(function (error) {
            message.error('Es gab einen Fehler beim Auslösen der Aktion');
            console.log(error);
          }
          )

        setExternalActionTimeout( 
          setTimeout(() => {
            console.log("timeout over")
            setExternalActionTimeout(null)
            clearTimeout(externalActionTimeout)
          }, wait_repeat_in_ms)
        );
        console.log("timeout for repeat set to " + wait_repeat_in_ms + " ms");
      }
    }

      
    const downloadData = (format) => {
      getBlobData(tableName, format);
    }
    ;

    return (
      <React.Fragment>
      <PageHeader
              //onBack={() => window.history.back()}
              title=""
              subTitle=""
              extra={[
                  
                allowedActions.includes("export_excel") && 
                <Button icon={<DownloadOutlined />} onClick={() => downloadData("XLSX")}> 
                  Excel
                </Button>
                , 
                externalActions && externalActions.map((externalAction) => {
                  return ( externalAction.type === 'call_rest_api' && (externalAction.position === 'summary' || !externalAction.position) ?
                    <Tooltip title={externalAction.tooltip ? externalAction.tooltip : ''}>
                      <Button onClick={(e) => {callRestAPI(externalAction.id, externalAction.wait_repeat_in_ms, externalAction.url, externalAction.body)}}>
                        {externalAction.label}
                      </Button>
                    </Tooltip>
                    : null
                  ) 
                })
                , 
                externalActions && externalActions.map((externalAction) => {
                  return ( externalAction.type === 'call_stored_procedure' && (externalAction.position === 'detail' || !externalAction.position) ?
                    <Tooltip title={externalAction.tooltip ? externalAction.tooltip : ''}>
                      <Button onClick={(e) => {callStoredProcedure(externalAction.id, externalAction.wait_repeat_in_ms, externalAction.name, externalAction.body)}}>
                        {externalAction.label}
                      </Button>
                    </Tooltip>
                    : null
                  ) 
                })
                ,
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
                    <Space direction="vertical">
                      {breadcrumbItems ? <Breadcrumb items={breadcrumbItems} /> : ''}
                      <Input.Search
                        placeholder="Suche ..."
                        //enterButton
                        onSearch={(value) => {searchData(value)}}
                        onChange={(e) => {searchDataWithTimeout(e.target.value)}}
                        style={{marginBottom:20,width:500}}
                        allowClear 
                      />
                    </Space>
                    
                    {error && 
                    (
                      <Alert
                        message={errorMessage}
                        description={errorDetail}
                        type="error"
                        showIcon
                      />
                    )}
                    {!error && (
                    <Table
                          size="small"
                          columns={tableColumns && tableColumns.filter((column) => !column.showdetailsonly) // show all columns, that are not limited to the detail view (modal) ...
                            .map((column) => {
                              return ((column.ui === "lookup" && activateLookups) ? getLookupColumn(column.column_label, column.column_name, column.lookup) : getColumn(column.column_label, column.column_name, column.datatype, column.ui));
                            })
                            .concat((allowedActions.includes("delete") || allowedActions.includes("update") || allowedActions.includes("duplicate")  || allowedActions.includes("export_dsdb")) ? getColumnAction(allowedActions.includes("delete"), allowedActions.includes("update"), allowedActions.includes("duplicate"), allowedActions.includes("export_dsdb")) : [])
                          } // .. also add action buttons (delete, edit), if allowed

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
                     )}
                    </React.Fragment>
                  ) 
                }
            
            {showModal &&
            <CRUDModal tableColumns={tableColumns} handleCancel={closeModal} handleSave={closeAndRefreshModal} type={modalMode} tableName={tableName} pk={currentPK} pkColumns={pkColumns} userColumn={userColumn} versioned={versioned} datasource={datasource} isRepo={isRepo} token={token} sequence={sequence}/>
            }
            {showTableModal &&
            <TableModal modalName="" tableColumns={tableModalColumns} tableData={tableModalData} handleClose={closeTableModal}/>
            }

            </React.Fragment>
    );

};

export default CRUDPage;

