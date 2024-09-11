import React from "react";
import { useState } from "react";
import {
  Button,
  Modal,
  Table,
  message
} from "antd";

const TableModal = ({ modalName, tableColumns, tableData, handleClose }) => {
    
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
            style={{
              maxWidth:"1500px"
            }}
            footer={[]} // no buttons
      >
        <Table 
          size="small" 
          columns={tableColumns} 
          dataSource={tableData} 
        />
      </Modal>
    </React.Fragment>
  );

};

export default TableModal;

/*


const tableData = [
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

const tableColumns = [
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