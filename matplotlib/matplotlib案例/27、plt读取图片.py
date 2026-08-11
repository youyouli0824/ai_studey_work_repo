import matplotlib.pyplot as plt

# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 读取图像文件 (返回一个 NumPy 三维数组 [高度, 宽度, 通道RGB/RGBA])
img = plt.imread('beauty.jpeg')

print("图像矩阵形状 (Shape):", img.shape)
print("图像数据类型 (Dtype):", img.dtype)

# 显示读取到的图片
plt.imshow(img)
plt.axis('off') # 关闭坐标轴刻度显示
plt.title('读取并显示的本地图像')
plt.show()
