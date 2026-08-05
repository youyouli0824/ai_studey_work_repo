import pandas as pd
import numpy as np
#print("当前版本：",pd.__version__)
s_custom = pd.Series(
data=[10, 5, 20, 15],
index=["手机", "电脑", "耳机", "手机"], # 标签允许重复
name="商品销量" # 给这一列起个名字
)
print(s_custom)
print("\n=== 从字典创建（键自动成为索引，值自动成为数值） ===")
city_dict = {"北京": 200, "上海": 300, "深圳": 220, "杭州": 280}
s_dict = pd.Series(city_dict)
print(s_dict)

print("\n=== 字典 + 指定 index（展示强大的自动对齐机制） ===")
# 如果指定的行标签在原字典中找不到，Pandas 会自动填充缺失值 NaN！
s_align = pd.Series(city_dict, index=["北京", "上海", "广州"])
print(s_align)

print("\n===从 NumPy 数组创建 ===")
arr = np.random.randint(1, 100, size=5)
s_numpy = pd.Series(arr, index=["a", "b", "c", "d", "e"], name="随机数")
print(s_numpy)

print("\n===创建空 Series 并在后续动态赋值 ===")
s_empty = pd.Series(dtype=int) # 必须显式声明 dtype，否则会有警告
s_empty["语文"] = 95
s_empty["数学"] = 100
s_empty.name="成绩"
print(s_empty)

print(s_empty.shape,s_empty.ndim,s_empty.values)