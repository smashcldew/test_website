# 作品集系統

本專案是一個以 Cloudflare 全端部署的個人作品集與後台管理網站。

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
