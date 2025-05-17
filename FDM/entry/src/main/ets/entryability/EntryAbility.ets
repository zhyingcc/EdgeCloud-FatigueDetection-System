import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';
import PreferencesUtil from '../utils/PreferencesUtil'
import DateUtil from '../utils/DateUtil';
import Logger from '../utils/Logger'
import DBUtil from '../utils/DBUtil'
import RecordModel from '../model/RecordModel';

export default class EntryAbility extends UIAbility {
  async onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): Promise<void> {
    // 加载用户首选项
    PreferencesUtil.loadPreference(this.context)
    Logger.debug('加载用户首选项')
    // 初始化日期
    AppStorage.setOrCreate('selectedDate', DateUtil.beginTimeOfDay(new Date()))
    Logger.debug('初始化日期')
    //初始化数据库
    await DBUtil.initDB(this.context)
    Logger.debug('初始化数据库')
    hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate');
    // 创建数据库表
    DBUtil.createTable(RecordModel.getCreateTableSql())

    Logger.debug('创建record表')
  }

  onDestroy(): void {
    hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onDestroy');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    // Main window is created, set main page for this ability
    hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageCreate');

    windowStage.loadContent('pages/SplashIndex', (err) => {
      if (err.code) {
        hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err) ?? '');
        return;
      }
      hilog.info(0x0000, 'testTag', 'Succeeded in loading the content.');
    });
  }

  onWindowStageDestroy(): void {
    // Main window is destroyed, release UI related resources
    hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageDestroy');
  }

  onForeground(): void {
    // Ability has brought to foreground
    hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onForeground');
  }

  onBackground(): void {
    // Ability has back to background
    hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onBackground');
  }
}
