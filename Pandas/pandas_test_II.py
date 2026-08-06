import pandas as pd
import numpy as np
s_dirty = pd.Series([10, np.nan, 20, np.nan, 30], index=["a", "b", "c", "d",
"e"])
# 1. 查找缺失值
print("判断是否为空 isna():\n", s_dirty.isna())
# 2. 彻底删除缺失行
print("\n剔除空值后 dropna():\n", s_dirty.dropna())
# 3. 智能填充缺失值 (常用技巧：用均值填充空缺)
mean_val = s_dirty.mean() # 自动忽略 NaN 计算均值：(10+20+30)/3 = 20
s_clean = s_dirty.fillna(mean_val)
print("\n均值填充后 fillna():\n", s_clean)

print("===================")
s_items = pd.Series(["苹果", "苹果", "香蕉", "香蕉", "香蕉", "橙子"])
# 1. 频数统计 (一键统计每个商品卖了多少次，按降序排列)
print("频数统计 value_counts():\n", s_items.value_counts())
# 2. 剔除重复值
print("\n去重后 drop_duplicates():\n", s_items.drop_duplicates())
# 3. 获取不重复的纯 NumPy 数组
print("\n获取唯一值数组 unique():", s_items.unique())
# 4. 统计有多少个不重复的商品
print("唯一值个数 nunique():", s_items.nunique())
print("==================")
dates = pd.date_range(start="2026-03-01", periods=5, freq="B")
print("工作日序列:\n", dates)