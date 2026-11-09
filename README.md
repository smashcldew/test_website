# 作品集系統

本專案是一個以 Cloudflare 全端部署的個人作品集與後台管理網站。

| 項目 | 位置 |
| --- | --- |
| 前端網站 | <https://test-website-386.pages.dev> |
| 後端 API | <https://blog-api.cldew20070210.workers.dev> |

## 系統架構
- **Frontend**: 靜態網頁 `front/`，部署於 **Cloudflare Pages**。
- **Backend**: 使用 **Cloudflare Workers** 撰寫 RESTful API（`worker/src/index.js`），取代原本 Render 上的 FastAPI。
- **Database**: 使用 **Cloudflare D1**（SQLite），表結構見 `worker/schema.sql`。
- **Image Hosting**: 沿用 **ImgBB API**（Cloudflare R2 需綁定付款資訊，故未採用）。

## API 端點
| Method | Path | 說明 | 需要登入 |
| --- | --- | --- | --- |
| GET | `/api/projects` | 取得所有作品 | 否 |
| POST | `/api/login` | 管理員登入，回傳 token | 否 |
| POST | `/api/projects` | 新增作品 | 是 |
| DELETE | `/api/projects/:id` | 刪除作品 | 是 |
| POST | `/api/upload` | 上傳圖片到 ImgBB | 是 |

## 部署步驟

### 1. 建立 D1 資料庫並套用表結構
```bash
cd worker
npm install
npx wrangler d1 create blog_backend        # 把輸出的 database_id 填入 wrangler.toml
npx wrangler d1 execute blog_backend --remote --file=schema.sql
```

### 2. 設定機密變數（不會寫入程式碼）
```bash
npx wrangler secret put ADMIN_USER
npx wrangler secret put ADMIN_PASSWORD
npx wrangler secret put SECRET_TOKEN
npx wrangler secret put IMGBB_API_KEY
```

### 3. 部署 Worker
```bash
npx wrangler deploy
```
把輸出的 `*.workers.dev` 網址填入 `front/JS/config.js` 的 `API_BASE`，並把 Pages 網域填入 `wrangler.toml` 的 `ALLOWED_ORIGIN`。

### 4. 部署前端
到 Cloudflare Dashboard 建立 Pages 專案並連接此 GitHub repo：
- Framework preset：None
- Build command：（留空）
- Build output directory：`front`

## 從舊的 MongoDB 搬移資料
```bash
cd worker/scripts
export MONGO_URI="mongodb+srv://..."
python mongo_to_d1.py > migrate.sql
cd ..
npx wrangler d1 execute blog_backend --remote --file=migrate.sql
```
確認資料無誤後，即可停用 Render 服務與 cron-job 的保持喚醒排程，並至 MongoDB Atlas 關閉叢集。

## 安全部分
所有機密（管理員帳密、登入 token、ImgBB API Key）都以 Wrangler secrets 管理，未寫入原始碼。

## 版本歷史

### v2.0 — Cloudflare 全端架構（2026-11）

將原本分散於三個服務商的架構整合至 Cloudflare。後端由 Python 改寫為 JavaScript，資料庫由文件型改為關聯型。

| 層級 | v1.0 | v2.0 |
| --- | --- | --- |
| 前端 | GitHub Pages | Cloudflare Pages |
| 後端 | Render（Python / FastAPI） | Cloudflare Workers（JavaScript） |
| 資料庫 | MongoDB Atlas | Cloudflare D1（SQLite） |
| 圖片儲存 | ImgBB API | ImgBB API（沿用） |
| 保持喚醒 | cron-job 定時發送 GET | 不需要 |

主要變更：

- Render 免費方案閒置後會休眠，首次請求需數十秒冷啟動，原先以 cron-job 定時發送 GET 維持喚醒。Workers 無休眠機制，此繞道做法已移除。
- Workers 執行於 V8 isolate，無法使用 pymongo 驅動，因此資料庫一併改為 D1，並撰寫 `worker/scripts/mongo_to_d1.py` 搬移既有資料。
- 刪除作品原先以陣列索引定位，多人同時操作時會刪錯資料；改用 D1 後以主鍵 `id` 定位，前端同步調整。
- 機密由 `.env` + `python-dotenv` 改為 Wrangler secrets，值儲存於 Cloudflare 端。
- 原計畫以 Cloudflare R2 取代 ImgBB，因 R2 需綁定付款資訊而維持原方案，僅將 API Key 改為 secret 管理。

### v1.0 — 多雲微服務架構（2026-03 ~ 2026-04）

初版的前後端分離架構，實現雲端資料持久化。

- **Frontend**: 部署於 GitHub Pages，以 GitHub Actions 自動部署。
- **Backend**: 部署於 Render，採用 FastAPI 構建 RESTful API。
- **Database**: 使用 MongoDB Atlas。
- **Image Hosting**: 整合 ImgBB API，實現自動化雲端圖床管理。
- **維運**: 以 cron-job 持續發出 GET 請求，避免 Render 伺服器休眠；機密以 `.env` 管理。

v1.0 的程式碼保存於 git 歷史中，最後狀態見 commit `8fb5db2`。
