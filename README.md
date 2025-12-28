<p align="center">
  <img src="/frontend/public/logo.png" alt="PicKoala Logo" width="120" height="120">
</p>

# PicKoala - 简洁优雅的图床与文件存储系统

<p align="center">
  <img src="https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat-square&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue.js-35495E?style=flat-square&logo=vuedotjs&logoColor=4FC08D" alt="Vue">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License">
</p>

**PicKoala** 是一个基于 **FastAPI + Vue 3** 构建的现代化媒体托管平台。它不仅是一个图床，更支持视频托管和文件快传，提供极佳的用户体验和强大的管理功能。

## 🙏 致谢与二次开发说明

本项目基于 [Forimage](https://github.com/globeglobefish/forimage) 二次开发，进行了全面的 UI 重构、功能增强和商业化适配。主要改进包括：

1.  **全新 UI/UX 重构**
    - 采用现代化设计语言，增加极光模式前端界面。

2.  **功能全面增强**
    - **视频托管**: 新增视频上传、播放、视频集管理功能。
    - **文件快传**: 新增通用文件上传，支持过期时间、提取码、下载限制。

3.  **商业化与安全适配**
    - **会员体系**: 引入 Guest/User/VIP 三级用户体系，支持权益差异化配置。
    - **支付集成**: 内置 Stripe 和 支付宝 支付接口，支持自动开通会员。

##  核心特性

### 📦 大文件与断点续传 (New)
- **超大文件支持**: 支持超过 2GB 的文件/视频上传（需 Nginx 配置配合）。
- **断点续传**: 网络中断后可自动从断点处继续上传，无需重新开始。
- **自动分片**: 前端自动分片上传，后端流式合并，极低内存占用，确保服务器稳定。

###  图片托管
- **多格式支持**: 支持 JPG, PNG, GIF, WEBP, SVG 等常见格式。
- **智能相册**: 拖拽上传、批量管理、相册分类。
- **图片处理**: 支持压缩、水印（可配置）、格式转换。
- **安全审核**: 集成腾讯云/阿里云内容安全审核，自动拦截违规图片。

###  视频托管 (New)
- **视频集管理**: 类似相册的文件夹管理体验，支持创建、编辑、删除视频集。
- **流畅播放**: 内置响应式视频播放器，支持 MP4, WebM, MOV 等格式。
- **独立限流**: 针对视频上传单独配置频率和大小限制（Guest/User/VIP）。

###  文件快传 (New)
- **临时分享**: 支持设置过期时间（1天/7天/30天等）。
- **访问控制**: 支持设置提取码（密码保护）和下载次数限制。
- **多格式**: 支持压缩包、文档、设计稿等任意文件格式。

###  系统功能
- **多存储策略**: 支持 本地存储, AWS S3, 阿里云 OSS, 腾讯云 COS, Cloudflare R2。
- **用户体系**: 完善的 Guest / User / VIP 三级用户体系，权益可配置。
- **支付系统**: 集成 Stripe / 支付宝（ 需自行申请接口），支持会员订阅。
- **管理后台**: 强大的仪表盘，支持系统配置、用户管理、文件管理、公告发布。
- **国际化**: 原生支持 中文 (简/繁) 和 English。

##  技术栈

| 模块 | 技术 | 说明 |
|------|----------|------|
| **后端** | **FastAPI** | Python 3.10+ 高性能异步框架 |
| **数据库** | **MySQL 8** | 数据持久化 |
| **缓存** | **Redis** | 频率限制、会话缓存、任务队列 |
| **前端** | **Vue 3** | Composition API, Setup Script |
| **UI 框架** | **Element Plus** | 现代化 UI 组件库 |
| **构建工具** | **Vite** | 极速冷启动与热更新 |
| **部署** | **Docker** | 一键容器化部署 |

## 📚 部署文档

我们提供针对主流面板的详细部署指南：

- [**1Panel 部署指南**](1PANEL_DEPLOY.md) (推荐) - 基于 Docker 的现代化部署。
- [**宝塔面板部署指南**](BAOTA_DEPLOY.md) - 适合传统运维习惯的用户。

##  快速开始 (Docker)

推荐使用 Docker Compose 进行一键部署。

### 1. 获取代码
```bash
git clone https://github.com/YourRepo/PicKoala.git
cd PicKoala
```

### 2. 启动服务
```bash
docker-compose up -d
```

访问 `http://localhost:3000` 即可看到全新的 PicKoala 界面。

> 默认管理员账号请查看数据库或使用注册的第一个账号（需在数据库修改 role 为 admin）。

##  配置说明

系统配置文件主要位于数据库 `system_settings` 表中，大部分配置（如站点名称、存储设置、邮件服务）均可直接在 **管理后台 -> 系统设置** 中实时修改，无需重启服务。

- **环境变量**: 只有数据库连接等核心配置在 `backend/.env` 或 `docker-compose.yml` 中。
- **首页文案**: 首页的特性介绍和对比表格内容可在后台动态配置。

##  许可证

本项目采用 [MIT License](LICENSE) 开源。

---
Copyright (c) 2025 PicKoala Team