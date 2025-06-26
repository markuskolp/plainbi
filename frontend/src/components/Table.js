import React from 'react';
import { Table as AntTable } from 'antd';
import { Resizable } from "react-resizable";
import ReactDragListView from "react-drag-listview";
// https://codesandbox.io/p/sandbox/table-column-sortable-resizable-st9bt?file=%2Findex.js%3A9%2C7-9%2C21

const Table = props => {
  const {
    columns,
    ...otherTableProps
  } = props;

  const sortableColumns = columns.map(column => {
    const { sorter, dataIndex, ...otherColumnProps } = column;

    if (sorter) {
      const { compare, ...otherSorterProps } = sorter;

      return {
        ...otherColumnProps,
        dataIndex,
        sorter: {
          compare: (rowA, rowB) => compare(rowA[dataIndex], rowB[dataIndex]),
          ...otherSorterProps,
        }
      };
    }

    return column;
  });

  return (
    <AntTable
      columns={sortableColumns}
      {...otherTableProps}
    />
  );
};

export default Table;