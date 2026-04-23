from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import shutil

app = FastAPI(
    title="個人作品集 API",
    description="極簡架構的後端 API 系統，支援作品資料的讀取與未來管理員系統的擴充。"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

FRONT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'front')
UPLOAD_DIR = os.path.join(FRONT_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True) # 若資料夾不存在則自動建立

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

@app.post("/api/upload", tags=["Upload"], dependencies=[Depends(verify_token)])
def upload_image(file: UploadFile = File(...)):
    try:
        # 核心修復：強制將路徑中的反斜線轉為正斜線，並透過 os.path.basename 只擷取「檔案名稱」
        # 這能把 "C:\Users\...\image.png" 或 "C:\fakepath\image.png" 乾淨地變成 "image.png"
        safe_filename = os.path.basename(file.filename.replace("\\", "/"))
        
        # 組合正確的存檔路徑
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        print(f"--- 檔案上傳偵錯 ---")
        print(f"安全過濾後的檔名: {safe_filename}")
        print(f"實際寫入路徑: {os.path.abspath(file_path)}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 回傳乾淨的相對路徑給前端
        return {"status": "success", "image_url": f"uploads/{safe_filename}"}
    except Exception as e:
        print(f"上傳發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")
# ↑↑↑ ➕ 任務 5-4 修正區塊結束 ➕ ↑↑↑

#取得內容
@app.get("/api/projects", tags=["Projects"])
def get_projects():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取資料庫失敗: {str(e)}")
    


#新增作品 API (Create)
@app.post("/api/projects", tags=["Projects"], dependencies=[Depends(verify_token)])
def create_project(project: ProjectData):
    try:
        # 讀取現有資料庫
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 將前端傳來的資料轉成字典並加入陣列
        data.append(project.model_dump())
        
        # 將更新後的陣列寫回 data.json
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return {"status": "success", "message": "作品新增成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"寫入資料庫失敗: {str(e)}")

#刪除作品 API (Delete)
@app.delete("/api/projects/{project_id}", tags=["Projects"], dependencies=[Depends(verify_token)])
def delete_project(project_id: int):
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 驗證索引值是否合法，防堵越界錯誤
        if project_id < 0 or project_id >= len(data):
            raise HTTPException(status_code=404, detail="找不到該作品")
            
        # 移除指定索引的資料
        deleted_project = data.pop(project_id)
        
        # 寫回資料庫
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return {"status": "success", "message": f"成功刪除作品: {deleted_project['title']}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新資料庫失敗: {str(e)}")