import DateDialog from '../../dialog/DateDialog'
import DateUtil from '../../utils/DateUtil'
import AddButton from './AddButton';
import Logger from '../../utils/Logger';
import router from '@ohos.router'
import ResultDialog from '../../pages/ResultDialog';
import RecordItem from '../../bean/RecordItem';
import RecordVO from '../../viewmodel/RecordVO';
import RecordPO from '../../bean/RecordPO';
import KeepService from '../../service/KeepService';


@Preview
@Component
export default struct HomeContent {
  @StorageProp('date')
  @Watch('aboutToAppear')
  date: number = DateUtil.beginTimeOfDay(new Date())
  @State records: RecordVO[] = []
  @State recordPOs: RecordPO[] = []
  @State record: RecordVO = new RecordVO(0, 0, Date.now(), new RecordItem(0, '', '', ''));

  async aboutToAppear() {
    this.records = await KeepService.selectRecordByDate(this.date)
    Logger.debug('根据日期查')
  }

  addTask() {
    router.pushUrl({ url: 'pages/addTeskPages' })
    Logger.debug('跳转到添加任务页面')
  }

  controller_1: CustomDialogController = new CustomDialogController({
    builder: DateDialog({ date: new Date(this.date) })
  })

  // controller_2: CustomDialogController = new CustomDialogController({
  //   builder: ResultDialog()
  // });

  clickAddBtn(record: RecordVO) {
    if (record.detectionResult) {
      try {
        record.detectionResultData = JSON.parse(record.detectionResult)
      } catch (error) {

      }
    }
    this.record = record
    router.pushUrl({ url: "pages/ResultDialog",params:{
        'record':record
    } })
  }

  defectTypeName() {
  }

  build() {
    Column() {
      Column() {
        Text('疲劳驾驶监测系统')
          .fontSize(30)
          .fontWeight(800)
          .margin({ top: 10, bottom: 100, left: 60 })
        Row() {
          Text(DateUtil.formatDate(this.date))
            .fontSize(15)
            .fontWeight(500)
          Image($r('app.media.arrow_down'))
            .width(20)
        }
        .width('90%')
        .height(50)
        .backgroundColor(Color.White)
        .margin({ left: 19, top: 90 })
        .borderRadius(20)
        .justifyContent(FlexAlign.Center)
        .onClick(() => {
          this.controller_1.open()
        })
      }
      .backgroundImage($r('app.media.car_background'))
      .backgroundImageSize({ width: '100%', height: 300 })
      .width('100%')
      .height('40%')
      .alignItems(HorizontalAlign.Start)
      .borderRadius({ bottomLeft: 20, bottomRight: 20 })

      Stack() {
        Column() {
          Text('')
            .fontSize(20)
            .fontWeight(700)
            .margin({ left: 20, top: 20, bottom: 10 })
          if (this.records.length !== 0) {
            Column() {
              List({ space: 10 }) {
                ForEach(this.records, (item: RecordVO) => {
                  ListItem() {
                    Row() {
                      Image(item.recordItem.image)
                        .width(60)
                        .height(60)
                      Text(item.recordItem.name)
                        .fontSize(16)
                        .fontWeight(600)
                        .opacity(0.8)
                        .margin({ left : 15})
                      Text('-PCB-ID:' + item.id)
                        .fontSize(16)
                        .fontWeight(600)
                        .opacity(0.8)
                      Blank(10)
                      Button('查看驾驶疲劳状况')
                        .backgroundColor(Color.Blue)
                    }
                    .width('100%')
                    .height(50)
                    .backgroundColor(Color.White)
                    .borderRadius(15)
                    .onClick(() => {
                      this.clickAddBtn(item)
                    })
                  }
                  .width('95%')
                })
              }
              .width('100%')
              .alignListItem(ListItemAlign.Center)
            }
            .width('100%')
          } else {
            Column({ space: 8 }) {
              Image($r('app.media.ic_no_data'))
                .width(350)
                .height(220)
              Text('暂无驾驶记录，请开始监测')
                .fontSize(20)
                .opacity(0.4)
            }
            .margin({ top: 50, left: 25 })
          }
        }
        .width('100%')
        .height('100%')
        .alignItems(HorizontalAlign.Start)

        // AddButton({ clickAction: (): void => this.addTask() })
      }
      .width('100%')
      .height('100%')
    }
    .backgroundColor($r('app.color.light_gray'))
  }
}