import picker from '@ohos.file.picker';
import { BusinessError } from '@ohos.base';

class MediaUtil {
  message: string = 'picker';
  imgUris: string[] = []

  photoPicker() {
    try {
      let PhotoSelectOptions = new picker.PhotoSelectOptions();
      PhotoSelectOptions.MIMEType = picker.PhotoViewMIMETypes.IMAGE_TYPE;
      PhotoSelectOptions.maxSelectNumber = 5;
      let photoPicker = new picker.PhotoViewPicker();
      photoPicker.select(PhotoSelectOptions).then((PhotoSelectResult: picker.PhotoSelectResult) => {
        console.info('PhotoViewPicker.select successfully, PhotoSelectResult uri: ' +
        JSON.stringify(PhotoSelectResult));

        // 遍历选择的图片 URI，并依次添加到 imgUris 数组中
        PhotoSelectResult.photoUris.forEach((uri) => {
          this.imgUris.push(uri);
        })
      }).catch((err: BusinessError) => {
        console.error('PhotoViewPicker.select failed with err: ' + JSON.stringify(err));
      });
    } catch (error) {
      let err: BusinessError = error as BusinessError;
      console.error('PhotoViewPicker failed with err: ' + JSON.stringify(err));
    }
  }
}

let mediaUtil = new MediaUtil()
export default MediaUtil