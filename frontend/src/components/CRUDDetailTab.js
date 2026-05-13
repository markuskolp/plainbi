import React, { useState, useEffect } from "react";
import { Button, Space, Popconfirm, message } from "antd";
import { EditOutlined, DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import Table from "./Table";
import CRUDModal from "./CRUDModal";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData, isTrue } from "../utils/dataUtils";
import { getPKForURL, getPKParamForURL, getColsParamForURL } from "../utils/pkUtils";

const CRUDDetailTab = ({ pageConfig, fkColumn, fkValue, staticValues = {}, token, datasource, isRepo }) => {
  const { loading, setLoading, setApiError } = useApiState(false);
  const [tableData, setTableData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState("new");
  const [currentPK, setCurrentPK] = useState(null);

  const {
    table, table_for_list, table_columns, pk_columns,
    allowed_actions, versioned, user_column, sequence
  } = pageConfig;

  const pkColumns = pk_columns || [];
  const allowedActions = allowed_actions || [];
  const api = isTrue(isRepo) ? "/api/repo/" : "/api/crud/" + (datasource ? datasource + '/' : '');

  // Force FK column and static_values columns to non-editable in the detail form
  const tableColumnsForForm = (table_columns || []).map(col =>
    (col.column_name === fkColumn || col.column_name in staticValues)
      ? { ...col, editable: false }
      : col
  );

  useEffect(() => {
    if (fkValue !== null && fkValue !== undefined) loadData();
  }, [fkValue]);

  const loadData = () => {
    setLoading(true);
    const queryParams = new URLSearchParams();
    const staticParts = Object.entries(staticValues).map(([k, v]) => `${k}:${v}`).join(",");
    const filterVal = [fkColumn + ":" + fkValue, staticParts].filter(Boolean).join(",");
    queryParams.append("filter", filterVal);
    queryParams.append("cols", getColsParamForURL(table_columns || [], pkColumns));
    if (versioned) queryParams.append("v", 1);
    const tbl = table_for_list || table;
    apiClient.get(api + tbl + '?' + queryParams)
      .then((res) => { setTableData(extractResponseData(res) || []); setLoading(false); })
      .catch((err) => setApiError('Fehler beim Laden', err));
  };

  const deleteRow = (record) => {
    const queryParams = new URLSearchParams();
    queryParams.append("pk", getPKParamForURL(pkColumns));
    apiClient.delete(api + table + '/' + getPKForURL(record, pkColumns, isRepo) + '?' + queryParams)
      .then(() => { message.success('Erfolgreich gelöscht.'); loadData(); })
      .catch((err) => setApiError('Fehler beim Löschen', err));
  };

  const columns = (table_columns || [])
    .filter(col => !col.showdetailsonly)
    .map(col => ({
      title: col.column_label,
      dataIndex: col.column_name,
      key: col.column_name,
      ellipsis: true,
      width: 150
    }))
    .concat([{
      title: " ", key: "action", width: 80, fixed: "right",
      render: (_, record) => (
        <Space>
          {allowedActions.includes("delete") && pkColumns.length > 0 &&
            <Popconfirm title="Löschen?" onConfirm={() => deleteRow(record)} okText="Ja" cancelText="Nein">
              <DeleteOutlined style={{ fontSize: 16, cursor: 'pointer' }} />
            </Popconfirm>}
          {allowedActions.includes("update") && pkColumns.length > 0 &&
            <EditOutlined style={{ fontSize: 16, cursor: 'pointer' }}
              onClick={() => { setCurrentPK(getPKForURL(record, pkColumns, isRepo)); setModalMode("edit"); setShowModal(true); }} />}
        </Space>
      )
    }]);

  return (
    <div style={{ paddingTop: 8 }}>
      {allowedActions.includes("create") &&
        <Button size="small" icon={<PlusOutlined />} style={{ marginBottom: 12 }}
          onClick={() => { setCurrentPK(null); setModalMode("new"); setShowModal(true); }}>
          Neu
        </Button>}
      <Table
        size="small"
        columns={columns}
        dataSource={tableData}
        loading={loading}
        pagination={{ defaultPageSize: 10, hideOnSinglePage: true, showTotal: (total) => `Gesamt: ${total}` }}
        scroll={{ x: 'max-content', y: 300 }}
      />
      {showModal &&
        <CRUDModal
          tableColumns={tableColumnsForForm}
          handleCancel={() => setShowModal(false)}
          handleSave={() => { setShowModal(false); loadData(); }}
          type={modalMode}
          tableName={table}
          pk={currentPK}
          pkColumns={pkColumns}
          userColumn={user_column}
          versioned={versioned}
          datasource={datasource}
          isRepo={isRepo}
          token={token}
          sequence={sequence}
          prefillValues={modalMode === 'new' ? { [fkColumn]: fkValue, ...staticValues } : undefined}
        />}
    </div>
  );
};

export default CRUDDetailTab;
