import React from 'react';
import { Button, Tooltip } from 'antd';
import { PageHeader } from "@ant-design/pro-layout";
import { PlusOutlined, DownloadOutlined } from "@ant-design/icons";

const CRUDToolbar = ({ allowedActions, externalActions, onNew, onDownload, callRestAPI, callStoredProcedure }) => (
  <PageHeader
    title=""
    subTitle=""
    extra={[
      allowedActions.includes("export_excel") &&
        <Button key="excel" icon={<DownloadOutlined />} onClick={() => onDownload("XLSX")}>Excel</Button>,
      externalActions && externalActions.map((ea) => (
        ea.type === 'call_rest_api' && (ea.position === 'summary' || !ea.position) ?
          <Tooltip key={ea.id} title={ea.tooltip || ''}>
            <Button onClick={() => callRestAPI(ea.id, ea.wait_repeat_in_ms, ea.url, ea.body)}>{ea.label}</Button>
          </Tooltip> : null
      )),
      externalActions && externalActions.map((ea) => (
        ea.type === 'call_stored_procedure' && (ea.position === 'summary' || !ea.position) ?
          <Tooltip key={ea.id} title={ea.tooltip || ''}>
            <Button onClick={() => callStoredProcedure(ea.id, ea.wait_repeat_in_ms, ea.name, ea.body)}>{ea.label}</Button>
          </Tooltip> : null
      )),
      allowedActions.includes("create") &&
        <Button key="new" onClick={onNew} type="primary" icon={<PlusOutlined />}>Neu</Button>
    ]}
  />
);

export default CRUDToolbar;
