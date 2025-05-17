import preferences from '@ohos.data.preferences';
import Logger from './Logger';

/**
 * 首选项工具类
 */
class PreferenceUtil{
  private pref: preferences.Preferences | null = null; // 初始值为 null

  //加载首选项
  async loadPreference(context: Context){
    try {
      //异步处理,获取首选项
      this.pref = await preferences.getPreferences(context, 'PCBStore')
      Logger.debug(`加载Preferences[PCBStore]成功`)
    } catch (e) {
      Logger.debug(`加载Preferences[PCBStore]失败`, JSON.stringify(e))
    }
  }

  //写入首选项值
  async putPreferenceValue(key: string, value: preferences.ValueType){
    if (!this.pref) {
      Logger.debug(`Preferences[PCBStore]尚未初始化！`)
      return
    }
    try {
      // 写入数据
      await this.pref.put(key, value)
      // 刷盘
      await this.pref.flush()
      Logger.debug(`保存Preferences[${key} = ${value}]成功`)
    } catch (e) {
      Logger.debug(`保存Preferences[${key} = ${value}]失败`, JSON.stringify(e))
    }
  }

  //获取首选项值
  async getPreferenceValue(key: string, defaultValue: preferences.ValueType): Promise<preferences.ValueType> {
    if (!this.pref) {
      Logger.debug(`Preferences[PCBStore]尚未初始化！`)
      return defaultValue;
    }
    try {
      // 读数据
      let value = await this.pref.get(key, defaultValue)
      Logger.debug(`读取Preferences[${key} = ${value}]成功`)
      return value
    } catch (e) {
      Logger.debug(`读取Preferences[${key}]失败`, JSON.stringify(e))
      return defaultValue;
    }
  }
}

const preferenceUtil = new PreferenceUtil()

export default preferenceUtil as PreferenceUtil