import { router } from '@kit.ArkUI'
import RecordItem from '../../bean/RecordItem';
import TaskAddDialog from '../../dialog/TaskAddDialog1';
import RecordItemModel from '../../model/RecordItemModel';


@Entry
@Preview
@Component
export default struct  AddTaskPage {


  @State arr: RecordItem[] = RecordItemModel.list()

  @State itemId: number = 0

  controller: CustomDialogController = new CustomDialogController({
    builder: TaskAddDialog({itemId: this.itemId})
  })

  clickAddBtn(id: number) {
    this.itemId = id
    this.controller.open()
  }

  build() {
    Column() {
      Row(){
        Image($r('app.media.back'))
          .width(25)
      }
      .margin({top: 10, left: 10,bottom: 10})
      .onClick(() => {
        // router.back()
        // 修改处: 使用 router.replace() 跳转到主页，而不是使用 router.back() 返回上一页
        router.back({ url: '../home/HomeContent' })  // 确保 /home 是你定义的主页路由
      })
      List({space: 10}) {
        ForEach(this.arr,(item: RecordItem) => {
          ListItem() {
            Row() {
              Image(item.image)
                .width(60)
                .height(60)
                .margin({ right: 15})
              Column() {
                Text(item.name)
                  .fontSize(18)
                  .fontWeight(500)
                // Text(item.detectType)
                //   .fontSize(14)
                //   .fontWeight(500)
                //   .opacity(0.7)
                Text(item.defectType)
                  .fontSize(14)
                  .fontWeight(500)
                  .opacity(0.7)
              }
              .alignItems(HorizontalAlign.Start)
              Button(){
                Image($r('app.media.add_norm_filled'))
                  .width(20)
              }
              .backgroundColor(Color.Transparent)
              .onClick(() => this.clickAddBtn(item.id))
            }
            .width('100%')
            .justifyContent(FlexAlign.SpaceBetween)
          }
          .width('95%')
          .backgroundColor(Color.White)
          .padding(5)
          .borderRadius(15)
        })
      }
      .width('100%')
      .alignListItem(ListItemAlign.Center)
    }
    .width('100%')
    .height('100%')
    .backgroundColor($r('app.color.light_gray'))
    .alignItems(HorizontalAlign.Start)
  }
}