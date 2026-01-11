# 1Panel 部署指南 (容器化部署)

1Panel 是一个现代化的运维面板，它的核心哲学是 **Docker 容器化**。
虽然你可以像宝塔那样手动跑命令部署 (Systemd)，但 **强烈建议使用 Docker**，这会让你的维护工作减少 90%。

---

## 方式一：Docker 一键部署 (推荐 🔥)

这种方式最简单，不需要配置环境，不需要管依赖冲突。

### 1. 准备代码 (关键步骤)
1. 确保 1Panel 已安装 **OpenResty**。
2. **上传代码**：请将本地项目文件夹完整上传到服务器的 `/opt/pickoala` 目录。
   *   **必须包含**：`backend` (后端源码), `database` (初始化SQL), `docker-compose.yml`。
   *   *确保路径存在：`/opt/pickoala/backend/Dockerfile`*。

### 2. 部署后端 (Service)
1. 在 1Panel 面板 -> **容器** -> **编排 (Compose)** -> **创建编排**。
2. **名称**：填 `pickoala`。
3. **内容**：
    *   **选项 A (推荐 - 公共数据库)**：复制 `docker-compose.yml`。
        *   默认配置已设为连接宿主机的 MySQL（通过 `host.docker.internal`）。
        *   **注意**：你需要在 1Panel 数据库管理中先创建 `pickoala` 数据库，并导入 `init.sql`。
    *   **选项 B (独立数据库)**：复制 `docker-compose.standalone.yml`（需重命名或手动指定）。
        *   这个配置会启动一个独立的 MySQL 容器，数据完全隔离。
        *   这种方式会自动初始化数据库，无需手动导入 SQL。
    *   *提示：为了匹配此处的路径，你可能需要简单修改 `docker-compose.yml` 里的构建路径，或者直接使用绝对路径 `. context: /opt/pickoala/backend`*。
    *   **环境变量**：根据选择修改 `DATABASE_URL` (选项 A 需填写真实的面板数据库密码)。
4. 点击 **确认**。
    *   1Panel 会自动构建镜像并启动服务。
    *   等待状态变为绿色的 "已启动"。

### 3. 初始化数据库
如果是第一次用 Docker 启动，MySQL 容器启动时会自动读取 `database/init.sql` 进行初始化。
**重要**：支付、会员等所有核心数据表会在首次启动时**自动创建**，无需手动运行脚本。

### 4. 部署前端 (Web)
1. 本地执行 `npm run build` 打包。
2. 1Panel 面板 -> **网站** -> **创建网站** -> **静态网站**。
3. **主域名**：填你的域名。
4. **代号**：pickoala-web。
5. 创建成功后，进入网站目录，把 `dist` 文件夹里的内容上传进去。

### 5. 配置反向代理 (连接前后端)
在网站设置 -> **反向代理**：

**规则 1 (API)**：
*   **名字**：API
*   **路径**：`/api`
*   **代理地址**：`http://127.0.0.1:8000` (如果 Docker 改了端口这里对应改)

**规则 2 (图片资源)**：
*   **名字**：Uploads
*   **路径**：`/uploads`
*   **代理地址**：`http://127.0.0.1:8000`

### 6. 必配：Nginx/OpenResty 配置 (解决 404 和上传限制)
**非常重要！** 默认配置会导致 Vue 页面刷新报 404，且无法上传超过 1MB 的图片。
请在 **网站设置** -> **配置文件** 里，修改 content 如下：

```nginx
# --- 关键修改 0.1：定义缓存路径 (可选) ---
# proxy_cache_path /www/sites/YOUR_DOMAIN_NAME/cache levels=1:2 keys_zone=img_cache:100m max_size=10g inactive=30d use_temp_path=off;

server {
    listen 80;
    listen [::]:80;
    server_name YOUR_DOMAIN_NAME; # 替换为你的域名
    
    # --- 关键修改 0.2：开启 Gzip 压缩 ---
    gzip on;
    # ... (保持原样)

    # --- 关键修改 1：允许上传超大文件 (支持 20GB) ---
    client_max_body_size 20480M;

    root /www/sites/YOUR_DOMAIN_NAME/index;
    index index.php index.html index.htm;
    
    # --- 关键修改 2：核心转发 (支持审核逻辑与隐形代理) ---
    location ~ ^/(api|img|uploads) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时时间延长至 1 小时，支持大文件合并
        proxy_connect_timeout 60s;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_request_buffering off;
        
        # 缓存配置 (配合上面的 cache_path)
        # proxy_cache img_cache;
        # proxy_cache_valid 200 30d;
    }

    # --- 关键修改 3：支持 Vue 路由 ---
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理 (1Panel 自动生成的可以酌情整合到上面)
}
```

---

## 方式二：手动部署 (像宝塔一样)

如果你不想用 Docker，流程和宝塔 **完全一样**：

1.  上传代码到 `/opt/pickoala/` 下(或者任意你喜欢的目录)。
2.  **前端**：和上面一样，建一个静态网站指向 `dist`。
3.  **后端**：
    *   你需要自己 SSH 进服务器。
    *   `apt install python3-venv ...` (装环境)。
    *   `python3 -m venv venv` (建环境)。
    *   `pip install ...` (装依赖)。
    *   写一个 `systemd` 服务文件 (配置同 BAOTA_DEPLOY.md，只需修改路径)。

**结论**：用 1Panel 就用 Docker，省心！

## 7. 常见问题与排查

- **系统诊断**: 
  部署完成后，请以管理员身份登录，进入 **后台管理 -> 系统状态 -> 系统诊断**。系统会自动检测数据库、存储、FFmpeg 等组件的连通性。

- **视频跨域播放**:
  如果需要在其他网站嵌入视频，请参考根目录下的 `CORS_CONFIG_GUIDE.md` 进行配置。

- **支付宝配置**: PicKoala 使用的是“**当面付**”产品。移动端支持自动拉起 App 支付，PC端显示二维码扫码。需在后台填写 AppID、应用私钥和支付宝公钥。

- **易支付配置**: 支持标准易支付接口协议。需在后台配置 API 地址、PID、商户密钥以及自定义的显示名称和 Logo。

- **支持超大文件上传 (如 20GB)**:
  1. **Nginx 配置**: 修改 `client_max_body_size` 为 `20480M` (见上文 Nginx 配置部分)。
  2. **系统设置**: 登录管理员后台 -> **系统设置** -> **上传设置**，将 "VIP最大视频大小" 修改为 `21474836480` (字节，即 20GB)。
  3. **增加超时**: 这一步非常重要！请确保 Nginx 配置中的 `proxy_read_timeout` 至少为 `3600s` (1小时)，否则大文件在后端合并时会因超时而中断。
