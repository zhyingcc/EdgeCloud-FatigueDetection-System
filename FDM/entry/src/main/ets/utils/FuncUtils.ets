export function runWithAnimation(
  fn: Function,
  duration: number = 300,
  curve: Curve = Curve.Smooth): void {
  animateTo({ duration: duration, curve: curve }, () => {
    fn();
  })
}