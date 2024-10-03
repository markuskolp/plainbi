import React, { CSSProperties, useState, useEffect } from 'react';
import { Button, Modal, Spin, Alert} from 'antd';
import { useCubeQuery } from '@cubejs-client/react';

import { TableQueryRenderer } from './TableQueryRenderer';

const modalStyle = {
  top: 50,
  minWidth: 450,
};

export function DrilldownModal({ query, open, onClose, pivotConfig }) {
  const [isOpen, setIsOpen] = useState(true);
  const { resultSet, isLoading, error } = useCubeQuery(query, {
    skip: !query,
  });

  useEffect(() => {
    setIsOpen(open);
  }, [open]);

  const handleCancel = () => {
    setIsOpen(false);
  };

  return (
    <Modal
      open={isOpen}
      onCancel={handleCancel}
      afterClose={onClose}
      centered
      width="80vw"
      maskClosable={false}
      //style={modalStyle}
      style={{
        maxWidth:"1500px"
      }}
      footer={null}
    >
      {error ? <Alert
        message="Fehler"
        description={error.toString()}
        type="error"
      /> : null}
      {isLoading && !error ? <Spin /> : null}
      {resultSet && !isLoading ? (
        <TableQueryRenderer resultSet={resultSet} pivotConfig={pivotConfig} />
      ) : null}
    </Modal>
  );
}