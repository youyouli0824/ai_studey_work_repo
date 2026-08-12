# ==========================================
# 文件名: main.py
# 描述: 我们的第一个 FastAPI Web 应用程序
# Python 版本: 3.12.0
# FastAPI 版本: 0.138.0
# ==========================================
# 1、导入模块
from fastapi import FastAPI

book_sanguo=["第一回 宴桃园豪杰三结义 斩黄巾英雄首立功","第二回 张翼德怒鞭督邮 何国舅谋诛宦竖","第三回 议温明董卓叱丁原 馈金珠李肃说吕布","第四回 废汉帝陈留践位 谋董贼孟德献刀","第五回 发矫诏诸镇应曹公 破关兵三英战吕布","第六回 焚金阙董卓行凶 匿玉玺孙坚背约","第七回 袁绍磐河战公孙 孙坚跨江击刘表","第八回 王司徒巧使连环计 董太师大闹凤仪亭","第九回 除暴凶吕布助司徒 犯长安李傕听贾诩","第十回 勤王室马腾举义 报父仇曹操兴师"]
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
@app.get("/")
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


@app.get("/msg")
def read_msg():
    """
    根路径测试接口
    返回一个简单的 JSON 字典
    """
    # 在 FastAPI 中，直接返回 Python 字典，FastAPI 会自动将其转换为 JSON 字符串返回给客户端！
    return {
        "code":100,
        "msg":book_sanguo
    }


@app.delete("/dir")
def read_dir():
    """
    根路径测试接口
    返回一个简单的 JSON 字典
    """
    # 在 FastAPI 中，直接返回 Python 字典，FastAPI 会自动将其转换为 JSON 字符串返回给客户端！
    return {
        "code": 200,
        "message": ["第一回 宴桃园豪杰三结义 斩黄巾英雄首立功","第二回 张翼德怒鞭督邮 何国舅谋诛宦竖","第三回 议温明董卓叱丁原 馈金珠李肃说吕布","第四回 废汉帝陈留践位 谋董贼孟德献刀","第五回 发矫诏诸镇应曹公 破关兵三英战吕布","第六回 焚金阙董卓行凶 匿玉玺孙坚背约","第七回 袁绍磐河战公孙 孙坚跨江击刘表","第八回 王司徒巧使连环计 董太师大闹凤仪亭","第九回 除暴凶吕布助司徒 犯长安李傕听贾诩","第十回 勤王室马腾举义 报父仇曹操兴师"]
    }


@app.put("/modify")
def modify_data():
    """
    根路径测试接口
    返回一个简单的 JSON 字典
    """
    # 在 FastAPI 中，直接返回 Python 字典，FastAPI 会自动将其转换为 JSON 字符串返回给客户端！
    return {
        "code": 200,
        "message": ["第一回 宴桃园豪杰三结义 斩黄巾英雄首立功","第二回 张翼德怒鞭督邮 何国舅谋诛宦竖","第三回 议温明董卓叱丁原 馈金珠李肃说吕布","第四回 废汉帝陈留践位 谋董贼孟德献刀","第五回 发矫诏诸镇应曹公 破关兵三英战吕布","第六回 焚金阙董卓行凶 匿玉玺孙坚背约","第七回 袁绍磐河战公孙 孙坚跨江击刘表","第八回 王司徒巧使连环计 董太师大闹凤仪亭","第九回 除暴凶吕布助司徒 犯长安李傕听贾诩","第十回 勤王室马腾举义 报父仇曹操兴师"]
    }
