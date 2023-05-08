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
const { Link } = Typography;

//TODO: Modal for create and update
//TODO: lookupData
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

const CRUDPage = ({ name, table, tableColumns, allowedActions }) => {
    
  const [loading, setLoading] = useState(true);
  const [tableData, setTableData] = useState([]);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    getTableData(table);
  }, [table]);

  // getTableData
  const getTableData = async (tableName) => {
    
    //await Axios.get("/api/data/table/"+tableName).then(
    await Axios.get("/api/crud/"+tableName).then(
      (res) => {
        const resData = (res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data); // take data directly if exists, otherwise take "data" part in JSON response
        console.log(JSON.stringify(resData));
        setTableData(resData);
        console.log(JSON.stringify(tableData));
        setLoading(false);
      }
    );
  };

  // removeTableRow
  const removeTableRow = async (tableName, record) => {
    setLoading(true);
    await Axios.delete("/api/crud/"+tableName, {  // /${id
        headers: { 
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        data: {
          record
        }
      }).then( 
      (res) => {
        getTableData(table);
      }
      )
  };

    // deleteConfirm
    const deleteConfirm = (record) => {
      console.log("deleteConfirm for table: " + table);
      console.log(record);
      removeTableRow(table, record);
      message.success('Wurde gelöscht.');
    };

    // showModal
    const showEditModal = () => {
      setShowModal(true);
    };
    const showCreateModal = () => {
      setShowModal(true);
    };
    // closeModal
    const closeModal = () => {
      setShowModal(false);
    }
    
    // add action buttons to a table record
   function getColumnAction( deleteAllowed, updateAllowed) {
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
            onConfirm={(e) => { deleteConfirm(record, e); }}
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
                  columns={tableColumns && tableColumns.filter((column) => !column.showdetailsonly) // show all columns, that are not limited to the detail view (modal) ...
                    .map((column) => {
                      return getColumn(column.column_label, column.column_name);
                    })
                    .concat(getColumnAction(allowedActions.includes("delete"), allowedActions.includes("update")))} // .. also add action buttons (delete, edit), if allowed

                  dataSource={tableData}
                  //dataSource={pageMetadataRelevant.name.table_columns}
                  //pagination={{ pageSize: 50 }}
                  pagination={false}
                  //scroll={{ y: 500 }}
                  //scroll={{ x: 300 }}
                  loading={loading}
            /> 
            
            {showModal &&
            <CRUDModal tableColumns={tableColumns} handleClose={closeModal}/>
            }

            </React.Fragment>
    );

};

export default CRUDPage;
