@Preview
@CustomDialog
export default struct UserDialog{
  controller: CustomDialogController = new CustomDialogController({builder: ''})
  cancel: Function = () => {}
  confirm: Function = () => {}
  build() {
    Column({space: 10}) {
      Text($r('app.string.welcome_title'))
        .fontSize(20)
        .fontWeight(FontWeight.Bolder)
        .margin({top: 8,bottom:5})
      Text(){
        Span($r('app.string.welcome_span_one'))
      }
      Text(){
        Span($r('app.string.welcome_span_two'))
        Span($r('app.string.personal_privacy_protocol'))
          .fontColor($r('app.color.tab_bar_sel'))
        Span($r('app.string.welcome_span_three'))
        Span($r('app.string.team_info'))
          .fontColor($r('app.color.tab_bar_sel'))
        Span($r('app.string.and'))
        Span($r('app.string.welcome_span_four'))
          .fontColor($r('app.color.tab_bar_sel'))
        Span($r('app.string.welcome_span_five'))

      }
      Text(){
        Span($r('app.string.welcome_span_end'))
      }
      Button('同意')
        .fontColor(Color.White)
        .backgroundColor("#007dff")
        .width(150)
        .onClick(() => {
          this.confirm()
          this.controller.close()
        })
      Button('不同意')
        .fontColor("#d09d9d9d")
        .backgroundColor($r('app.color.light_gray'))
        .width(150)
        .onClick(() => {
          this.cancel()
          this.controller.close()
        })
    }
    .width('80%')
    .height('60%')
  }
}