import relationalStore from '@ohos.data.relationalStore'
import common from '@ohos.app.ability.common';
import Logger from './Logger';
import { ColumnInfo, ColumnType } from '../viewmodel/ColumnInfo';
import RecordPO from '../bean/RecordPO';

const DB_FILENAME: string = 'PCBDetector.db'



class DBUtil {
  rdbStore: relationalStore.RdbStore | null = null;

  //初始化数据库
  initDB(context: common.UIAbilityContext): Promise<void> {
    let config: relationalStore.StoreConfig = {
      name: DB_FILENAME,
      //安全等级
      securityLevel: relationalStore.SecurityLevel.S1
    }
    return new Promise<void>((resolve, reject) => {
      relationalStore.getRdbStore(context, config)
        .then(rdbStore => {
          this.rdbStore = rdbStore
          Logger.debug('rdbStore 初始化完成')
          resolve()
        })
        .catch((reason: Error) => {
          Logger.debug('rdbStore 初始化异常', JSON.stringify(reason))
          reject(reason)
        })
    })
  }
  /*
  创建数据库表
   */
  createTable(createSQL: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.rdbStore) {
        this.rdbStore.executeSql(createSQL)
          .then(() => {
            Logger.debug('成功创建表', createSQL);
            resolve();
          }).catch((err: Error) => {
          Logger.error('创建表失败，' + err.message, JSON.stringify(err,Object.getOwnPropertyNames(err)));
          reject(err);
        });
      } else {
        reject(new Error("rdbStore is not initialized"));
      }
    });
  }

  insert(tableName: string, obj: RecordPO, columns: ColumnInfo[]): Promise<number> {
    return new Promise((resolve, reject) => {
      if (this.rdbStore) {
        let value = this.buildValueBucket(obj, columns);
        Logger.debug('待插入的对象参数' + JSON.stringify(value))
        this.rdbStore.insert(tableName, value, (err, id) => {
          if (err) {
            Logger.error('新增失败', JSON.stringify(err,Object.getOwnPropertyNames(err)));
            reject(err);
          } else {
            Logger.debug('新增成功，新增数据ID：' + id.toString());
            resolve(id);
          }
        });
      } else {
        reject(new Error("rdbStore is not initialized"));
      }
    });
  }
  /*
  删
   */
  delete(predicates: relationalStore.RdbPredicates): Promise<number> {
    return new Promise((resolve, reject) => {
      if (this.rdbStore) {
        this.rdbStore.delete(predicates, (err, rows) => {
          if (err) {
            Logger.error('删除失败', JSON.stringify(err));
            reject(err);
          } else {
            Logger.debug('删除成功，删除第' + rows.toString() + '行数据');
            resolve(rows);
          }
        });
      } else {
        reject(new Error("rdbStore is not initialized"));
      }
    });
  }

  /*
  查
   */
  queryForList<T>(predicates: relationalStore.RdbPredicates, columns: ColumnInfo[]): Promise<T[]> {
    return new Promise((resolve, reject) => {
      if (this.rdbStore) {
        this.rdbStore.query(predicates, columns.map(info => info.columnName), (err, result) => {
          if (err) {
            Logger.error('查询失败', JSON.stringify(err));
            reject(err);
          } else {
            Logger.debug('查询结果: ' + JSON.stringify(result));
            Logger.debug('查询成功，查询到 ' + result.rowCount.toString() + ' 行');
            resolve(this.parseResulSet(result, columns));
          }
        });
      } else {
        reject(new Error("rdbStore is not initialized"));
      }
    });
  }

  update(obj: RecordPO, columns: ColumnInfo[], predicates: relationalStore.RdbPredicates): Promise<number> {
    return new Promise((resolve, reject) => {
      if (this.rdbStore) {
        const value = this.buildValueBucket(obj, columns);
        this.rdbStore.update(value, predicates, (err, id) => {
          if (err) {
            Logger.error('修改失败', JSON.stringify(err));
            reject(err);
          } else {
            Logger.debug('修改成功，修改数据ID为：' + id);
            resolve(id);
          }
        });
      } else {
        reject(new Error("rdbStore is not initialized"));
      }
    });
  }

  /*
  处理查询方法返回的Promise类型数据
   */
  parseResulSet<T> (result: relationalStore.ResultSet, columns: ColumnInfo[]): T[] {
    let arr: RecordPO[] = []
    if(result.rowCount <= 0) {
      return arr as T[]
    }
    //循环处理结果,循环条件：当所在行不是最后一行
    while (!result.isAtLastRow) {
      //去往下一行
      result.goToNextRow()
      const obj: RecordPO = new RecordPO()
      //解析数据，转换成对象
      columns.forEach(info => {
        const columnIndex = result.getColumnIndex(info.columnName);
        const columnValue = this.getColumnValue(result, columnIndex, info.type);

        if (info.name === 'id') {
          obj.id = columnValue as number;
        } else if (info.name === 'detectId') {
          obj.detectId = columnValue as number;
        } else if (info.name === 'createTime') {
          obj.createTime = columnValue as number;
        }
        else if (info.name === 'detectionResult') {
          obj.detectionResult = columnValue as string;
        } else if (info.name === 'imageUri') {
          obj.imageUri = columnValue as string;
        }
      });
      //将对象填入结果数组
      arr.push(obj)
      Logger.debug('查询到的数据：' + JSON.stringify(obj))
    }
    return arr as T[]
  }


  getColumnValue(result: relationalStore.ResultSet, columnIndex: number, type: ColumnType): number | string | null {
    switch (type) {
      case ColumnType.LONG:
        return result.getLong(columnIndex);
      case ColumnType.DOUBLE:
        return result.getDouble(columnIndex);
      case ColumnType.STRING:
        return result.getString(columnIndex);
      default:
        return null;
    }
  }

  buildValueBucket(obj: RecordPO, columns: ColumnInfo[]): relationalStore.ValuesBucket {
    let value: relationalStore.ValuesBucket = {};
    columns.forEach(info => {
      switch (info.columnName) {
        case 'detect_id':
          value[info.columnName] = obj.detectId;
          Logger.debug('检测任务类型id已添加')
          break;
        case 'create_time':
          if (obj.createTime !== undefined) {
            value[info.columnName] = obj.createTime;
            Logger.debug('创建时间已添加')
          }
          break;
        case 'detection_result':
          if (obj.detectionResult !== undefined) {
            value[info.columnName] = obj.detectionResult;
            Logger.debug('检测结果已添加');
          }
          break;
        case 'image_uri':
          if (obj.imageUri !== undefined) {
            value[info.columnName] = obj.imageUri;
            Logger.debug('检测图片位置已添加')
          }
          break;
        default:
          Logger.warn('未知的列名：' + info.columnName);
      }
    });
    Logger.debug('新生成的 ValuesBucket：' + JSON.stringify(value));
    return value;
  }

}

let dbUtil: DBUtil = new DBUtil()
export default dbUtil as DBUtil
