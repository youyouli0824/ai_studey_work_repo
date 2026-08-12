import csv
import random
import hashlib

# 中文姓名库
first_names = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴',
               '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
               '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧',
               '程', '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕',
               '苏', '卢', '蒋', '蔡', '贾', '丁', '魏', '薛', '叶', '阎',
               '余', '潘', '杜', '戴', '夏', '钟', '汪', '田', '任', '姜',
               '范', '方', '石', '姚', '谭', '廖', '邹', '熊', '金', '陆',
               '郝', '孔', '白', '崔', '康', '毛', '邱', '秦', '江', '史',
               '顾', '侯', '邵', '孟', '龙', '万', '段', '雷', '钱', '汤',
               '尹', '黎', '易', '常', '武', '乔', '贺', '赖', '龚', '文']

last_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
              '洋', '勇', '艳', '杰', '倩', '涛', '明', '超', '秀兰', '霞',
              '平', '刚', '桂英', '涛', '慧', '建', '文', '辉', '玲', '桂',
              '云', '飞', '玉兰', '斌', '宇', '鑫', '浩', '然', '博', '文',
              '昊', '子', '轩', '梓', '萱', '涵', '睿', '彤', '妍', '琪']

# 城市列表
cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '重庆',
          '苏州', '天津', '长沙', '郑州', '东莞', '青岛', '沈阳', '宁波', '昆明', '大连',
          '厦门', '福州', '合肥', '济南', '哈尔滨', '长春', '石家庄', '贵阳', '南宁', '太原']

# 信息描述库
info_templates = [
    '江湖人称{}', '擅长{}', '资深{}工程师', '{}领域专家', '热爱{}',
    '专注{}技术', '{}爱好者', '职业{}选手', '自由{}人', '{}达人',
    '科技{}迷', '{}收藏家', '美食{}家', '旅游{}博主', '摄影{}师'
]
info_subjects = ['法外狂徒', '代码', '设计', '音乐', '摄影', '咖啡', '读书', '旅行', '写作', '运动',
                 '美食', '绘画', '编程', '健身', '游戏', '电影', '书法', '围棋', '茶道', '花艺']

def generate_name():
    return random.choice(first_names) + random.choice(last_names)

def generate_email(name, id):
    domains = ['@gmail.com', '@163.com', '@qq.com', '@outlook.com', '@126.com', '@foxmail.com']
    # 用拼音简化模拟
    pinyin_map = {
        '张': 'zhang', '李': 'li', '王': 'wang', '刘': 'liu', '陈': 'chen',
        '杨': 'yang', '赵': 'zhao', '黄': 'huang', '周': 'zhou', '吴': 'wu'
    }
    first = pinyin_map.get(name[0], 'user')
    # 用id生成唯一性
    return f"{first}{id}{random.choice(domains)}"

def generate_phone():
    prefix = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
              '150', '151', '152', '153', '155', '156', '157', '158', '159',
              '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    return random.choice(prefix) + ''.join(str(random.randint(0, 9)) for _ in range(8))

def generate_info():
    template = random.choice(info_templates)
    subject = random.choice(info_subjects)
    return template.format(subject)

# 生成100条数据
data = []
for i in range(1, 101):
    id_num = 10000 + i
    name = generate_name()
    email = generate_email(name, i)
    phone = generate_phone()
    address = random.choice(cities)
    info = generate_info()
    data.append([id_num, name, email, phone, address, info])

# 导出为CSV
with open('student_data.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'e-mail', 'phone_number', 'address', 'info'])
    writer.writerows(data)

print("CSV文件已生成：student_data.csv")
print(f"共生成 {len(data)} 条数据")