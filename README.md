<p align="center">
  <img src="pickoala/public/logo.png" alt="PicKoala Logo" width="120" height="120">
</p>

# PicKoala - 简洁优雅的图床与文件存储系统

**演示站点**: [https://pickoala.com](https://pickoala.com)

<p align="center">
  <img src="https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat-square&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue.js-35495E?style=flat-square&logo=vuedotjs&logoColor=4FC08D" alt="Vue">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License">
</p>

**PicKoala (考拉云图)** 是一个基于 **FastAPI + Vue 3** 构建的现代化媒体托管平台。它不仅是一个图床，更支持视频托管、文件快传以及 AI 智能增强，提供极佳的用户体验和强大的管理功能。

## 🙏 致谢与二次开发说明

本项目基于 [Forimage第一版](https://github.com/globeglobefish/forimage) 二次开发，进行了深度的 UI 重构、功能增强和商业化适配。

1.  **全新 UI/UX 重构**
    - 采用现代化设计语言，增加极光/深色模式切换，全面优化移动端体验。

2.  **AI 智能增强 (New)**
    - 集成 **Google Gemini AI**，实现上传图片自动生成标签和描述，大幅提升搜索与管理效率。

3.  **功能全面增强**
    - **视频托管**: 新增视频上传、播放、视频集管理功能。
    - **文件快传**: 新增通用文件上传，支持过期时间、提取码、下载限制。
    - **原生 OAuth 2.0**: 移除了复杂的外部身份平台依赖，直接内置了 Google, Linux.do, GitHub 等主流原生 OAuth 登录支持。

4.  **商业化与安全适配**
    - **会员体系**: 引入 Guest/User/VIP 三级用户体系，支持权益差异化配置。
    - **支付集成**: 内置 Stripe、支付宝、易支付（兼容接口）支付接口，支持自动开通会员。

##  核心特性

### 🤖 AI 智能分析 (New)
- **自动标签**: 利用 Gemini AI 图像识别能力，为每一张图片自动生成多维度的标签。
- **内容描述**: 自动生成准确的图片文字描述，便于索引和辅助阅读。
- **状态监控**: 后端异步处理 AI 分析任务，前端实时显示分析进度。

### 📦 大文件与断点续传
- **超大文件支持**: 支持超过 2GB 的文件/视频上传（需 Nginx 配置配合）。
- **断点续传**: 网络中断后可自动从断点处继续上传，无需重新开始。
- **自动分片**: 前端自动分片上传，后端流式合并，极低内存占用，确保服务器稳定。

###  图片托管
- **多格式支持**: 支持 JPG, PNG, GIF, WEBP, SVG 等常见格式。
- **全新水印系统**: 支持文字/图片双水印模式，支持 9 宫格位置自定义、透明度/大小调节。水印配置支持浏览器持久化存储。
- **智能相册**: 拖拽上传、批量管理、相册分类。
- **安全审核**: 集成腾讯云/阿里云内容安全审核，自动拦截违规图片。

###  视频托管
- **视频集管理**: 类似相册的文件夹管理体验，支持创建、编辑、删除视频集。
- **流畅播放**: 内置响应式视频播放器，支持 MP4, WebM, MOV 等格式。
- **独立限流**: 针对视频上传单独配置频率和大小限制（Guest/User/VIP）。

###  文件快传
- **临时分享**: 支持设置过期时间（1天/7天/30天等）。
- **访问控制**: 支持设置提取码（密码保护）和下载次数限制。
- **多格式**: 支持压缩包、文档、设计稿等任意文件格式。

###  系统功能
- **多存储策略**: 支持 本地存储, AWS S3, 阿里云 OSS, 腾讯云 COS, Cloudflare R2。
- **自动化 CDN 刷新**: 支持 **Cloudflare 自动清理缓存 (API Purge)**。当删除图片时，系统会自动清理边缘节点的缓存。
- **用户体系**: 完善的 Guest / User / VIP 三级用户体系，权益可配置。
- **原生登录**: 内置 Google, Linux.do, GitHub 登录。
- **支付系统**: 集成 Stripe / 支付宝 / 易支付。**支付宝支持“当面付”，支持移动端自动唤起**。
- **性能优化**: 支持 Gzip 压缩、WebP 自动转换，秒开体验。
- **管理后台**: 强大的仪表盘，支持 AI 密钥管理、系统配置、用户管理、文件/视频管理。
- **国际化**: 原生支持 中文 (简/繁) 和 English。

##  技术栈

| 模块 | 技术 | 说明 |
|------|----------|------|
| **后端** | **FastAPI** | Python 3.10+ 高性能异步框架 |
| **AI 引擎** | **Google Gemini** | 智能图像识别与语义分析 |
| **数据库** | **MySQL 8** | 数据持久化 |
| **缓存** | **Redis** | 频率限制、任务队列 (Celery-less) |
| **前端** | **Vue 3** | Composition API + Vite |
| **UI 框架** | **Element Plus** | 现代化 UI 组件库 |

## 📚 部署文档

我们提供详细的部署指南：

- [**1Panel 部署指南**](1PANEL_DEPLOY.md) (推荐) - 基于 Docker 的现代化部署。
- [**宝塔面板部署指南**](BAOTA_DEPLOY.md) - 适合传统运维习惯的用户。

##  快速开始 (Docker)

推荐使用 Docker Compose 进行一键部署。

### 1. 获取代码
```bash
git clone https://github.com/Bitkoala/PicPanda.git
cd PicPanda
```

### 2. 启动服务

访问 `http://localhost:3000` 即可看到全新的 PicKoala 界面。

> [!TIP]
> 默认管理员账号请查看数据库或使用注册的第一个账号（需在数据库修改 role 为 admin）。

##  许可证

本项目采用 [MIT License](LICENSE) 开源。

---
Copyright (c) 2026 PicKoala Team