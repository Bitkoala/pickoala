# CORS 配置指南 (Cross-Origin Resource Sharing)

## 简介
如果您的视频需要在其他网站（如您的博客、论坛）通过高级播放器（如 Video.js）播放，或者遇到跨域错误（CORS Error），则需要修改后端配置以允许这些域名的访问。

**注意**：标准 HTML5 `<video>` 标签直接引用直链通常不受 CORS 限制，仅在使用 JS 请求资源时才需要配置。

## 配置步骤

### 1. 修改后端配置文件
打开文件：`backend/app/main.py`

### 2. 定位 CORS 中间件配置
找到大约第 86 行的 `CORSMiddleware` 配置部分：

```python
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # 默认配置（仅允许本机或调试模式下所有）
    allow_origins=["*"] if settings.app_debug else [settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 添加允许的域名
修改 `allow_origins` 列表，将您需要引用的外部网站域名添加进去。

**示例代码**：

```python
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.app_url,           # 保持原有的 APP_URL
        "https://blog.yourdomain.com",   # 添加您的博客域名
        "https://www.another-site.com",  # 其他允许的网站
        # "http://localhost:8080",       # 本地调试端口
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. 重启服务
修改完成后，需要重启后端服务使配置生效。

*   **Docker 部署**：`docker-compose restart backend`
*   **手动部署**：重新运行 `python -m app.main` 或重启 systemd 服务。

## 常见问题

*   **为什么要限制域名？**
    限制允许的域名可以防止您的资源被未经授权的恶意网站盗用（例如通过 JS 脚本偷取您的 API 数据）。
*   **不想限制怎么办？**
    如果您主要作为公开图床/视频床使用，可以将 `allow_origins` 设置为 `["*"]`，这样允许所有网站跨域访问，但请注意这也意味着失去了基于 CORS 的防盗链保护。
