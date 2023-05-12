import React from 'react';
import { Table as AntTable } from 'antd';

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