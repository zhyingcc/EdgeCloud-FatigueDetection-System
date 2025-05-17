import RecordPO from '../bean/RecordPO';
import DBUtil from '../utils/DBUtil';
import { ColumnInfo, ColumnType } from '../viewmodel/ColumnInfo';
import relationalStore from '@ohos.data.relationalStore';
import Logger from '../utils/Logger'
const CREATE_TABLE_SQL: string = `
CREATE TABLE IF NOT EXISTS record
(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  detect_id INTEGER NOT NULL,
  create_time INTEGER NOT NULL,
  detection_result TEXT,
  image_uri TEXT
)`


/*
数据库列信息
 */
const COLUMNS: ColumnInfo[] = [
  { name: 'id', columnName: 'id', type: ColumnType.LONG },
  { name: 'detectId', columnName: 'detect_id', type: ColumnType.LONG },
  { name: 'createTime', columnName: 'create_time', type: ColumnType.LONG },
  { name: 'detectionResult', columnName: 'detection_result', type: ColumnType.STRING },
  { name: 'imageUri', columnName: 'image_uri', type: ColumnType.STRING }
]

/*
表明，ID列名，时间列名 常量
 */
const TABLE_NAME = 'record';
const ID_COLUMN = 'id';
const DATE_COLUMN = 'create_time';

class RecordModel {

  getCreateTableSql(): string {
    return CREATE_TABLE_SQL
  }

  /*
  增
   */
  insert (record: RecordPO)  {
    Logger.debug('准备插入数据' + JSON.stringify(record))
    let result = DBUtil.insert(TABLE_NAME, record, COLUMNS)
    Logger.debug('插入结果：' + JSON.stringify(result))
    return result
  }

  /*
  删
   */
  delete (id: number) {
    let predicates = new relationalStore.RdbPredicates(TABLE_NAME)
    predicates.equalTo(ID_COLUMN, id)
    return DBUtil.delete(predicates)
  }

  /*
  改
   */
  update(record: RecordPO, id: number) {
    let predicates = new relationalStore.RdbPredicates(TABLE_NAME)
    predicates.equalTo(ID_COLUMN, id)

    return DBUtil.update(record, COLUMNS, predicates)
  }

  /*
  查所有
   */
  queryAll(): Promise<RecordPO[]> {
    let predicates = new relationalStore.RdbPredicates(TABLE_NAME)

    return DBUtil.queryForList(predicates, COLUMNS)
  }

  /*
  根据日期查
   */
  queryByDate(date: number): Promise<RecordPO[]> {
    let predicates = new relationalStore.RdbPredicates(TABLE_NAME)
    predicates.equalTo(DATE_COLUMN, date)

    return DBUtil.queryForList(predicates, COLUMNS)
  }
}

let recordModel = new RecordModel();
export default recordModel as RecordModel