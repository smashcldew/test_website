# 作品集系統

本專案是一個整合多項雲端微服務的高可用性作品集網站。

## 系統架構
本系統採用前後端分離架構，實現了 100% 的雲端資料持久化：
- **Frontend**: 部署於 **GitHub Pages**。
- **Backend**: 部署於 **Render**，採用 **FastAPI** 構建 RESTful API。
- **Database**: 使用 **MongoDB Atlas**，確保作品資料永不遺失。
- **Image Hosting**: 整合 **ImgBB API**，實現自動化雲端圖床管理。

## 技術棧
- **語言**: Python, JavaScript
- **框架**: FastAPI, Pydantic
- **維運**: GitHub Actions部署前端網頁, Cron-job持續發出GET請求讓Render伺服器不會shutdown, 環境變數加密.env使重要的帳密不會洩漏

## 安全部分
本專案已落實資安防護，所有機密金鑰（MongoDB 憑證、ImgBB API Key）均透過伺服器環境變數管理，未在原始碼中洩露。