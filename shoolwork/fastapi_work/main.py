# ==========================================
# 文件名: main.py
# 描述: 我们的第一个 FastAPI Web 应用程序
# Python 版本: 3.12.0
# FastAPI 版本: 0.138.0
# ==========================================
# 1、导入模块
from fastapi import FastAPI
import numpy as np

# 2、创建FastAPI的应用程序
app = FastAPI(
    title="高校图书管理系统 API 服务",
    description="""
    本项目为 **计算机系新生** FastAPI 教学实战项目。

    ## 包含模块:
    * 📚 **图书模块**: 图书检索、借阅、新增、修改
    * 👤 **用户模块**: 读者注册、登录、权限校验
    """,
    version="1.0.0",
    terms_of_service="https://www.university.edu.cn/terms",
    contact={
        "name": "计算机系教学组",
        "url": "https://cs.university.edu.cn",
        "email": "teacher@university.edu.cn",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# 3. 定义一个路径操作装饰器 (Path Operation Decorator)
# @app.get("/") 表示: 当客户端以 GET 方法访问网站根路径 "/" 时，触发下面的函数
@app.get(
    "/",
    summary="当前网站的根路径，网站的首页",
    description="用于监控服务器当前运行状态，返回 pong 字符串及服务器时间。",
    response_description="返回首页",
    tags=["首页"]
)
def read_root():
    """
    根路径测试接口
    返回一个简单的 JSON 字典
    """
    # 在 FastAPI 中，直接返回 Python 字典，FastAPI 会自动将其转换为 JSON 字符串返回给客户端！
    return {
        "code": 200,
        "message": "欢迎来到 FastAPI 的世界！",
        "author": "新生开发团队666666"
    }


@app.get(
    "/hello",
    summary="服务器健康检查接口",
    description="用于监控服务器当前运行状态，返回 pong 字符串及服务器时间。",
    response_description="返回健康检查状态 JSON",
    tags=["系统运维接口"]
)
def read_root():
    """
    根路径测试接口
    返回一个简单的 JSON 字典
    """
    # 在 FastAPI 中，直接返回 Python 字典，FastAPI 会自动将其转换为 JSON 字符串返回给客户端！
    return {
        "code": 200,
        "message": "欢迎来到 FastAPI 的世界！",
        "author": "新生开发团队666666"
    }


@app.get(
    "/msg",
    tags=["首页"]
)
def read_msg():
    """
    根路径测试接口
    返回一个简单的 JSON 字典
    """
    # 在 FastAPI 中，直接返回 Python 字典，FastAPI 会自动将其转换为 JSON 字符串返回给客户端！
    return {
        "code": 200,
        "message": "滚滚长江东逝水，浪花淘尽英雄。是非成败转头空。青山依旧在，几度夕阳红。白发渔樵江渚上，惯看秋月春风。一壶浊酒喜相逢。古今多少事，都付笑谈中。——调寄《临江仙》"
    }


np_data = np.loadtxt("heroes.csv", skiprows=1, encoding="utf-8", delimiter="\t", dtype="U")
# print(np_data)
heroes = [['1001', '宋江', '及时雨', '郓城', '总首领', '权谋、笼络人心', '三打祝家庄、招安', '梁山老大，后遭毒酒赐死'], ['1002', '卢俊义', '玉麒麟', '大名府', '马军五虎将', '棍棒天下无双', '活捉史文恭', '被高俅水银毒死'], ['1003', '吴用', '智多星', '郓城', '机密军师', '策划、计谋', '智取生辰纲、连环计', '自缢于宋江墓前'], ['1004', '公孙胜', '入云龙', '蓟州', '法师', '法术、五雷天罡法', '破高廉妖法', '征方腊前归隐修道'], ['1005', '关胜', '大刀', '河东解良', '马军五虎将', '青龙偃月刀', '大战林冲、秦明', '征方腊后病逝'], ['1006', '林冲', '豹子头', '东京', '马军五虎将', '林家枪法', '风雪山神庙', '征方腊后病逝（或中风）'], ['1007', '秦明', '霹雳火', '开州', '马军五虎将', '狼牙棒', '祝家庄之战', '征方腊时战死'], ['1008', '呼延灼', '双鞭', '开州', '马军五虎将', '双鞭打法', '连环马破梁山', '征方腊后授御营指挥使'], ['1009', '花荣', '小李广', '青州', '马军八骠骑', '神箭（百步穿杨）', '箭射吕方郭盛', '自缢于宋江墓前'], ['1010', '柴进', '小旋风', '沧州', '后勤/贵族', '仗义疏财', '暗助林冲、武松', '征方腊后辞官归农'], ['1011', '李应', '扑天雕', '郓州', '马军八骠骑', '飞刀', '祝家庄内应', '征方腊后返乡富豪'], ['1012', '朱仝', '美髯公', '郓城', '马军八骠骑', '关刀', '义释雷横', '征方腊后任保定府都统制'], ['1013', '鲁智深', '花和尚', '关西', '步军头领', '疯魔杖法', '拳打镇关西、倒拔垂杨柳', '征方腊后坐化于六和寺'], ['1014', '武松', '行者', '清河县', '步军头领', '鸳鸯脚、玉环步', '景阳冈打虎、斗杀西门庆', '征方腊失左臂，出家八十而终'], ['1015', '董平', '双枪将', '东平府', '马军五虎将', '双枪', '大战徐宁', '征方腊时战死'], ['1016', '张清', '没羽箭', '东昌府', '马军八骠骑', '飞石（暗器）', '飞石打伤梁山十五将', '征方腊时战死'], ['1017', '杨志', '青面兽', '东京', '马军八骠骑', '杨家枪法', '校场比武、押运花石纲', '征方腊时病逝'], ['1018', '徐宁', '金枪手', '东京', '马军八骠骑', '钩镰枪法', '破呼延灼连环马', '征方腊时中箭毒死'], ['1019', '索超', '急先锋', '大名府', '马军八骠骑', '开山斧', '北京城战杨志', '征方腊时战死'], ['1020', '戴宗', '神行太保', '江州', '情报/通讯', '神行术（日行八百里）', '传信梁山', '征方腊后辞官修仙'], ['1021', '刘唐', '赤发鬼', '东潞州', '步军头领', '朴刀', '智取生辰纲', '征方腊时战死'], ['1022', '李逵', '黑旋风', '沂州', '步军头领', '双板斧、嗜杀', '劫法场、沂岭杀四虎', '被宋江毒酒毒死'], ['1023', '史进', '九纹龙', '华阴县', '马军八骠骑', '棍术（王进所授）', '少华山落草', '征方腊时中箭战死'], ['1024', '穆弘', '没遮拦', '江州', '马军八骠骑', '拳脚', '揭阳镇称霸', '征方腊时病逝'], ['1025', '雷横', '插翅虎', '郓城', '步军头领', '朴刀、飞身扑跳', '私放晁盖', '征方腊时战死'], ['1026', '李俊', '混江龙', '江州', '水军头领', '水性、艨艟战法', '三败高俅水军', '征方腊后出海为暹罗王'], ['1027', '阮小二', '立地太岁', '石碣村', '水军头领', '水战', '劫生辰纲', '征方腊时战死'], ['1028', '张横', '船火儿', '江州', '水军头领', '水性', '劫杀客人', '征方腊时病逝'], ['1029', '阮小五', '短命二郎', '石碣村', '水军头领', '水战', '劫生辰纲', '征方腊时战死'], ['1030', '张顺', '浪里白条', '江州', '水军头领', '水下功夫（伏水七日）', '活捉高俅、凿沉海鳅船', '征方腊时涌金门被射死'], ['1031', '阮小七', '活阎罗', '石碣村', '水军头领', '水战', '穿龙袍嬉戏', '征方腊后贬为庶民'], ['1032', '杨雄', '病关索', '蓟州', '步军头领', '棍棒、朴刀', '杀妻潘巧云', '征方腊后病逝'], ['1033', '石秀', '拼命三郎', '建康', '步军头领', '朴刀、胆识', '劫法场救卢俊义', '征方腊时战死'], ['1034', '解珍', '两头蛇', '登州', '步军头领', '山猎、钢叉', '登州劫狱', '征方腊时坠崖战死'], ['1035', '解宝', '双尾蝎', '登州', '步军头领', '山猎、钢叉', '登州劫狱', '征方腊时坠崖战死']]
heroes = np_data.tolist()


@app.get("/hero/heroes")
def get_heroes():
    return {
        "code": 200,
        "msg": "获取到水浒传36天罡",
        "heroes": heroes
    }


@app.get("/hero/by_name/{name}")
def get_hero_by_name(name):
    """
    根据hero的name属性查询对应的数据
    :param name:    关键词name
    :return:        name对应的数据，如果不存在给出提示信息
    """
    for hero in heroes:
        if hero[1] == name:
            return hero
    return "查无此人"


@app.get("/hero/by_id/{id}")
def get_hero_by_id(name):
    """
    根据hero的name属性查询对应的数据
    :param name:    关键词name
    :return:        name对应的数据，如果不存在给出提示信息
    """
    for hero in heroes:
        if hero[1] == name:
            return hero
    return "查无此人"


@app.delete("/heroes/delete_by_id/{hero_id}")
def delete_hero_by_id(hero_id):
    print("delete_hero_by_id被访问啦啦啦")
    """
    通过hero的name查询并删除
    :param hero_id:
    :param name:
    :return:
    """
    for hero in heroes:
        if hero[0] == hero_id:
            heroes.remove(hero)
            return "通过id删除成功"
    return "查无此人"


@app.delete("/heroes/delete_by_name/{name}")
def delete_hero_by_name(name):
    print("delete_hero_by_name被访问啦啦啦")
    """
    通过hero的name查询并删除
    :param name:
    :return:
    """
    for hero in heroes:
        if hero[1] == name:
            heroes.remove(hero)
            return "通过name删除成功"
    return "查无此人"


@app.get("/hero/items/get_by_page")
def get_hero_items(page: int = 1, limit: int = 6):  # 方法形参中声明参数和类型，自动转换
    """
    分页查询
    :param page:
    :param limit:
    :return:
    """
    page = int(page)    # 显式转换类型
    start = (page-1) * limit
    end = page * limit
    return heroes[start: end]

# for hero in heroes:
#     if hero[1] == "燕青":
#         heroes.remove(hero)
# print(heroes)
# name = "zhangsan"
# age = 24
# print(f"姓名{name}, 年龄{age}")

str01 = "abcdefghijklmn"
print(str01.find("abc"))
print(str01.find("fgh"))
print(str01.find("fhfgh"))

str02 = "梁山老大，后遭毒酒赐死"
print(str02.find("老大"))
