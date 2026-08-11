import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']     
plt.rcParams['axes.unicode_minus'] = False 

# ---------- 1. 读取两个数据源 ----------
dir_data = r"C:\shoolwork\my_python_work_myself\shoolwork\np_pd_plot_works"

# 户籍人口：长表，列“年份”“年末户籍人口_万人”等
df_huji = pd.read_csv(f"{dir_data}\\户籍人口和总户数（1949-2024年，部分年份）.csv", encoding='utf-8-sig')

# 常住人口与城镇化率：宽表，行首列为“地区”，后面是各年份的数据列
df_changzhu = pd.read_csv(f"{dir_data}\\分地区常住人口和城镇化率（2022-2024年末）.csv", encoding='utf-8-sig')

# ---------- 2. 清洗户籍人口 ----------
# 只保留“年份”和“年末户籍人口_万人”两列，去除空值，转为数值
df_huji_clean = df_huji[['年份', '年末户籍人口_万人']].copy()
df_huji_clean['年份'] = pd.to_numeric(df_huji_clean['年份'], errors='coerce')
df_huji_clean['年末户籍人口_万人'] = pd.to_numeric(df_huji_clean['年末户籍人口_万人'], errors='coerce')
df_huji_clean.dropna(inplace=True)
# 按年份排序
df_huji_clean.sort_values('年份', inplace=True)

# ---------- 3. 清洗常住人口（宽表 -> 长表） ----------
# 筛选“杭州市合计”行（即全杭州市数据）
hangzhou_row = df_changzhu[df_changzhu['地区'] == '杭州市合计'].iloc[0]

# 提取年份、常住人口、城镇化率
records = []
for col in df_changzhu.columns:
    if '常住人口' in col and '_万人' in col:          # 例：2022年常住人口_万人
        year_str = col.split('年')[0]                 # 得到 "2022"
        year = int(year_str)
        pop = hangzhou_row[col]                       # 常住人口值
        # 寻找对应年份的城镇化率列
        urb_col = f"{year_str}年城镇化率_%"
        urb = hangzhou_row[urb_col] if urb_col in df_changzhu.columns else np.nan
        records.append({'年份': year, '常住人口_万人': pop, '城镇化率_%': urb})

df_changzhu_clean = pd.DataFrame(records)
# 转换为数值并去除缺失
df_changzhu_clean['常住人口_万人'] = pd.to_numeric(df_changzhu_clean['常住人口_万人'], errors='coerce')
df_changzhu_clean['城镇化率_%']   = pd.to_numeric(df_changzhu_clean['城镇化率_%'], errors='coerce')
df_changzhu_clean.dropna(subset=['常住人口_万人', '城镇化率_%'], inplace=True)
df_changzhu_clean.sort_values('年份', inplace=True)
#print(df_huji_clean)
#print(df_changzhu_clean)
# ---------- 4. 合并两个干净的表格 ----------
# 内连接：只保留两个表都有的年份（2022–2024）
df = pd.merge(df_huji_clean, df_changzhu_clean, on='年份', how='inner')

# 计算人口净流入（正值表示常住多于户籍，即净流入）
df['净流入_万人'] = df['常住人口_万人'] - df['年末户籍人口_万人']

print("合并后的数据（人口单位：万人）：")
print(df[['年份', '年末户籍人口_万人', '常住人口_万人', '净流入_万人', '城镇化率_%']])

# ---------- 5. 绘制双轴折线图 ----------
fig, ax1 = plt.subplots(figsize=(10, 6))

# 左轴：户籍人口 and 常住人口
ax1.plot(df['年份'], df['年末户籍人口_万人'], 'o-', label='户籍人口（万人）', linewidth=2)
ax1.plot(df['年份'], df['常住人口_万人'],     's-', label='常住人口（万人）', linewidth=2)
ax1.set_xlabel('年份')
ax1.set_ylabel('人口（万人）')
ax1.legend(loc='upper left')
ax1.grid(True, linestyle=':', alpha=0.5)

# 右轴：城镇化率
ax2 = ax1.twinx()
ax2.plot(df['年份'], df['城镇化率_%'], 'D-', color='green', label='城镇化率（%）', linewidth=2)
ax2.set_ylabel('城镇化率（%）')
ax2.legend(loc='upper right')

plt.title('杭州市人口结构与城镇化率（2022-2024）')
fig.tight_layout()
plt.show()

# ---------- 6. NumPy 计算近十年指标 ----------
# 6.1 户籍人口近十年年均复合增长率（CAGR），取2014‑2024
hui_10 = df_huji_clean[df_huji_clean['年份'].between(2014, 2024)]
pop_2014 = hui_10[hui_10['年份'] == 2014]['年末户籍人口_万人'].values[0]
pop_2024 = hui_10[hui_10['年份'] == 2024]['年末户籍人口_万人'].values[0]
n_years = 10
cagr_huji = (pop_2024 / pop_2014) ** (1 / n_years) - 1

print(f"\n户籍人口近十年（2014‑2024）年均复合增长率：{cagr_huji:.4%}")

# 6.2 城镇化率年均提升幅度（百分点/年），利用现有常住人口数据（2022‑2024）
urb_2022 = df_changzhu_clean[df_changzhu_clean['年份'] == 2022]['城镇化率_%'].values[0]
urb_2024 = df_changzhu_clean[df_changzhu_clean['年份'] == 2024]['城镇化率_%'].values[0]
urb_annual_increase = (urb_2024 - urb_2022) / 2   # 两年差除以年数

print(f"城镇化率年均提升（2022‑2024）：{urb_annual_increase:.2f} 百分点")