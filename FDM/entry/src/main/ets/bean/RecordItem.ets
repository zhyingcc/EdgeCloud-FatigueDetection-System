// export default class RecordItem {
//   // 检测任务id
//   id: number;
//   // 检测任务名称
//   name: string;
//   // 检测图标
//   image: ResourceStr
//   // 检测对象类别
//   detectType: string;
//   // 检测缺陷种类
//   defectType: string;
//
//   constructor(id: number, name: string, image: ResourceStr, detectType: string, defectType: string) {
//     this.id = id;
//     this.name = name;
//     this.image = image;
//     this.detectType = detectType;
//     this.defectType = defectType;
//   }
// }
export default class RecordItem {
  // 检测任务id
  id: number;
  // 检测任务名称
  name: string;
  // 检测图标
  image: ResourceStr
  // 检测对象方式
  // detectType: string;
  // 驾驶状态
  defectType: string;

  constructor(id: number, name: string, image: ResourceStr, defectType: string) {
    this.id = id;
    this.name = name;
    this.image = image;
    // this.detectType = detectType;
    this.defectType = defectType;
  }
}


