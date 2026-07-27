def read_float(prompt, min_value=None, max_value=None):
    while True:
        value = input(prompt).strip()
        try:
            num = float(value)
        except ValueError:
            print("输入必须是数字，请重新输入。")
            continue

        if min_value is not None and num <= min_value:
            print(f"数值必须大于 {min_value}，请重新输入。")
            continue
        if max_value is not None and num > max_value:
            print(f"数值必须小于或等于 {max_value}，请重新输入。")
            continue

        return num

H = read_float("请输入你的身高：（米）", min_value=0, max_value=3)
W = read_float("请输入你的体重：（公斤）", min_value=0)

BMI = W / (H ** 2)
print(f"你的BMI指数是：{BMI:.2f}")