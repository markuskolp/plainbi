import React, { useState, useEffect } from "react";
import { Button, Space, Popconfirm, message } from "antd";
import { EditOutlined, DeleteOutlined, PlusOutlined, CaretUpFilled, CaretDownFilled } from "@ant-design/icons";
import Table from "./Table";
import CRUDModal from "./CRUDModal";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";
import { extractResponseData, isTrue } from "../utils/dataUtils";
import { getPKForURL, getPKParamForURL, getColsParamForURL } from "../utils/pkUtils";
import { Sorter } from "../utils/sorter";

const CRUDDetailTab = ({ pageConfig, fkColumn, fkValue, staticValues = {}, token, datasource, isRepo }) => {
  const { loading, setLoading, setApiError } = useApiState(false);
  const [tableData, setTableData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [order, setOrder] = useState("");
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

  const tableColumnsForForm = (table_columns || []).map(col =>
    (col.column_name === fkColumn || col.column_name in staticValues)
      ? { ...col, editable: false }
      : col
  );

  useEffect(() => {
    if (fkValue !== null && fkValue !== undefined) loadData(1, order, pageSize);
  }, [fkValue]);

  const loadData = (page = currentPage, ord = order, ps = pageSize) => {
    setLoading(true);
    const queryParams = new URLSearchParams();
    const staticParts = Object.entries(staticValues).map(([k, v]) => `${k}:${v}`).join(",");
    const filterVal = [fkColumn + ":" + fkValue, staticParts].filter(Boolean).join(",");
    queryParams.append("filter", filterVal);
    queryParams.append("cols", getColsParamForURL(table_columns || [], pkColumns));
    queryParams.append("offset", (page - 1) * ps);
    queryParams.append("limit", ps);
    if (ord) queryParams.append("order_by", ord);
    if (versioned) queryParams.append("v", 1);
    const tbl = table_for_list || table;
    apiClient.get(api + tbl + '?' + queryParams)
      .then((res) => {
        const tc = res.data.length === 0 || res.data.length === undefined ? res.data.total_count : res.total_count;
        setTotalCount(tc || 0);
        setTableData(extractResponseData(res) || []);
        setLoading(false);
      })
      .catch((err) => setApiError('Fehler beim Laden', err));
  };

  const handleTableChange = (pagination, _filters, sorter) => {
    const page = pagination.current || 1;
    const ps = pagination.pageSize || pageSize;
    let newOrder = "";
    if (sorter.hasOwnProperty("column") && !sorter.length && sorter.order)
      newOrder = sorter.field + (sorter.order === "descend" ? " desc" : "");
    if (sorter.length > 1)
      newOrder = sorter.map((s) => s.field + (s.order === "descend" ? " desc" : "")).join(",");
    setCurrentPage(page);
    setPageSize(ps);
    setOrder(newOrder);
    loadData(page, newOrder, ps);
  };

  const deleteRow = (record) => {
    const queryParams = new URLSearchParams();
    queryParams.append("pk", getPKParamForURL(pkColumns));
    apiClient.delete(api + table + '/' + getPKForURL(record, pkColumns, isRepo) + '?' + queryParams)
      .then(() => { message.success('Erfolgreich gelöscht.'); loadData(currentPage, order, pageSize); })
      .catch((err) => setApiError('Fehler beim Löschen', err));
  };

  const renderSortIcon = (sortColumns, column_name) => {
    const sorted = sortColumns?.find((col) => col.column.dataIndex === column_name);
    if (!sorted?.order) return <CaretUpFilled className="inactive" style={{ fontSize: '14px' }} />;
    return sorted.order === "ascend"
      ? <CaretUpFilled style={{ fontSize: '14px' }} />
      : <CaretDownFilled style={{ fontSize: '14px' }} />;
  };

  const columnTitle = (label, column_name) => ({ sortColumns }) => (
    <div className="th-div-custom">
      <span className="th-div-custom-title">{label}</span>
      <span>{renderSortIcon(sortColumns, column_name)}</span>
    </div>
  );

  const columns = (table_columns || [])
    .filter(col => !col.showdetailsonly)
    .map(col => ({
      title: columnTitle(col.column_label, col.column_name),
      dataIndex: col.column_name,
      key: col.column_name,
      ellipsis: true,
      width: 150,
      sorter: { compare: Sorter.DEFAULT, multiple: 3 },
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
        onChange={handleTableChange}
        pagination={{
          current: currentPage,
          pageSize: pageSize,
          total: totalCount,
          hideOnSinglePage: true,
          showSizeChanger: true,
          showTotal: (total) => `Gesamt: ${total}`
        }}
        scroll={{ x: 'max-content', y: 300 }}
      />
      {showModal &&
        <CRUDModal
          tableColumns={tableColumnsForForm}
          handleCancel={() => setShowModal(false)}
          handleSave={() => { setShowModal(false); loadData(currentPage, order, pageSize); }}
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
