import { DetectionResult } from './resultViemModel'

export default class KeepInfo {
  //日期
  day: number
  detectionResult: DetectionResult

  constructor(day: number, detectionResult: DetectionResult ) {
    this.day = day;
    this.detectionResult = detectionResult
  }
}