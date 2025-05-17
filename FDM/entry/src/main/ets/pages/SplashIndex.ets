import UserDialog from '../dialog/UserDialog'
import { common } from '@kit.AbilityKit';
import data_preferences from '@ohos.data.preferences';
import Logger from '../utils/Logger'
import router from '@ohos.router'

//定义用户是否第一次使用app
const PCB_STORE: string = 'PCB_DetectorAppStore'
const IS_PRIVACY: string = 'isPrivacy'
@Preview
@Entry
@Component
struct SplashIndex {
  context: common.UIAbilityContext = getContext(this) as common.UIAbilityContext;
  dialogController: CustomDialogController = new CustomDialogController({
    builder: UserDialog({
      cancel: () => {this.exitApp()},
      confirm: () => {this.onConfirm()}
    })
  })

  // 定义用户点击同意后的操作
  onConfirm() {
    //定义首选项
    let preferences = data_preferences.getPreferences(this.context, PCB_STORE)
    //异步处理首选项中的数据
    preferences.then((res) => {
      //记录用户数据到首选项
      res.put(IS_PRIVACY, true).then(() => {
        res.flush();
        //记录日志
        Logger.debug('SplashIndex', 'isPrivacy记录成功')
        this.jumpToMain()
      }).catch((err: Error) => {
        Logger.error('SplashIndex', 'isPrivacy记录失败，原因：' + err)
      })
    })
  }

  // 定义用户点击取消后的操作
  exitApp() {
    this.context.terminateSelf()
  }


  aboutToAppear() {
    let preferences = data_preferences.getPreferences(this.context, PCB_STORE)
    preferences.then((res) => {
      res.get(IS_PRIVACY, false).then((isPrivate) => {
        //判断传入参数值
        if(isPrivate === true) {
          //说明用户已经点击过同意
          this.jumpToMain()
        } else {
          //弹出弹窗
          this.dialogController.open()
        }
      })
    })
  }

  jumpToMain(){
    setTimeout(() => {
      router.replaceUrl({url: "pages/MainIndex"})
    },2000)
  }

  aboutToDisappear(): void {
    clearTimeout()
  }

  build() {
    Column() {
      Image($r('app.media.logoAndStartIcon'))
        .width(100)
        .margin({top: 160})
      Blank()
        .height('20%')
      // Text('欢迎使用工业质检通')
      //   .fontSize(18)
      //   .fontColor(Color.Blue)
      //   .fontWeight(900)
      //   .letterSpacing(0.1)
      //   .opacity(0.6)
      //   .margin({top :20, bottom:140})
      Image($r('app.media.titlePhoto'))
        .width('80%')
        .margin({bottom:420})
    }
    .width('100%')
    .height('100%')
    // .backgroundImage($r('app.media.welcomeBg'))
    .backgroundImage($r('app.media.bj2_s'))
    .backgroundImageSize({width: '100%', height: '100%'})
    .backgroundImagePosition({x: 0, y:0})
  }
}

