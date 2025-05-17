// import RecordItemModel from '../model/RecordItemModel';
// import RecordItem from '../bean/RecordItem';
// import { DetectionResult } from './resultViemModel';
//
// export default class RecordVO {
//   //记录ID
//   id: number;
//   //检测任务ID
//   detectId: number;
//   //检测任务创建日期
//   createTime: number;
//   //检测任务信息
//   recordItem: RecordItem
//   // 检测结果
//   detectionResult?: string;
//   // 检测图片位置
//   imageUri?: string;
//   detectionResultData: DetectionResult = new DetectionResult([],[],[])
//
//   constructor(
//     id: number | undefined,
//     detectId: number,
//     createTime: number,
//     recordItem: RecordItem,
//     detectionResult?: string,
//     imageUri?: string
//   ) {
//     this.id = id ?? 0;
//     this.detectId = detectId;
//     this.createTime = createTime;
//     this.recordItem = RecordItemModel.getById(this.detectId);
//     this.detectionResult = detectionResult;
//     this.imageUri = imageUri;
//   }
// }

import RecordItemModel from '../model/RecordItemModel';
import RecordItem from '../bean/RecordItem';
import { DetectionResult } from './resultViemModel';

export default class RecordVO {
  // 记录ID
  id: number;
  // 检测任务ID
  detectId: number;
  // 检测任务创建日期
  createTime: number;
  // 检测任务信息
  recordItem: RecordItem;
  // 检测结果
  detectionResult?: string;
  // 检测图片位置
  imageUri?: string;
  // 检测结果数据
  detectionResultData: DetectionResult;

  constructor(
    id: number | undefined,
    detectId: number,
    createTime: number,
    recordItem: RecordItem,
    detectionResult?: string,
    imageUri?: string
  ) {
    this.id = id ?? 0;
    this.detectId = detectId;
    this.createTime = createTime;
    this.recordItem = recordItem; // 直接使用传入的 recordItem
    this.detectionResult = detectionResult;
    this.imageUri = imageUri;
    // 初始化 DetectionResult，使用默认值
    this.detectionResultData = new DetectionResult(0, 0); // 默认使用 0 初始化
  }
}
