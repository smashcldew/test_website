from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
#import requests
import pymongo
from bson import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

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

MONGO_URI = os.getenv("MONGO_URI")
#IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "fallback-token-for-dev")

client = pymongo.MongoClient(MONGO_URI)
db = client["portfolio_db"] 
collection = db["projects"] 

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="access denied")

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
    return {"message": "server is running!"}

@app.post("/api/login", tags=["Admin"])
def login(request: LoginRequest):
    if request.username == ADMIN_USER and request.password == ADMIN_PASSWORD:
        return {
            "status": "success",
            "message": "login successful",
            "token": SECRET_TOKEN
        }
    else:
        raise HTTPException(status_code=401, detail="wrong username or password")

# @app.post("/api/upload", tags=["Upload"], dependencies=[Depends(verify_token)])
# def upload_image(file: UploadFile = File(...)):
#     try:
#         image_bytes = file.file.read()
#         image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
#         response = requests.post(
#             "https://api.imgbb.com/1/upload",
#             data={
#                 "key": IMGBB_API_KEY,
#                 "image": image_b64
#             }
#         )
        
#         if response.status_code == 200:
#             result = response.json()
#             cloud_url = result["data"]["url"] 
            
#             print(f"--- image upload ---")
#             print(f"cloud_address: {cloud_url}")
            
#             return {"status": "success", "image_url": cloud_url}
#         else:
#             print(f"ImgBB denied request: {response.text}")
#             raise HTTPException(status_code=500, detail="image upload failed: " + response.text)
            
#     except Exception as e:
#         print(f"error upload failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"upload failed: {str(e)}")

@app.post("/api/upload", tags=["Upload"], dependencies=[Depends(verify_token)])
def upload_image(file: UploadFile = File(...)):
    try:
        # 讀取圖片的二進位資料
        image_bytes = file.file.read()

        # 將二進位資料轉換為 base64 字串
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        # 取得檔案類型 (例如: image/jpeg)，若無則預設為 image/jpeg
        content_type = file.content_type or "image/jpeg"

        # 組合成 Data URL 格式
        data_url = f"data:{content_type};base64,{image_b64}"

        print(f"--- image processed to base64 ---")

        # 直接回傳轉換後的 Data URL 給前端
        return {"status": "success", "image_url": data_url}

    except Exception as e:
        print(f"error process failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"image process failed: {str(e)}")

#get
@app.get("/api/projects", tags=["Projects"])
def get_projects():
    try:
        projects = list(collection.find())

        for p in projects:
            p["_id"] = str(p["_id"])
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB load failed: {str(e)}")
    
#add
@app.post("/api/projects", tags=["Projects"], dependencies=[Depends(verify_token)])
def create_project(project: ProjectData):
    try:
        collection.insert_one(project.model_dump())

        return {"status": "success", "message": "create success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"cloud insert failed: {str(e)}")

#delete
@app.delete("/api/projects/{project_id}", tags=["Projects"], dependencies=[Depends(verify_token)])
def delete_project(project_id: int):
    try:
        projects = list(collection.find())

        if project_id < 0 or project_id >= len(projects):
            raise HTTPException(status_code=404, detail="not found")
        
        target_id = projects[project_id]["_id"]
        collection.delete_one({"_id": target_id})
        
        return {"status": "success", "message": "delete success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"delete failed: {str(e)}")