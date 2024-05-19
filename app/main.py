from fastapi import FastAPI, Body, HTTPException, Depends

from auth.jwt_handler import signJWT
from auth.jwt_bearer import jwtBearer
from db import database, User, ToDo
from models import ToDoSchema, UserSchema
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="RestAPI")

async def check_user(data: UserSchema):
    if not database.is_connected:
        await database.connect()
    users = await User.objects.all()
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False

@app.get("/")
async def read_root():
    return await ToDo.objects.all()

@app.get("/users/", tags=["users"])
async def read_user(id: int):
    if not database.is_connected:
        await database.connect()
    return await User.objects.get(id=id)

@app.get("/todo", tags=["todo"])
async def read_todo(user_id: int):
    if not database.is_connected:
        await database.connect()
    return await ToDo.objects.all(user_id=user_id)

@app.post("/users/signup", tags=["users"])
async def create_user(user: UserSchema = Body(default=None)):
    if not database.is_connected:
        await database.connect()
    await User.objects.create(
        email=user.email,
        password=user.password
    )
    return signJWT(user.email)

@app.post("/users/login", tags=["users"])
async def user_login(user: UserSchema = Body(default=None)):
    if await check_user(user):
        return signJWT(user.email)
    raise HTTPException(status_code=404, detail=f"{user.email} não encontrado")

@app.post("/todo", tags=["todo"]) 
async def create_todo(todo: ToDoSchema):
    if not database.is_connected:
        await database.connect()
    return await ToDo.objects.create(
        title=todo.title,
        content=todo.content
    )

@app.put("/todo/update/{id}", tags=["todo"])
async def update_todo(id: int, todo: ToDoSchema):
    if not database.is_connected:
        await database.connect()
    try:
        task = await ToDo.objects.get_or_none(id=id)
        if task:
            task.title = todo.title
            task.content = todo.content
            await task.update()
            return {"message": "Task updated successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Task with id {id} not found")
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=404, detail=f"Task with id {id} not found")

@app.delete("/todo/delete/{id}", tags=["todo"])
async def delete_todo(id: int):
    if not database.is_connected:
        await database.connect()
    return await ToDo.objects.delete(id=id)

@app.delete("/users/delete/{id}", tags=["users"], dependencies=[Depends(jwtBearer())])
async def delete_user(id: int):
    if not database.is_connected:
        await database.connect()
    return await User.objects.delete(id=id)

@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()

@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
