@CustomDialog
export default struct DateDialog {
  controller: CustomDialogController
  date: Date = new Date ()

  build() {
    Column() {
      DatePicker({
        start: new Date('2020-01-01'),
        end: new Date(),
        selected: this.date
      })
        .onChange((value: DatePickerResult) => {
          const year = value.year ?? new Date().getFullYear();
          const month = (value.month ?? (new Date().getMonth() + 1)) ;
          const day = value.day ?? new Date().getDate();

          this.date.setFullYear(year, month, day);
        })

      Row({space: 20}){
        Button('取消')
          .width(120)
          .backgroundColor($r('app.color.light_gray'))
          .onClick(() => {
            this.controller.close()
          })
        Button('确定')
          .width(120)
          .backgroundColor($r('app.color.theme_color'))
          .onClick(() => {
            // 将日期保存在全局
            AppStorage.setOrCreate('date', this.date.getTime())
            //关闭弹窗
            this.controller.close()
          })
      }
    }
    .padding(12)
  }
}