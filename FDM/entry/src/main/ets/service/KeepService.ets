import RecordPO from '../bean/RecordPO'
import RecordItemModel from '../model/RecordItemModel'
import RecordModel from '../model/RecordModel'
import DateUtil from '../utils/DateUtil'
import Logger from '../utils/Logger'
import RecordVO from '../viewmodel/RecordVO'
import { DetectionResult } from '../viewmodel/resultViemModel'


class KeepService {
  /*
  增
   */
  insert(detectId: number, detectionResult: DetectionResult, imageUri: string): Promise<number> {
    let createTime = (AppStorage.Get('selectedDate') || DateUtil.beginTimeOfDay(new Date())) as number
    let detectionResultJson = JSON.stringify(detectionResult)
    Logger.debug('detectionResult 长度：' + detectionResultJson.length)
    Logger.debug('imageUri 长度：' + imageUri.length)
    let record: RecordPO = {
      detectId: detectId,
      createTime: createTime,
      detectionResult: detectionResultJson,
      imageUri: imageUri
    };
    Logger.debug('准备插入的数据对象：' + JSON.stringify(record));
    return RecordModel.insert(record)
  }

  /*
  删
   */
  deleteById(id: number): Promise<number> {
    return RecordModel.delete(id)
  }

  /*
  改
   */
  update(record: RecordVO): Promise<number> {
    return RecordModel.update({
      id: record.id,
      detectId: record.detectId,
      createTime: record.createTime,
      // detectionResult: record.detectionResult,
      // imageUri: record.imageUri
    }, record.id)
  }

  /*
  查所有
   */
  async selectAllRecord(): Promise<RecordVO[]> {
    let rps = await RecordModel.queryAll()
    return Promise.all(rps.map(async rp => {
      if (rp.createTime === undefined) {
        throw new Error("createTime is undefined");
      }
      // 通过ID查询RecordItem对象
      let recordItem = await RecordItemModel.getById(rp.detectId);
      // 使用RecordVO的构造函数创建RecordVO实例
      let rv = new RecordVO(rp.id, rp.detectId, rp.createTime, recordItem);
      return rv;
    }));
  }

  /*
  根据日期查询
   */
  async selectRecordByDate(date: number): Promise<RecordVO[]> {
    let rps = await RecordModel.queryByDate(date)
    return Promise.all(rps.map(async rp => {
      // 通过ID查询RecordItem对象
      if (rp.createTime === undefined) {
        throw new Error("createTime is undefined");
      }
      // 通过ID查询RecordItem对象
      let recordItem = await RecordItemModel.getById(rp.detectId);
      // 使用RecordVO的构造函数创建RecordVO实例
      let rv = new RecordVO(rp.id, rp.detectId, rp.createTime, recordItem, rp.detectionResult, rp.imageUri);

      return rv;
    }));
  }
}

let keepService = new KeepService();

export default keepService as KeepService;