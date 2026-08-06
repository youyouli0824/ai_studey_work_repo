import pandas as pd
print("========1========")
sales_dict={"手机": 120, "笔记本": 45, "平板": 80, "耳机": 240, "智能手表": 110}
s_sales=pd.Series(sales_dict,name="商品季度销售量")
print(s_sales)
print("========2========")
print("商品名称（Index）：",s_sales.index)
print("销量（Values）：",s_sales.values)
print("========3========")
result=s_sales.loc[["笔记本","耳机"]]
print(result)
print("========4========")
result_slice=s_sales.iloc[1:4]
print(result_slice)
print("========5========")
result_loc_slice = s_sales.loc["笔记本":"耳机"]
print(result_loc_slice)
print("========6========")
s_sales.at["智能手表"] = 130
print("修改后的智能手表销量:", s_sales.at["智能手表"])
print("========7========")
s_double=s_sales*2
print(s_double)
print("========8========")
filtered_sales=s_sales[(s_sales>100)&(s_sales<250)]
print(filtered_sales)
print("========9========")
s_channel2=pd.Series(
    {"手机":100,"平板":90,"游戏机":75},
    index=["手机","平板","游戏机","电脑"])
print(s_channel2)
print("空值数量:",s_channel2.isna().sum())
print("========10========")
top3_sales=s_sales.nlargest(3)
print(top3_sales)

import numpy as np
print("--------1--------")
date_index=pd.date_range(start="2026-03-01",periods=10,freq="D")
print(date_index)
print("--------2--------")
temp_data=[12.0, 14.5, np.nan, 18.0, 15.0, np.nan, 22.0, 24.5, 20.0, 19.5]
s_temp=pd.Series(temp_data,index=date_index,name="气温")
print(s_temp.isna())
print("--------3--------")
s_temp=s_temp.ffill()
print(s_temp)
print("--------4--------")
s_weather = pd.Series(["晴", "阴", "阴", "雨", "雨", "晴", "晴", "晴", "阴", "晴"])
print(s_weather.value_counts())
print("--------5--------")
print(s_weather.drop_duplicates(keep="first"))
print("--------6--------")
temp_diff=s_temp.diff()
print(temp_diff)
print("--------7--------")
print(s_temp.pct_change().round(4))
print("--------8--------")
print(s_temp.resample("W").mean())
print("--------9--------")
s_weather.index=s_temp.index
target_days=s_temp[(s_temp>15.0)&(s_weather!="雨")]
print(target_days)
print("--------10--------")
is_rising=s_temp.diff()>0
rising_temps=s_temp[is_rising]
print(rising_temps)



print("########1########")
emp_data = {
    "员工号": ["E01", "E02", "E03", "E04", "E05"],
    "姓名": ["韩梅梅", "李雷", "林涛", "吉姆", "露西"],
    "部门": ["销售", "技术", "销售", "技术", "市场"],
    "月薪": [7500, 12000, 8000, 15000, 9500]
}
df_emp=pd.DataFrame(emp_data)
print(df_emp)
print("表格数据形状 (shape):", df_emp.shape)
print("\n各列数据类型 (dtypes):\n", df_emp.dtypes)
print("########2########")
df_sub = df_emp[["姓名", "月薪"]]
print(df_sub)
print("########3########")
df_emp["年终奖"]=df_emp["月薪"]*2
print(df_emp)
print("########4########")
df_emp.drop(columns=["年终奖"],inplace=True)
print(df_emp)
print("########5########")
lin_tao_info = df_emp.iloc[2]
print(lin_tao_info)
print("########6########")
print(df_emp[df_emp["月薪"]>9000])
print("########7########")
df_emp.at[4, "部门"] = None
print(df_emp.isna().sum())