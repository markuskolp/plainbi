import React from "react";
import { useState } from "react";
import {
  Button,
  Modal,
  Table,
  message
} from "antd";

const TableModal = ({ modalName, tableColumns, tableData, handleClose }) => {
    
  const [totalCount, setTotalCount]=useState(tableData.length);

  console.log("modalName: ", modalName);
  console.log("tableColumns: ", tableColumns);
  console.log("tableData: ", tableData);

  /*
  const [isModalOpen, setIsModalOpen] = useState(false);
  const showModal = () => {
    setIsModalOpen(true);
  };
  const handleOk = () => {
    setIsModalOpen(false);
  };
  const handleCancel = () => {
    setIsModalOpen(false);
  };
  */
  
  return (
    <React.Fragment>
      <Modal
            title={modalName}
            open={true} // isModalOpen
            //onOk={handleClose} // handleOk
            onCancel={handleClose} // handleCancel
            centered
            width="80vw"
            maskClosable={false}
            style={{
              maxWidth:"1500px"
            }}
            footer={[]} // no buttons
      >
        <Table 
          size="small" 
          columns={tableColumns} 
          dataSource={tableData} 
          tableLayout="auto"
          pagination={{ defaultPageSize: 20, total: totalCount, hideOnSinglePage: true, showTotal: (total) => `Gesamt: ${total}` }}
        />
      </Modal>
    </React.Fragment>
  );

};

export default TableModal;
