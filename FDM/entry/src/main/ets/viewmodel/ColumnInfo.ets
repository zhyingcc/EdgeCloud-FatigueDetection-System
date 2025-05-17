/*
 数据库列信息
 */
export interface ColumnInfo {
  name: string;
  columnName: string;
  type: ColumnType;
}

export enum ColumnType {
  LONG,
  DOUBLE,
  STRING,
  BLOB,
  JSON
}

