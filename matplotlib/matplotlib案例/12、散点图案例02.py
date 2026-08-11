# 导包
import matplotlib.pyplot as plt
import numpy as np

# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 50 名学生的每周学习时长 (小时)、期末成绩 (分)、以及学习满意度指数 (1~100)
study_hours = np.random.uniform(5, 30, 50)
scores = study_hours * 2.5 + 25 + np.random.normal(0, 5, 50)
satisfaction = study_hours * 2 + np.random.normal(20, 5, 50)

# 设置画布
plt.figure(figsize=(9, 5.5))

# c 控制颜色映射，cmap 设置色彩渐变，s 设置点大小
sc = plt.scatter(study_hours, scores, c=satisfaction, cmap='viridis', s=80, alpha=0.9, edgecolors='gray')

# 添加右侧色彩条 Colorbar
cbar = plt.colorbar(sc)
cbar.set_label('学习满意度指数', fontsize=11)

# 设置标题、标签
plt.title('学生学习时长 vs 期末成绩（颜色映射满意度）', fontsize=14)
plt.xlabel('每周学习时长 (小时)')
plt.ylabel('期末考试成绩 (分)')
# 设置背景
plt.grid(True, alpha=0.3)
plt.show()
