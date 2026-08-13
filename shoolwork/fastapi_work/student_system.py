from pathlib import Path

from fastapi import FastAPI, HTTPException
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

student_data = pd.read_csv(
    "student_data.csv",
    encoding="utf-8-sig",
)
dict_student_data=student_data.to_dict(orient="records")
app = FastAPI(title="学生信息管理")


class StudentIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    name: str
    email: str = Field(alias="e-mail")
    phone_number: str
    address: str
    info: str


@app.get(
    "/students",
    summary="获取所有学生列表",
)
def get_all_students():
    return dict_student_data


@app.post(
    "/students/add",
    status_code=201,
    summary="新增学生信息",
)
def add_student(student: StudentIn):
    if student.id is None:
        student.id = max(s["id"] for s in dict_student_data) + 1
    elif any(s["id"] == student.id for s in dict_student_data):
        raise HTTPException(status_code=400, detail=f"id {student.id} 已存在")

    new_student = student.model_dump(by_alias=True)
    dict_student_data.append(new_student)
    return {"msg": "新增成功", "student": new_student}


@app.get(
    "/students/{student_id}",
    summary="根据id查询学生信息"
)
def get_student_by_id(student_id:int):
    for student in dict_student_data:
        if student["id"]==student_id:
            return student
    return "查无此人"


@app.get(
    "/students/search/filter",
    summary="根据地址筛选学生信息"
)
def search_students_by_address(address: str):
    students = []
    for student in dict_student_data:
        if student["address"] == address:
            students.append(student)
    return students if students else "没有符合条件的学生"


@app.get(
    "/students/find/{info}",
    summary="根据特长模糊查询学生信息"
)
def find_students_by_info(info:str):
    students=[]
    for student in dict_student_data:
        if info in student["info"]:
            students.append(student)
    return students if students else "没有符合条件的学生"

@app.delete(
    "/students",
    summary="删除学生信息（可按 id / 名字 / info 模糊删除）",
)
def delete_students(
    id: int | None = None,
    name: str | None = None,
    info: str | None = None,
):
    if id is None and name is None and info is None:
        raise HTTPException(status_code=400, detail="请至少提供一个删除条件：id / name / info")

    deleted = [
        s for s in dict_student_data
        if (id is not None and s["id"] == id)
        or (name is not None and s["name"] == name)
        or (info is not None and info in s["info"])
    ]
    if not deleted:
        return {"msg": "没有符合条件的学生", "deleted": []}

    for s in deleted:
        dict_student_data.remove(s)
    return {"msg": f"已删除 {len(deleted)} 条记录", "deleted": deleted}


@app.put(
    "/students/{student_id}",
    summary="修改学生信息",
)
def update_student(student_id: int, student: dict):
    for s in dict_student_data:
        if s["id"] == student_id:
            s["name"] = student.get("name", s["name"])
            s["e-mail"] = student.get("e-mail", s["e-mail"])
            s["phone_number"] = student.get("phone_number", s["phone_number"])
            s["address"] = student.get("address", s["address"])
            s["info"] = student.get("info", s["info"])
            return {"msg": "修改成功", "student": s}
    return "查无此人"


