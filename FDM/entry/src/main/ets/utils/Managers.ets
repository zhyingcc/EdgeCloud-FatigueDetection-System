import { window } from '@kit.ArkUI'

class WindowSizeManager {
  private size: window.Size = { width: 0, height: 0 };

  constructor() {
    window.getLastWindow(getContext()).then((value: window.Window) => {
      const rect: window.Rect = value.getWindowProperties().windowRect;
      this.size.width = px2vp(rect.width);
      this.size.height = px2vp(rect.height);
      console.log(`[windowWidth]${this.size.width} [windowHeight]${this.size.height}`);
    })
  }

  get(): window.Size {
    return this.size;
  }
}

export const windowSizeManager: WindowSizeManager = new WindowSizeManager();