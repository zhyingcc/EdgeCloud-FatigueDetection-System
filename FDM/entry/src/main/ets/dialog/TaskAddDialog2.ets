import RecordItem from '../bean/RecordItem'
import DateUtil from '../utils/DateUtil'
import MediaUtil from '../utils/MediaUtil'
import ItemModel from '../model/RecordItemModel'
import Logger from '../utils/Logger'
import router from '@ohos.router';
import { picker } from '@kit.CoreFileKit';
import { photoAccessHelper } from '@kit.MediaLibraryKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { dataSharePredicates } from '@kit.ArkData';
import KeepService from '../service/KeepService'
import { http } from '@kit.NetworkKit';
import { image } from '@kit.ImageKit';
import resourceManager from '@ohos.resourceManager'
import PermissionsUtil from '../utils/PermissionsUtil'
// import { Permissions } from '@kit.AbilityKit';
import { abilityAccessCtrl, PermissionRequestResult, Permissions } from '@kit.AbilityKit';
import fs from '@ohos.file.fs';
import { DetectionResult } from '../viewmodel/resultViemModel'
import { camera } from '@kit.CameraKit';
import { common } from '@kit.AbilityKit';

// // 在文件顶部定义 PermissionRequestResult 类型
// type PermissionRequestResult = {
//   authResults: number[]; // 0 表示授权成功，其他值表示授权失败
// };

// ...
@Preview
@CustomDialog
@Component
export default struct TaskAddDialog {

  @StorageProp('data') data: number = DateUtil.beginTimeOfDay(new Date())
  @Prop itemId: number
  @State recordItem: RecordItem = ItemModel.getById(this.itemId)
  @State pixelMap: image.PixelMap  | undefined = undefined
  @State uriTemp: string = ''
  //新模块
  @State cameraManager: camera.CameraManager | null = null;
  @State cameraInput: camera.CameraInput | null = null;
  @State previewOutput: camera.PreviewOutput | null = null;
  @State captureSession: camera.CaptureSession | null = null;
  @State imageReceiver: image.ImageReceiver | null = null;
  @State canvasContext: CanvasRenderingContext2D | null = null;




  private permissions: Array<Permissions> = ['ohos.permission.WRITE_IMAGEVIDEO','ohos.permission.READ_IMAGEVIDEO','ohos.permission.CAMERA','ohos.permission.WRITE_MEDIA']
  private imageUri: string = ''

  controller: CustomDialogController
  mediaController: MediaUtil = new MediaUtil()

  // 点击后开始检测
  onConfirm() {
    // Logger.debug('检测任务id'+ this.itemId)
    // // 将记录想添加到数据库并返回到主页面
    // KeepService.insert(this.itemId)
    //   .then(() => {
    //     router.replaceUrl({ url: 'pages/MainIndex' })
    //     this.controller.close()
    // })
    this.requestHttpPost()
      .then((detectionResult) => {
        let imageUri = this.imageUri
        Logger.debug('检测itemId：' + this.itemId)
        // Logger.debug('检测结果：' + detectionResult)
        Logger.debug('图片位置：' + imageUri)
        // 将图片位置和检测结果存储到全局
        return KeepService.insert(this.itemId, detectionResult, imageUri)
      })
      .then(() => {
        router.replaceUrl({ url: 'pages/MainIndex' });
        this.controller.close();
      })
      .catch((err: Error) => {
        Logger.error('发生错误: ' + err.message);
      });
  }

  async aboutToAppear(): Promise<void> {
    PermissionsUtil.checkPermissions(this.permissions)
  }

  //相机整体获取
  async startCameraMonitoring() {
    const context: common.BaseContext = getContext(this);
    this.cameraManager = await this.getCameraManager(context);
    if (this.cameraManager) {
      await this.onCameraStatus(this.cameraManager);
      const cameraDevices = await this.getCameraDevices(this.cameraManager);
      if (cameraDevices.length > 0) {
        const cameraDevice = cameraDevices[0]; // 选择第一个摄像头
        const sceneMode = camera.SceneMode.NORMAL_VIDEO; // 根据需求选择场景模式
        const outputCapability = await this.getSupportedOutputCapability(
          cameraDevice,
          this.cameraManager,
          sceneMode
        );
        if (outputCapability) {
          // 在此可以继续配置摄像头预览和图像捕获
          // 例如，初始化 captureSession，添加输入和输出，启动预览等
          // 请根据您的具体需求添加相应的逻辑
        }
      }
    }
  }

  //摄像头调用
  async getCameraManager(context: common.BaseContext): Promise<camera.CameraManager> {
    let cameraManager: camera.CameraManager = camera.getCameraManager(context);
    return cameraManager;
  }

  //获得相机输入流
  async getSupportedOutputCapability(cameraDevice: camera.CameraDevice, cameraManager: camera.CameraManager, sceneMode: camera.SceneMode): Promise<camera.CameraOutputCapability | undefined> {
  // 创建相机输入流
    let cameraInput: camera.CameraInput | undefined = undefined;
    try {
      cameraInput = cameraManager.createCameraInput(cameraDevice);
    } catch (error) {
      let err = error as BusinessError;
      console.error('Failed to createCameraInput errorCode = ' + err.code);
    }
    if (cameraInput === undefined) {
      return undefined;
    }
    // 监听cameraInput错误信息
    cameraInput.on('error', cameraDevice, (error: BusinessError) => {
      console.error(`Camera input error code: ${error.code}`);
    });
    // 打开相机
    await cameraInput.open();
    // 获取相机设备支持的输出流能力
    let cameraOutputCapability: camera.CameraOutputCapability = cameraManager.getSupportedOutputCapability(cameraDevice, sceneMode);
    if (!cameraOutputCapability) {
      console.error("cameraManager.getSupportedOutputCapability error");
      return undefined;
    }
    console.info("outputCapability: " + JSON.stringify(cameraOutputCapability));
    return cameraOutputCapability;
  }
  // 打包 PixelMap 为 jpg 格式
  async packingPixelMap2Jpg(pixelMap: PixelMap): Promise<ArrayBuffer> {
    const imagePackerApi = image.createImagePacker();
    const packOpts: image.PackingOption = { format: "image/jpeg", quality: 98 };
    let imageBuffer: ArrayBuffer = new ArrayBuffer(1);
    try {
      // 图片压缩或重新打包
      imageBuffer = await imagePackerApi.packing(pixelMap, packOpts);
    } catch (err) {
      console.error(`Invoke packingPixelMap2Jpg failed, err: ${JSON.stringify(err)}`);
    }
    return imageBuffer;
  }
  //相机列表
  async getCameraDevices(cameraManager: camera.CameraManager): Promise<camera.CameraDevice[]> {
    let cameraArray: Array<camera.CameraDevice> = cameraManager.getSupportedCameras();
    if (cameraArray != undefined && cameraArray.length > 0) {
      for (let index = 0; index < cameraArray.length; index++) {
        console.info('cameraId : ' + cameraArray[index].cameraId);  // 获取相机ID
        console.info('cameraPosition : ' + cameraArray[index].cameraPosition);  // 获取相机位置
        console.info('cameraType : ' + cameraArray[index].cameraType);  // 获取相机类型
        console.info('connectionType : ' + cameraArray[index].connectionType);  // 获取相机连接类型
      }
      return cameraArray;
    } else {
      console.error("cameraManager.getSupportedCameras error");
      return [];
    }
  }
  //相机监听
  async onCameraStatus(cameraManager: camera.CameraManager): Promise<void> {
    cameraManager.on('cameraStatus', (err: BusinessError, cameraStatusInfo: camera.CameraStatusInfo) => {
      if (err !== undefined && err.code !== 0) {
        console.error(`Callback Error, errorCode: ${err.code}`);
        return;
      }
      console.info(`camera: ${cameraStatusInfo.camera.cameraId}`);
      console.info(`status: ${cameraStatusInfo.status}`);
    });
  }
  // 在rawfile读取图片
  async getPixelMapByImage():Promise<image.PixelMap>{
    const context : Context = getContext(this);
    // 获取resourceManager资源管理器
    const resourceMgr : resourceManager.ResourceManager = context.resourceManager;
    let rawFileDescriptor = await resourceMgr.getRawFd('detectImg.jpg')
    const imageSource : image.ImageSource = image.createImageSource(rawFileDescriptor);
    let decodingOptions : image.DecodingOptions = {
      editable: true,
      desiredPixelFormat: 3,
    }
    // 创建pixelMap并进行简单的旋转和缩放
    const pixelMap:image.PixelMap = await imageSource.createPixelMap(decodingOptions)
    this.pixelMap =  pixelMap
    return pixelMap;
  }


  //展示相册第一张图片
  async showFirstPhoto() {
    let context = getContext(this);
    let phAccessHelper = photoAccessHelper.getPhotoAccessHelper(context);
    console.info('getAssets');
    let predicates: dataSharePredicates.DataSharePredicates = new dataSharePredicates.DataSharePredicates();
    let fetchOptions: photoAccessHelper.FetchOptions = {
      fetchColumns: [],
      predicates: predicates
    };
    phAccessHelper.getAssets(fetchOptions, async (err, fetchResult) => {
      if (fetchResult !== undefined) {
        console.info('fetchResult success');
        let photoAsset: photoAccessHelper.PhotoAsset = await fetchResult.getFirstObject();
        this.uriTemp = photoAsset.uri
        if (photoAsset !== undefined) {
          console.info('photoAsset.displayName : ' + photoAsset.displayName);
        }
      } else {
        console.error(`fetchResult fail with error: ${err.code}, ${err.message}`);
      }
    });
  }

  // 读取图片并写入相册
  async WritePhoto() {
    console.info('createAssetDemo');
    let context = getContext(this);
    let phAccessHelper = photoAccessHelper.getPhotoAccessHelper(context);
    let photoType: photoAccessHelper.PhotoType = photoAccessHelper.PhotoType.IMAGE;
    let extension:string = 'jpg';
    let options: photoAccessHelper.CreateOptions = {
      title: 'testPhoto'
    }
    let uri = await phAccessHelper.createAsset(photoType, extension, options);
    // 使用uri打开文件，可以持续写入内容，写入过程不受时间限制
    let file = await fs.open(uri, fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE);
    try {
      const imageBuffer = await this.packingPixelMap2Jpg(this.pixelMap as image.PixelMap)

      // 写到媒体库文件中
      await fs.write(file.fd, imageBuffer);
      await fs.close(file.fd);
      AlertDialog.show({message:'已保存至相册!'});
      Logger.debug('已保存至相册')
    }
    catch (err) {
      console.error("error is "+ JSON.stringify(err))
    }
  }

  // 选择视频
  selectVideo(): Promise<string> {
    return new Promise((resolve, reject) => {
      let videoPicker = new picker.PhotoViewPicker();
      let videoSelectOption = new picker.PhotoSelectOptions();
      videoSelectOption.MIMEType = picker.PhotoViewMIMETypes.VIDEO_TYPE; // 选择视频类型
      videoPicker.select(videoSelectOption).then((videoSelectResult) => {
        Logger.debug("视频选择结果:" + videoSelectResult);
        let uri = videoSelectResult.photoUris[0]; // 返回视频URI
        Logger.debug("视频uri:" + uri);
        resolve(uri);
      }).catch((err: BusinessError) => {
        Logger.debug('视频选择失败, code is' + err.code + ' message is' + err.message);
        reject(err);
      });
    });
  }

  // pickPhoto选择图片
  selectImage(): Promise<string> {
    return new Promise((resolve, reject) => {
      let photoViewPicker = new picker.PhotoViewPicker();
      let photoSelectOption = new picker.PhotoSelectOptions();
      photoSelectOption.MIMEType = picker.PhotoViewMIMETypes.IMAGE_TYPE;
      photoViewPicker.select(photoSelectOption).then((photoSelectResult) => {
        Logger.debug("图片选择结果:" + photoSelectResult);
        let uri = photoSelectResult.photoUris[0];
        Logger.debug("图片uri:" + uri);
        resolve(uri);
      }).catch((err: BusinessError) => {
        Logger.debug('Invoke photoViewPicker.select failed, code is' + err.code + 'message is' + err.message);
        reject(err);
      });
    });
}

  requestHttpPostForVideo(): Promise<DetectionResult> {
    return new Promise((resolve, reject) => {
      let uri = this.imageUri; // 使用选择到的视频uri
      try {
        let resultVideo = fs.openSync(uri, fs.OpenMode.READ_ONLY);
        let fileTemp = fs.openSync(getContext().filesDir + resultVideo.name, fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE);
        let videoUri = fileTemp.path;
        fs.copyFileSync(resultVideo.fd, fileTemp.fd);
        fs.closeSync(resultVideo);
        fs.closeSync(fileTemp);

        const httpRequest = http.createHttp();
        httpRequest.request('https://015c2ea02afc4cf0afbd3935a760adab.apig.cn-north-4.huaweicloudapis.com/v1/infers/d8700113-5c4a-4ee7-b987-18e87ea6062b', { // 使用正确的API端点
          method: http.RequestMethod.POST,
          header: {
            'content-Type': 'application/json',
            'Connection': 'keep-alive',
            'X-Auth-Token': 'MIIN2gYJKoZIhvcNAQcCoIINyzCCDccCAQExDTALBglghkgBZQMEAgEwggvsBgkqhkiG9w0BBwGgggvdBIIL2XsidG9rZW4iOnsiZXhwaXJlc19hdCI6IjIwMjQtMTAtMDVUMDg6MzU6NDAuMzczMDAwWiIsIm1ldGhvZHMiOlsicGFzc3dvcmQiXSwiY2F0YWxvZyI6W10sInJvbGVzIjpbeyJuYW1lIjoidGVfYWRtaW4iLCJpZCI6IjAifSx7Im5hbWUiOiJ0ZV9hZ2VuY3kiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3JlcF9hY2NlbGVyYXRpb24iLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfZGlza0FjYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Rzc19tb250aCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29ic19kZWVwX2FyY2hpdmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2NuLXNvdXRoLTRjIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZGVjX21vbnRoX3VzZXIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jYnJfc2VsbG91dCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vbGRfcmVvdXJjZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX3Bhbmd1IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfd2VsaW5rYnJpZGdlX2VuZHBvaW50X2J1eSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Nicl9maWxlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZG1zLXJvY2tldG1xNS1iYXNpYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Rtcy1rYWZrYTMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lZGdlc2VjX29idCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29ic19kZWNfbW9udGgiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3Jlc3RvcmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9pZG1lX21ibV9mb3VuZGF0aW9uIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX2M2YSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX211bHRpX2JpbmQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9zbW5fY2FsbG5vdGlmeSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfYXAtc291dGhlYXN0LTNkIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfY3Nic19wcm9ncmVzc2JhciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Nlc19yZXNvdXJjZWdyb3VwX3RhZyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vZmZsaW5lX2FjNyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2V2c19yZXR5cGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9rb29tYXAiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9ldnNfZXNzZDIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9kbXMtYW1xcC1iYXNpYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2V2c19wb29sX2NhIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9jbi1zb3V0aHdlc3QtMmIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9od2NwaCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vZmZsaW5lX2Rpc2tfNCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2h3ZGV2IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfc21uX3dlbGlua3JlZCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2h2X3ZlbmRvciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfY24tbm9ydGgtNGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2NuLW5vcnRoLTRkIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX2hlY3NfeCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19hYzciLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lcHMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3Jlc3RvcmVfYWxsIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9jbi1ub3J0aC00ZiIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29jdG9wdXMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9vcF9nYXRlZF9yb3VuZHRhYmxlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX2V4dCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX3Bmc19kZWVwX2FyY2hpdmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2FwLXNvdXRoZWFzdC0xZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfcnUtbW9zY293LTFiIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9hcC1zb3V0aGVhc3QtMWQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hcHBzdGFnZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfYXAtc291dGhlYXN0LTFmIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfc21uX2FwcGxpY2F0aW9uIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX2NvbGQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9yZHNfY2EiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfZ3B1X2c1ciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29wX2dhdGVkX21lc3NhZ2VvdmVyNWciLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfcmkiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX3J1LW5vcnRod2VzdC0yYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2llZl9wbGF0aW51bSIsImlkIjoiMCJ9XSwicHJvamVjdCI6eyJkb21haW4iOnsibmFtZSI6ImhpZF9lYjJnbnhzNTV5cWRubl8iLCJpZCI6Ijc4NDM5MjJhZTEyYjRhZmFhMTEzNTZhNWMyZGNmMDRlIn0sIm5hbWUiOiJjbi1ub3J0aC00IiwiaWQiOiI4N2IxYjYyMDdiMjk0NTEzYWFhNmE2MDcxOGM2ZDY2OCJ9LCJpc3N1ZWRfYXQiOiIyMDI0LTEwLTA0VDA4OjM1OjQwLjM3MzAwMFoiLCJ1c2VyIjp7ImRvbWFpbiI6eyJuYW1lIjoiaGlkX2ViMmdueHM1NXlxZG5uXyIsImlkIjoiNzg0MzkyMmFlMTJiNGFmYWExMTM1NmE1YzJkY2YwNGUifSwibmFtZSI6IkN6cSIsInBhc3N3b3JkX2V4cGlyZXNfYXQiOiIiLCJpZCI6ImI3Zjk1ZDVhOGNlZDRhYThhNWE5YmFlMjg4MGExZjQyIn19fTGCAcEwggG9AgEBMIGXMIGJMQswCQYDVQQGEwJDTjESMBAGA1UECAwJR3VhbmdEb25nMREwDwYDVQQHDAhTaGVuWmhlbjEuMCwGA1UECgwlSHVhd2VpIFNvZnR3YXJlIFRlY2hub2xvZ2llcyBDby4sIEx0ZDEOMAwGA1UECwwFQ2xvdWQxEzARBgNVBAMMCmNhLmlhbS5wa2kCCQDcsytdEGFqEDALBglghkgBZQMEAgEwDQYJKoZIhvcNAQEBBQAEggEAC5ApL65rZ5ly5X61BxQPGZXnIvBq+SYgdRAUVxrft2kgUQRML6LDeq3ThJOvpiIkjvc4rQqToeVRYObJpvTIf4RM7GbIORg5-TElM6h8Fi-XirTZOjLUa1iGjRaY2E49h07xOIdurX+DlwpCfn2SSaIZzshwzshzly+MII9Czwvb07-eqXzmxXE8io9+7BCK8CJ7uadSS8DfEUT-H3IbDwXqhQwAmcDiLphDs2pD6+61EdQJX4yT3q8OqNaIw6SVWrEefCAEhNRND5RZ4GpQRNOActLOieIousIbK38qeoZrUSir8Z2SBDsvyGCy+tBPDsTCmqADntHAOvsVBrlZRQ=='
          },
          expectDataType: http.HttpDataType.STRING,
          multiFormDataList: [{
            name: 'file',
            contentType: 'video/mp4', // 视频类型
            filePath: videoUri
          }],
        }, (err: BusinessError, data: http.HttpResponse) => {
          if (!err) {
            if (typeof data.result === 'string') {
              Logger.debug('返回值为' + data.result);
              let detectionResult: DetectionResult = JSON.parse(data.result) as DetectionResult; //Error message:Unexpected Text in JSON
              resolve(detectionResult);
            } else {
              reject('Unexpected data format');
            }
          } else {
            Logger.error('返回错误原因:' + JSON.stringify(err));
            reject(err);
          }
          httpRequest.destroy();
        });
      } catch (err) {
        Logger.debug('请求上传失败' + JSON.stringify(err));
        reject(err);
      }
    });
  }

  requestHttpPost(): Promise<DetectionResult> {
  return new Promise((resolve, reject) => {
    let uri = '';
    let photoViewPicker = new picker.PhotoViewPicker();
    let photoSelectOption = new picker.PhotoSelectOptions();
    photoSelectOption.MIMEType = picker.PhotoViewMIMETypes.IMAGE_TYPE;
    photoViewPicker.select(photoSelectOption).then((photoSelectResult) => {
      Logger.debug("图片选择结果:" + photoSelectResult);
      uri = photoSelectResult.photoUris[0];
      Logger.debug("图片uri:" + uri);
      try {
        let resultPhoto = fs.openSync(uri, fs.OpenMode.READ_ONLY);
        // let resultName = resultPhoto.name;
        let fileTemp = fs.openSync(getContext().filesDir + resultPhoto.name, fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE);
        let imageUri = fileTemp.path;
        this.imageUri = imageUri
        fs.copyFileSync(resultPhoto.fd, fileTemp.fd);
        fs.closeSync(resultPhoto);
        fs.closeSync(fileTemp);
        const httpRequest = http.createHttp();
        httpRequest.request('https://015c2ea02afc4cf0afbd3935a760adab.apig.cn-north-4.huaweicloudapis.com/v1/infers/d8700113-5c4a-4ee7-b987-18e87ea6062b', {
          method: http.RequestMethod.POST,
          header: {
            'content-Type': 'application/json',
            'Connection': 'keep-alive',
            'X-Auth-Token': 'MIIN2gYJKoZIhvcNAQcCoIINyzCCDccCAQExDTALBglghkgBZQMEAgEwggvsBgkqhkiG9w0BBwGgggvdBIIL2XsidG9rZW4iOnsiZXhwaXJlc19hdCI6IjIwMjQtMTAtMDVUMDg6MzU6NDAuMzczMDAwWiIsIm1ldGhvZHMiOlsicGFzc3dvcmQiXSwiY2F0YWxvZyI6W10sInJvbGVzIjpbeyJuYW1lIjoidGVfYWRtaW4iLCJpZCI6IjAifSx7Im5hbWUiOiJ0ZV9hZ2VuY3kiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3JlcF9hY2NlbGVyYXRpb24iLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfZGlza0FjYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Rzc19tb250aCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29ic19kZWVwX2FyY2hpdmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2NuLXNvdXRoLTRjIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZGVjX21vbnRoX3VzZXIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jYnJfc2VsbG91dCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vbGRfcmVvdXJjZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX3Bhbmd1IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfd2VsaW5rYnJpZGdlX2VuZHBvaW50X2J1eSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Nicl9maWxlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZG1zLXJvY2tldG1xNS1iYXNpYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Rtcy1rYWZrYTMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lZGdlc2VjX29idCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29ic19kZWNfbW9udGgiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3Jlc3RvcmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9pZG1lX21ibV9mb3VuZGF0aW9uIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX2M2YSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX211bHRpX2JpbmQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9zbW5fY2FsbG5vdGlmeSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfYXAtc291dGhlYXN0LTNkIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfY3Nic19wcm9ncmVzc2JhciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Nlc19yZXNvdXJjZWdyb3VwX3RhZyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vZmZsaW5lX2FjNyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2V2c19yZXR5cGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9rb29tYXAiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9ldnNfZXNzZDIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9kbXMtYW1xcC1iYXNpYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2V2c19wb29sX2NhIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9jbi1zb3V0aHdlc3QtMmIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9od2NwaCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vZmZsaW5lX2Rpc2tfNCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2h3ZGV2IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfc21uX3dlbGlua3JlZCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2h2X3ZlbmRvciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfY24tbm9ydGgtNGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2NuLW5vcnRoLTRkIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX2hlY3NfeCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19hYzciLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lcHMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3Jlc3RvcmVfYWxsIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9jbi1ub3J0aC00ZiIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29jdG9wdXMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9vcF9nYXRlZF9yb3VuZHRhYmxlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX2V4dCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX3Bmc19kZWVwX2FyY2hpdmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2FwLXNvdXRoZWFzdC0xZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfcnUtbW9zY293LTFiIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9hcC1zb3V0aGVhc3QtMWQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hcHBzdGFnZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfYXAtc291dGhlYXN0LTFmIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfc21uX2FwcGxpY2F0aW9uIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZXZzX2NvbGQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9yZHNfY2EiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfZ3B1X2c1ciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29wX2dhdGVkX21lc3NhZ2VvdmVyNWciLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfcmkiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX3J1LW5vcnRod2VzdC0yYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2llZl9wbGF0aW51bSIsImlkIjoiMCJ9XSwicHJvamVjdCI6eyJkb21haW4iOnsibmFtZSI6ImhpZF9lYjJnbnhzNTV5cWRubl8iLCJpZCI6Ijc4NDM5MjJhZTEyYjRhZmFhMTEzNTZhNWMyZGNmMDRlIn0sIm5hbWUiOiJjbi1ub3J0aC00IiwiaWQiOiI4N2IxYjYyMDdiMjk0NTEzYWFhNmE2MDcxOGM2ZDY2OCJ9LCJpc3N1ZWRfYXQiOiIyMDI0LTEwLTA0VDA4OjM1OjQwLjM3MzAwMFoiLCJ1c2VyIjp7ImRvbWFpbiI6eyJuYW1lIjoiaGlkX2ViMmdueHM1NXlxZG5uXyIsImlkIjoiNzg0MzkyMmFlMTJiNGFmYWExMTM1NmE1YzJkY2YwNGUifSwibmFtZSI6IkN6cSIsInBhc3N3b3JkX2V4cGlyZXNfYXQiOiIiLCJpZCI6ImI3Zjk1ZDVhOGNlZDRhYThhNWE5YmFlMjg4MGExZjQyIn19fTGCAcEwggG9AgEBMIGXMIGJMQswCQYDVQQGEwJDTjESMBAGA1UECAwJR3VhbmdEb25nMREwDwYDVQQHDAhTaGVuWmhlbjEuMCwGA1UECgwlSHVhd2VpIFNvZnR3YXJlIFRlY2hub2xvZ2llcyBDby4sIEx0ZDEOMAwGA1UECwwFQ2xvdWQxEzARBgNVBAMMCmNhLmlhbS5wa2kCCQDcsytdEGFqEDALBglghkgBZQMEAgEwDQYJKoZIhvcNAQEBBQAEggEAC5ApL65rZ5ly5X61BxQPGZXnIvBq+SYgdRAUVxrft2kgUQRML6LDeq3ThJOvpiIkjvc4rQqToeVRYObJpvTIf4RM7GbIORg5-TElM6h8Fi-XirTZOjLUa1iGjRaY2E49h07xOIdurX+DlwpCfn2SSaIZzshwzshzly+MII9Czwvb07-eqXzmxXE8io9+7BCK8CJ7uadSS8DfEUT-H3IbDwXqhQwAmcDiLphDs2pD6+61EdQJX4yT3q8OqNaIw6SVWrEefCAEhNRND5RZ4GpQRNOActLOieIousIbK38qeoZrUSir8Z2SBDsvyGCy+tBPDsTCmqADntHAOvsVBrlZRQ=='
          },
          expectDataType: http.HttpDataType.STRING,
          multiFormDataList: [{
            name: 'file',
            contentType: 'image/jpg',
            filePath: imageUri
          }],
        }, (err: BusinessError, data: http.HttpResponse) => {
          Logger.debug('test:上传结束');
          if (!err) {
            if (typeof data.result == 'string') {
              Logger.debug('返回值为' + data.result);
              Logger.debug('返回调用代码:' + data.responseCode );
              let detectionResult: DetectionResult = JSON.parse(data.result) as DetectionResult;
              Logger.debug('返回驾驶违规类型:' + detectionResult.category);
              Logger.debug('返回驾驶违规持续时间:' + detectionResult.duration);
              // Logger.debug('返回错误类型结果:' + detectionResult.detection_classes);
              // Logger.debug('返回错误位置结果:' + detectionResult.detection_boxes);
              // Logger.debug('返回置信度结果:' + detectionResult.detection_scores);
              resolve(detectionResult);
            } else {
              reject('Unexpected data format');
            }
          } else {
            Logger.error('返回错误原因:' + JSON.stringify(err));
            reject(err);
          }
          httpRequest.destroy();
        });
      } catch (err) {
        Logger.debug('请求上传失败' + JSON.stringify(err));
        reject(err);
      }
    }).catch((err: BusinessError) => {
      Logger.debug('Invoke photoViewPicker.select failed, code is' + err.code + ' message is' + err.message);
      reject(err);
    });
  });
}

build() {
    Column() {
      Row() {
        Text(DateUtil.formatDate(this.data))
          .fontSize(20)
          .fontWeight(600)
          .margin({top: 5, left: 5})
        Blank(10)
        Button() {
          Text('x')
            .fontSize(15)
            .fontColor(Color.White)
            .fontWeight(800)
        }
        .width(20)
        .height(20)
        .backgroundColor(Color.Red)
        .padding({ bottom: 5 })
        .onClick(() => {
          this.controller.close()
        })
      }
      .width('95%')
      .justifyContent(FlexAlign.End)


      // Column({ space: 10 }) {
      //   Button() {
      //     Text('摄像头监测')
      //       .fontSize(18)
      //       .fontWeight(600)
      //   }
      //   .width('80%')
      //   .height(50)
      //   .backgroundColor("#ffd0d0d0")
      //   // .onClick(() => {
      //   //   this.startCameraMonitoring()
      //   // })
      //   .onClick(async () => {
      //     const context = getContext(this);
      //     try {
      //       let atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager();
      //       let context: Context = getContext(this) as common.UIAbilityContext;
      //       atManager.requestPermissionsFromUser(context, ['ohos.permission.CAMERA'], (err: BusinessError, data: PermissionRequestResult) => {
      //         if (err) {
      //           console.error(`requestPermissionsFromUser fail, err->${JSON.stringify(err)}`);
      //         } else {
      //           this.startCameraMonitoring();
      //           console.info('data:' + JSON.stringify(data));
      //           console.info('data permissions:' + data.permissions);
      //           console.info('data authResults:' + data.authResults);
      //           console.info('data dialogShownResults:' + data.dialogShownResults);
      //         }
      //       });
      //     } catch (err) {
      //       Logger.error('权限请求错误: ' + err);
      //     }
      //   })


      Column({ space: 10 }) {
        Button() {
          Text('摄像头监测4')
            .fontSize(18)
            .fontWeight(600)
        }
        .width('80%')
        .height(50)
        .backgroundColor("#ffd0d0d0")
        .onClick(async () => {
          try {
            // 创建 AtManager 实例
            let atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager();
            let context: Context = getContext(this) as common.UIAbilityContext;

            // 请求摄像头权限
            atManager.requestPermissionsFromUser(context, ['ohos.permission.CAMERA'], async (err: BusinessError, data: PermissionRequestResult) => {
              if (err) {
                console.error(`requestPermissionsFromUser fail, err->${JSON.stringify(err)}`);
              } else {
                // 判断权限授予结果，authResults 为数组，值为 0 代表已授予
                if (data.authResults && data.authResults[0] === 0) {
                  await this.startCameraMonitoring();  // 调用摄像头监测
                  console.info('摄像头权限已授予，开始监测');
                } else {
                  console.error('摄像头权限被拒绝');
                }
              }
            });
          } catch (err) {
            Logger.error('权限请求错误: ' + JSON.stringify(err));
          }
        })

      Button() {
          Text('从相册选择视频')
            .fontSize(18)
            .fontWeight(600)
        }
        .width('80%')
        .height(50)
        .backgroundColor("#ffd0d0d0")
        .onClick(() => {
          this.selectVideo()
            .then((uri: string) => {
              Logger.debug('视频选择成功，uri:', uri);
              this.imageUri = uri;
              // 调用上传视频的方法
              return this.requestHttpPostForVideo();
              // return this.requestHttpPost();
            })
            .then((detectionResult: DetectionResult) => {
              // 如果 detectionResult 是一个复杂对象，你需要提取属性或转换为字符串
              Logger.debug('检测结果：' + JSON.stringify(detectionResult)); // 转换为 JSON 字符串以输出
              // 或者直接输出具体的属性
              Logger.debug('检测类别：' + detectionResult.category);
            })
            .catch((error: Error) => {
              Logger.error('操作失败：', error.message);
            });
        })

        // Button() {
        //   Text('本地视频上传')
        //     .fontSize(18)
        //     .fontWeight(600)
        // }
        // .width('80%')
        // .height(50) // 50
        // .backgroundColor("#ffd0d0d0")
        // .onClick(() => {
        //   // const result: DetectionResult = callModelArtsAPI()
        //   // this.pickPhotoBtn()
        //   // this.onConfirm()
        //   this.getPixelMapByImage()
        //   this.WritePhoto()
        // })

        Button() {
          Text('取消')
            .fontSize(18)
            .fontWeight(600)
        }
        .width('80%')
        .height(50)
        .backgroundColor("#ffd0d0d0")
        .onClick(() => {
          this.controller.close()
        })

        // Column() {
        //   Button('待检测图片预览')
        //     .onClick(() => {
        //
        //     })
        //   Image(this.pixelMap)
        //     .width(300)
        //     .height(300)
        //   Button('开始检测')
        //     .onClick(() => {
        //       this.onConfirm()
        //     })
        // }
      }
      .width('95%')
      .height('37%')
      .alignItems(HorizontalAlign.Center)
    }
  }
}