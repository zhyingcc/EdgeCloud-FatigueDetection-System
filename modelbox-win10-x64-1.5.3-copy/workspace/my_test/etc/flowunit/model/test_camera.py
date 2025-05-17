# 计算摄像头数量
# import cv2
# def get_camera_count():
#     camera_count = 0
#     while True:
#         cap = cv2.VideoCapture(camera_count)
#         if not cap.isOpened():  # 如果无法打开该设备
#             break
#         cap.release()  # 释放摄像头
#         camera_count += 1
#     return camera_count

# camera_count = get_camera_count()
# print(f"检测到的摄像头数量: {camera_count}")


# 检测可打开性
# import cv2
# def test_camera_index(camera_index):
#     cap = cv2.VideoCapture(camera_index)
#     if cap.isOpened():
#         print(f"成功打开摄像头 {camera_index}")
#         cap.release()
#     else:
#         print(f"无法打开摄像头 {camera_index}")

# camera_count = 3  # 你检测到的摄像头数量
# for i in range(camera_count):
#     test_camera_index(i)

# # 打开指定摄像头
# import cv2
# # 假设你想使用索引为1的摄像头
# camera_index = 2
# cap = cv2.VideoCapture(camera_index)

# if not cap.isOpened():
#     print(f"无法打开摄像头 {camera_index}")
# else:
#     print(f"成功打开摄像头 {camera_index}")
    
#     while True:
#         ret, frame = cap.read()  # 从摄像头读取图像
#         if not ret:
#             break

#         # 显示图像
#         cv2.imshow(f"摄像头 {camera_index}", frame)

#         # 按 'q' 键退出
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()  # 释放摄像头
#     cv2.destroyAllWindows()  # 关闭所有 OpenCV 窗口


# 绘制文本测试
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def put_chinese_text(image, text, position, font_size=30):
    # try:
    #     # 设置字体，可以指定路径使用合适的字体文件
    #     font = ImageFont.truetype("C:/Users/86188/AppData/Local/Microsoft/Windows/Fonts/msyh.ttf", font_size)
    # except OSError as e:
    #     print(f"Font loading error: {e}")
    #     font = ImageFont.load_default()  # 如果字体加载失败，使用默认字体


    font = ImageFont.truetype("C:/Users/86188/AppData/Local/Microsoft/Windows/Fonts/msyh.ttf", font_size)

    # 将 OpenCV 图片转换为 Pillow 图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)

    # 绘制中文文本
    draw.text(position, text, font=font, fill=(0, 0, 255))

    # 将 Pillow 图像转换回 OpenCV 图像
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

def test_put_chinese_text():
    # 创建一个空白图像
    width, height = 640, 480
    image = np.ones((height, width, 3), dtype=np.uint8) * 255  # 白色背景

    # 测试绘制中文文本
    text = "警告! 请不要左顾右盼!"
    position = (50, 50)  # 文本位置
    font_size = 30  # 字体大小

    # 调用绘制文本函数
    result_image = put_chinese_text(image, text, position, font_size)

    # 显示结果图像
    cv2.imshow("Test Image", result_image)
    
    # 等待用户按键关闭窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_put_chinese_text()


