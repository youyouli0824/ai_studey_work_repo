import matplotlib.pyplot as plt
import numpy as np

# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 加载图片
img = plt.imread('output_chart.png')

# 如果图片有 alpha 透明通道，取前 3 个 RGB 通道
if img.shape[2] == 4:
    rgb = img[:, :, :3]
else:
    rgb = img

# 加权平均计算灰度值
gray_img = np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])

plt.figure(figsize=(8, 5))
# cmap='gray' 指定灰度映射
plt.imshow(gray_img, cmap='gray')
plt.title('基于 RGB 加权通道转换后的灰度图像')
plt.axis('off')
plt.show()
