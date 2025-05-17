export default class RecordPO {
  // 序号
  id?: number;
  // 检测项目类型
  detectId: number = 0;
  // 检测日期
  createTime?: number;
  // 检测结果
  detectionResult?: string;
  // 检测图片位置
  imageUri?: string;
}