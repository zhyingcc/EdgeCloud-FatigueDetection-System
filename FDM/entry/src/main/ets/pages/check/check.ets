import { BusinessError } from '@kit.BasicServicesKit';
import { camera } from '@kit.CameraKit';
import { media } from '@kit.MediaKit';
import { common } from '@kit.AbilityKit';

// 获取 CameraManager 对象
function getCameraManager(context: common.BaseContext): camera.CameraManager {
  return camera.getCameraManager(context);
}

// 获取设备支持的相机列表
function getCameraDevices(cameraManager: camera.CameraManager): Array<camera.CameraDevice> {
  let cameraArray: Array<camera.CameraDevice> = cameraManager.getSupportedCameras();
  if (cameraArray !== undefined && cameraArray.length > 0) {
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

// 获取设备支持的输出能力
async function getSupportedOutputCapability(cameraDevice: camera.CameraDevice, cameraManager: camera.CameraManager, sceneMode: camera.SceneMode): Promise<camera.CameraOutputCapability | undefined> {
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

  // 获取设备支持的输出流能力
  let cameraOutputCapability: camera.CameraOutputCapability = cameraManager.getSupportedOutputCapability(cameraDevice, sceneMode);
  if (!cameraOutputCapability) {
    console.error("cameraManager.getSupportedOutputCapability error");
    return undefined;
  }

  console.info("outputCapability: " + JSON.stringify(cameraOutputCapability));
  return cameraOutputCapability;
}

// 监听相机状态
function onCameraStatus(cameraManager: camera.CameraManager): void {
  cameraManager.on('cameraStatus', (err: BusinessError, cameraStatusInfo: camera.CameraStatusInfo) => {
    if (err !== undefined && err.code !== 0) {
      console.error(`Callback Error, errorCode: ${err.code}`);
      return;
    }
    console.info(`camera: ${cameraStatusInfo.camera.cameraId}`);
    console.info(`status: ${cameraStatusInfo.status}`);
  });
}

// Function to create and get the video SurfaceId
async function getVideoSurfaceId(aVRecorderConfig: media.AVRecorderConfig): Promise<string | undefined> {
  let avRecorder: media.AVRecorder | undefined = undefined;
  try {
    avRecorder = await media.createAVRecorder();
  } catch (error) {
    const err = error as BusinessError;
    console.error(`createAVRecorder call failed. error code: ${err.code}`);
  }
  if (!avRecorder) {
    return undefined;
  }

  avRecorder.prepare(aVRecorderConfig, (err: BusinessError) => {
    if (!err) {
      console.info('AVRecorder prepared successfully');
    } else {
      console.error('AVRecorder preparation failed: ' + err.message);
    }
  });

  const videoSurfaceId = await avRecorder.getInputSurface();
  return videoSurfaceId;
}

// Function to create the video output stream
async function getVideoOutput(cameraManager: camera.CameraManager, videoSurfaceId: string, cameraOutputCapability: camera.CameraOutputCapability): Promise<camera.VideoOutput | undefined> {
  const videoProfilesArray: Array<camera.VideoProfile> = cameraOutputCapability.videoProfiles;
  if (!videoProfilesArray) {
    console.error("No video profiles available");
    return undefined;
  }

  const aVRecorderProfile: media.AVRecorderProfile = {
    fileFormat: media.ContainerFormatType.CFT_MPEG_4,
    videoBitrate: 100000,
    videoCodec: media.CodecMimeType.VIDEO_AVC,
    videoFrameWidth: 640,
    videoFrameHeight: 480,
    videoFrameRate: 30
  };

  const aVRecorderConfig: media.AVRecorderConfig = {
    videoSourceType: media.VideoSourceType.VIDEO_SOURCE_TYPE_SURFACE_YUV,
    profile: aVRecorderProfile,
    url: 'fd://35',
    rotation: 90
  };

  let avRecorder: media.AVRecorder | undefined = undefined;
  try {
    avRecorder = await media.createAVRecorder();
  } catch (error) {
    const err = error as BusinessError;
    console.error(`Failed to create AVRecorder. error code: ${err.code}`);
  }
  if (!avRecorder) {
    return undefined;
  }

  avRecorder.prepare(aVRecorderConfig);

  const videoProfile: camera.VideoProfile | undefined = videoProfilesArray.find((profile) => {
    return profile.size.width === aVRecorderProfile.videoFrameWidth && profile.size.height === aVRecorderProfile.videoFrameHeight;
  });

  if (!videoProfile) {
    console.error('Matching video profile not found');
    return undefined;
  }

  let videoOutput: camera.VideoOutput | undefined = undefined;
  try {
    videoOutput = cameraManager.createVideoOutput(videoProfile, videoSurfaceId);
  } catch (error) {
    const err = error as BusinessError;
    console.error('Failed to create VideoOutput. errorCode = ' + err.code);
  }

  return videoOutput;
}

// Function to start video recording
async function startVideo(videoOutput: camera.VideoOutput, avRecorder: media.AVRecorder): Promise<void> {
  videoOutput.start((err: BusinessError) => {
    if (err) {
      console.error(`Failed to start the video output: ${err.message}`);
    } else {
      console.info('Video output started successfully');
    }
  });

  try {
    await avRecorder.start();
  } catch (error) {
    const err = error as BusinessError;
    console.error(`Failed to start recording: ${JSON.stringify(err)}`);
  }
}

// Function to stop video recording
async function stopVideo(videoOutput: camera.VideoOutput, avRecorder: media.AVRecorder): Promise<void> {
  try {
    await avRecorder.stop();
  } catch (error) {
    const err = error as BusinessError;
    console.error(`Failed to stop recording: ${JSON.stringify(err)}`);
  }

  videoOutput.stop((err: BusinessError) => {
    if (err) {
      console.error(`Failed to stop the video output: ${err.message}`);
    } else {
      console.info('Video output stopped successfully');
    }
  });
}

// UI to control video recording
@Entry
@Component
export default struct CameraPage {
  @State videoOutput: camera.VideoOutput | undefined = undefined;
  @State avRecorder: media.AVRecorder | undefined = undefined;

  build() {
    Column() {
      Button("Start Video Recording").onClick(() => {
        this.setupAndStartRecording();
      });
      Button("Stop Video Recording").onClick(() => {
        this.stopRecording();
      });
    }
  }

  async setupAndStartRecording() {
    const context = getContext(this); // 假设您有获取Context的方式
    const cameraManager = getCameraManager(context);
    const cameraArray = getCameraDevices(cameraManager);

    if (cameraArray.length === 0) {
      console.error("No cameras available on the device");
      return;
    }

    // 假设我们选择第一个设备
    const cameraDevice = cameraArray[0];
    const cameraOutputCapability = await getSupportedOutputCapability(cameraDevice, cameraManager, camera.SceneMode.NORMAL_VIDEO);

    const aVRecorderProfile: media.AVRecorderProfile = {
      fileFormat: media.ContainerFormatType.CFT_MPEG_4,
      videoBitrate: 100000,
      videoCodec: media.CodecMimeType.VIDEO_AVC,
      videoFrameWidth: 640,
      videoFrameHeight: 480,
      videoFrameRate: 30
    };

    const aVRecorderConfig: media.AVRecorderConfig = {
      videoSourceType: media.VideoSourceType.VIDEO_SOURCE_TYPE_SURFACE_YUV,
      profile: aVRecorderProfile,
      url: 'fd://35',
      rotation: 90
    };

    const videoSurfaceId = await getVideoSurfaceId(aVRecorderConfig);
    if (videoSurfaceId && cameraOutputCapability) {
      this.videoOutput = await getVideoOutput(cameraManager, videoSurfaceId, cameraOutputCapability);
    }

    if (this.videoOutput && this.avRecorder) {
      await startVideo(this.videoOutput, this.avRecorder);
    }
  }

  async stopRecording() {
    if (this.videoOutput && this.avRecorder) {
      await stopVideo(this.videoOutput, this.avRecorder);
    }
  }
}
