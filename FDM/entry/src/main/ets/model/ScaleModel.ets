@Observed
export class ScaleModel {
  public scaleValue: number;
  public lastValue: number;
  public maxScaleValue: number;
  public extraScaleValue: number;
  public readonly defaultScaleValue: number = 1;

  constructor(scaleValue: number = 1.0, lastValue: number = 1.0,
              maxScaleValue: number = 1.5, extraScaleValue: number = 0.2) {
    this.scaleValue = scaleValue;
    this.lastValue = lastValue;
    this.maxScaleValue = maxScaleValue;
    this.extraScaleValue = extraScaleValue;
  }

  reset(): void {
    this.scaleValue = this.defaultScaleValue;
    this.lastValue = this.scaleValue;
  }

  stash(): void {
    this.lastValue = this.scaleValue;
  }

  toString(): string {
    return `[scaleValue: ${this.scaleValue} lastValue: ${this.lastValue}]`;
  }
}