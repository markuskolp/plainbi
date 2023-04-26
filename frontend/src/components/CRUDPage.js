import React from "react";
import { useState, useEffect } from "react";
import Axios from "axios";
import {
  Table,
  Button,
  Typography,
  Layout,
  Menu,
  Modal,
  Switch,
  Form,
  Input,
  Select,
  InputNumber,
  DatePicker,
  Space,
  Popconfirm,
  message
} from "antd";
import { PageHeader } from "@ant-design/pro-layout";
import { EditOutlined, PlusOutlined, DeleteOutlined } from "@ant-design/icons";
const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Text, Link } = Typography;

//TODO: Modal for create and update
//TODO: lookupData
//"datatype": "number", //text/number/date/boolean
//            "ui": "lookup", //hidden/textinput/numberinput/datepicker/lookup/textarea/textarea_markdown/switch

const CRUDPage = ({ name, table, tableColumns, allowedActions }) => {
    
  const [loading, setLoading] = useState(true);
  const [tableData, setTableData] = useState([]);

  const layout = {
      labelCol: { span: 6 },
      wrapperCol: { span: 14 }
    };
    const layoutpage = {
      labelCol: { span: 6 },
      wrapperCol: { span: 14 }
    };
    /*
  
    const [lookupData, setLookupData] = useState([]);
    const [columnItems, setColumnItems] = useState([]);
    const [columnItemsForSummary, setColumnItemsForSummary] = useState([]);
  
    */

  useEffect(() => {
    getTableData(table);
  }, [table]);

  // getTableData
  const getTableData = async (tableName) => {
    
    await Axios.get("/api/data/table/"+tableName+".json").then(
      (res) => {
        console.log(JSON.stringify(res.data));
        setTableData(res.data);
        console.log(JSON.stringify(tableData));
        setLoading(false);
      }
    );
  };



    // deleteConfirm
    const deleteConfirm = (e) => {
      console.log(e);
      message.success('Wurde gelöscht.');
    };

    // showModal
    const showEditModal = () => {
      
    };
    const showCreateModal = () => {
      
    };
    
    // add action buttons to a table record
   function getColumnAction(deleteAllowed, updateAllowed) {
    return {
      title: " ",
      key: "action",
      width: 100,
      render: (_, record) => ([
        <Space>
          {deleteAllowed && 
            <Popconfirm
            title="Löschen"
            description="Wirklich löschen?"
            onConfirm={deleteConfirm}
            //onCancel={cancel}
            okText="Ja"
            cancelText="Nein"
            //<Link onClick={(e) => { this.onDelete(record.key, e); }}>
            >
            <DeleteOutlined style={{ fontSize: "18px" }} />
            </Popconfirm>
          }
          {updateAllowed && 
          <Link onClick={showEditModal}>
            <EditOutlined style={{ fontSize: "18px" }} />
          </Link>
          }
        </Space>
      ])
    };
  }

  // return a column to be used as metadata for a Table component
  function getColumn(column_label, column_name) {
    return {
      title: column_label,
      dataIndex: column_name,
      //key: column_name
      //width: 50,
      //render
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
                <Table
                  size="small"
                  columns={tableColumns.filter((column) => !column.showdetailsonly) // show all columns, that are not limited to the detail view (modal) ...
                    .map((column) => {
                      return getColumn(column.column_label, column.column_name);
                    })
                    .concat(getColumnAction(allowedActions.includes("delete"), allowedActions.includes("update")))} // .. also add action buttons (delete, edit), if allowed

                  dataSource={tableData}
                  //dataSource={pageMetadataRelevant.name.table_columns}
                  //pagination={{ pageSize: 50 }}
                  pagination={false}
                  //scroll={{ y: 500 }}
                  loading={loading}
            /> 
            
            </React.Fragment>
    );

};

export default CRUDPage;
