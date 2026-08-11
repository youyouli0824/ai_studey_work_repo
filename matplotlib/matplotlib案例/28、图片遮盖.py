import matplotlib.pyplot as plt

# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 读取本地文件
img = plt.imread('beauty.jpeg').copy()

# 获取图像高、宽
h, w, c = img.shape

# 在图片顶部 20%~40% 的区域添加半透明红色遮罩 (RGB 中的 R 通道加深)
img[int(h*0.2):int(h*0.4), :, 0] = 1.0 # 红色通道设为最大值 1.0
# img[int(h*0.2):int(h*0.4), :, 1] *= 0.5 # 绿色通道减半

plt.imshow(img)
plt.title('在图像特定区域叠加半透明红色遮罩')
plt.axis('off')
plt.show()