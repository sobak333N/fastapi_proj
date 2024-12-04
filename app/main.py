from fastapi import FastAPI

# Создаем экземпляр FastAPI
app = FastAPI()

# Определяем эндпоинты (routes)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: dict):
    return {"message": "Item created", "item": item}
