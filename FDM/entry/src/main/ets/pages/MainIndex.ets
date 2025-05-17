import HomeContent from '../view/home/HomeContent'
import MineContent from '../view/mine/MineContent'
import FuncContent from '../view/function/FuncContent'


@Entry
@Component
struct MainIndex {
  @State selectIndex: number = 0

  @Builder TabBarBuilder(index: number, normalicon: ResourceStr, selIcon: ResourceStr, text:string){
    Column(){
      Image(this.selectIndex ===index ? selIcon : normalicon)
        .width(20)
      Text(text)
        .fontSize(10)
        .fontColor(this.selectIndex === index ? $r('app.color.tab_bar_sel') : $r('app.color.tab_bar_normal'))
    }
  }

  build() {
    Tabs({
      barPosition: BarPosition.End,
      index: this.selectIndex
    }) {
      // 主页
      TabContent() {
        HomeContent()
      }
        .tabBar(this.TabBarBuilder(
          0,
          $r('app.media.ic_tabs_home_normal'),
          $r('app.media.ic_tabs_home_sel'),
          "主页"
        ))
      // 页面2
      TabContent(){
        FuncContent()
      }
        .tabBar(this.TabBarBuilder(
          1,
          $r('app.media.ic_tabs_func_normal'),
          $r('app.media.ic_tabs_func_sel'),
          "驾驶监测"
        ))
      // 页面3
      TabContent() {
        MineContent()
      }
        .tabBar(this.TabBarBuilder(
          2,
          $r('app.media.ic_tabs_mine_normal'),
          $r('app.media.ic_tabs_mine_sel'),
          "个人"
        ))
    }
    .onChange((index: number) => {
      this.selectIndex = index
    })
  }
}