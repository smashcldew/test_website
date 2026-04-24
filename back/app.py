from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import requests
import pymongo
from bson import ObjectId

app = FastAPI(
    title="個人作品集 API",
    description=""
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = "mongodb://cldew:google123@ac-bv30w7i-shard-00-00.nomm389.mongodb.net:27017,ac-bv30w7i-shard-00-01.nomm389.mongodb.net:27017,ac-bv30w7i-shard-00-02.nomm389.mongodb.net:27017/?ssl=true&replicaSet=atlas-86rjao-shard-0&authSource=admin&appName=Website"
client = pymongo.MongoClient(MONGO_URI)
db = client["portfolio_db"] # 資料庫名稱
collection = db["projects"] # 集合名稱 (類似資料表)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # 模擬驗證我們在 login API 發放的 token
    if credentials.credentials != "fake-jwt-token-for-now":
        raise HTTPException(status_code=401, detail="權限不足：無效或遺失的 Token")

class LoginRequest(BaseModel):
    username: str
    password: str

class ProjectData(BaseModel):
    title: str
    image: str
    content: str
    date: str

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "歡迎來到個人作品集 API 伺服器！請前往 /docs 查看 API 互動文件。"}

ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin123"

@app.post("/api/login", tags=["Admin"])
def login(request: LoginRequest):
    # 註解：驗證帳號密碼是否正確
    if request.username == ADMIN_USER and request.password == ADMIN_PASSWORD:
        return {
            "status": "success",
            "message": "登入成功",
            "token": "fake-jwt-token-for-now" # 註解：先回傳虛擬 Token 供前端測試邏輯
        }
    else:
        # 註解：若錯誤，回傳 401 Unauthorized 狀態碼
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

IMGBB_API_KEY = "42bb24d3a8a0a9a33eb55ea6f030d459"

@app.post("/api/upload", tags=["Upload"], dependencies=[Depends(verify_token)])
def upload_image(file: UploadFile = File(...)):
    try:
        # 步驟 1：將圖片讀取並轉為 Base64 編碼，符合 ImgBB API 的傳輸規範
        image_bytes = file.file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # 步驟 2：向 ImgBB 發送 HTTP POST 請求
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": IMGBB_API_KEY,
                "image": image_b64
            }
        )
        
        # 步驟 3：解析回傳結果
        if response.status_code == 200:
            result = response.json()
            cloud_url = result["data"]["url"] # 取得 ImgBB 生成的永久雲端網址
            
            print(f"--- 圖片上傳微服務成功 ---")
            print(f"雲端網址: {cloud_url}")
            
            # 將完整的 https 網址回傳給前端
            return {"status": "success", "image_url": cloud_url}
        else:
            print(f"ImgBB 拒絕請求: {response.text}")
            raise HTTPException(status_code=500, detail="圖片上傳至雲端圖床失敗")
            
    except Exception as e:
        print(f"上傳發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")

#取得內容
@app.get("/api/projects", tags=["Projects"])
def get_projects():
    try:
        projects = list(collection.find())
        # 將 MongoDB 的 ObjectId 轉換為字串，否則 JSON 會報錯
        for p in projects:
            p["_id"] = str(p["_id"])
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料庫讀取失敗: {str(e)}")
    


#新增作品 API (Create)
@app.post("/api/projects", tags=["Projects"], dependencies=[Depends(verify_token)])
def create_project(project: ProjectData):
    try:
        # 直接插入雲端資料庫，不再需要讀寫 data.json
        collection.insert_one(project.model_dump())
        return {"status": "success", "message": "作品成功存入雲端資料庫"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"雲端寫入失敗: {str(e)}")

#刪除作品 API (Delete)
@app.delete("/api/projects/{project_id}", tags=["Projects"], dependencies=[Depends(verify_token)])
def delete_project(project_id: int):
    try:
        # 由於前端傳來的是索引值 (Index)，我們必須先找出對應的項目
        projects = list(collection.find())
        if project_id < 0 or project_id >= len(projects):
            raise HTTPException(status_code=404, detail="找不到該作品")
        
        target_id = projects[project_id]["_id"]
        collection.delete_one({"_id": target_id})
        
        return {"status": "success", "message": "已從雲端資料庫刪除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除失敗: {str(e)}")