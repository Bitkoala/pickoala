# 宝塔面板 (Baota Panel) 部署指南 (推荐版)

本指南将指导你如何在宝塔面板上部署 **PicKoala** 图床系统。
**注意：** 为了保证稳定性，本教程**不使用**宝塔自带的“Python项目管理器”，而是采用更稳定、更标准的 Linux 原生部署方式 (Systemd)。

## 1. 准备工作

在开始之前，请确保你的宝塔面板已安装以下软件（在"软件商店"中安装）：

*   **Nginx** (建议 1.22+)
*   **MySQL** (建议 8.0，5.7 也可以)
*   **Redis** (必装) - *用于验证码和缓存，否则会出现多进程验证码错误*

### 1.1 安装系统依赖库 (通过终端)
进入服务器终端（SSH），执行以下命令安装必要的系统库：

```bash
# 更新源并安装 Python venv 模块和数据库开发库
apt update && apt install -y python3.10-venv pkg-config build-essential default-libmysqlclient-dev
```
*(如果你的系统是 CentOS，请用 `yum install python3-devel mysql-devel` 替代)*

## 2. 数据库配置

1.  进入宝塔面板 -> **数据库** -> **添加数据库**。
2.  填写数据库名（例如 `pickoala`）、用户名和密码。
3.  提交后，点击该数据库右侧的 **管理** (phpMyAdmin) 或 **导入**。
4.  如果是导入，请选择项目目录下的 `database/init.sql` 文件进行导入。
    *   **重要**：务必导入 `init.sql` 初始化表结构（包含最新的支付和会员表）。

## 3. 后端部署 (FastAPI)

### 3.1 上传代码
1.  进入 **文件**，将项目代码上传到服务器目录（建议 `/www/wwwroot/pickoala`）。
2.  解压，确保目录结构如下：
    ```
    /www/wwwroot/pickoala/
    ├── backend/
    ├── pickoala/
    └── ...
    ```

### 3.2 配置环境变量
1.  进入 `backend` 目录。
2.  复制 `.env.example` 为 `.env`。
3.  编辑 `.env` 文件，修改数据库连接配置：
    ```ini
    # 随机生成一个密钥
    APP_SECRET_KEY=生成的随机强密码
    
    # 数据库配置 (需对应第2步创建的信息)
    # 格式: mysql+aiomysql://用户名:密码@127.0.0.1:3306/数据库名
    DATABASE_URL=mysql+aiomysql://pickoala:password@127.0.0.1:3306/pickoala
    
    # Redis 配置 (必填)
    REDIS_ENABLED=true
    REDIS_URL=redis://127.0.0.1:6379/0
    
    # 注意：所有支付配置 (Stripe/支付宝)、邮件、存储等均在后台管理面板设置，此处无需配置。
    ```

### 3.3 创建虚拟环境与安装依赖 (最关键一步)
在终端中执行以下命令（请一行行复制执行）：

1.  **创建虚拟环境**：
    ```bash
    cd /www/wwwroot/pickoala/backend
    python3 -m venv venv
    ```

2.  **安装依赖**：
    ```bash
    ./venv/bin/pip install -r requirements.txt
    ```
    *(如果有报错提示缺少 gcc 或 mysqlclient，请回头检查 1.1 步是否执行到位)*

### 3.4 配置 Systemd 服务 (实现开机自启)
我们使用 Linux 标准的服务管理器来管理后台。

1.  **创建服务文件**：
    新建文件 `/etc/systemd/system/pickoala-backend.service`，内容如下：
    (注意修改路径里的用户和目录，如果你完全按照本教程，则可直接复制)

    ```ini
    [Unit]
    Description=PicKoala Backend Service
    After=network.target

    [Service]
    User=root
    Group=root
    WorkingDirectory=/www/wwwroot/pickoala/backend
    # 指向虚拟环境中的 python
    ExecStart=/www/wwwroot/pickoala/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
    Restart=always
    RestartSec=5
    Environment=LANG=C.UTF-8 LC_ALL=C.UTF-8

    [Install]
    WantedBy=multi-user.target
    ```

2.  **注册并启动服务**：
    ```bash
    # 重载配置
    systemctl daemon-reload
    
    # 开启自启并立即启动
    systemctl enable pickoala-backend
    systemctl start pickoala-backend
    
    # 查看状态 (应显示绿色的 active running)
    systemctl status pickoala-backend
    ```

## 4. 前端部署 (Vue 3)

### 4.1 编译前端
1.  在本地电脑进入 `pickoala` 目录。
2.  运行 `npm install` 然后 `npm run build`。
3.  将生成的 `dist` 文件夹上传到服务器（例如 `/www/wwwroot/pickoala/dist_frontend`）。

### 4.2 创建网站
1.  在宝塔面板 **网站** -> **PHP项目** (或纯静态) -> **添加站点**。
2.  **域名**：填写你的域名（或服务器IP）。
3.  **根目录**：指向刚才上传的 `dist_frontend` 目录。

## 5. 反向代理配置 (连接前后端)

### 5.1 创建缓存目录 (必须)
为了支持高效的图片缓存，请务必在终端执行以下命令创建缓存目录：

```bash
# 1. 创建目录
mkdir -p /www/swift_cache
# 2. 修改目录所有者为 www 用户 (关键步骤，宝塔默认是 www)
chown -R www:www /www/swift_cache
# 3. 赋予读写执行权限
chmod -R 755 /www/swift_cache
```

### 5.2 修改配置文件
1.  进入 **网站** -> 点击刚创建的网站 -> **配置文件**。
2.  **替换** `server` 块中的 `location` 配置如下：

```nginx
    # 【新增】支持 20GB 上传限制 (20480M)
    client_max_body_size 20480M;

    # 【新增】开启 Gzip 压缩 (大幅提升加载速度)
    gzip on;
    gzip_min_length 1k;
    gzip_buffers 4 16k;
    gzip_comp_level 5;
    gzip_types text/plain application/javascript application/x-javascript text/javascript text/xml text/css;
    gzip_vary on;
    gzip_disable "MSIE [1-6]\.";

    # 1. 前端路由支持 (解决刷新 404)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 2. 核心转发：API 请求、图片代理（/img）及本地资源（/uploads）
    # 统一经由后端处理以支持“预览审核”和“隐形代理”
    location ~ ^/(api|img|uploads) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # --- 缓存配置 (可选) ---
        proxy_cache img_cache;
        proxy_cache_valid 200 302 30d;
        proxy_cache_key $host$uri$is_args$args;
        add_header X-Cache-Status $upstream_cache_status;

        # --- 超时与大文件优化 ---
        # 增加超时到 1小时 (3600s)，以支持 20GB 文件的合并和云端转存
        proxy_connect_timeout 60s;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        
        # 大文件上传不建议经过 Nginx 缓存请求体
        proxy_request_buffering off;
    }
```
*(注意：location /uploads 使用 `alias` 直接指向后端上传目录效率更高，前提是前后端在同一台服务器)*

3.  保存即可！现在访问域名即可看到完整网站。
4.  **最后一步**：
    登录管理员账号 (默认: `admin` / `Admin123`)。
    进入 **管理面板 -> 系统设置 -> 支付配置**，启用 Stripe、支付宝或易支付。
    *   **支付宝配置**：PicKoala 使用的是“**当面付**”产品。你需要在后台配置：`APPID`、`应用私钥`、`支付宝公钥`。
    *   **易支付配置**：支持标准易支付协议。需配置 `API 地址`、`PID` 和 `Key`，支持自定义前端显示的名称和 Logo。

## 6. 常见问题与排查

- **系统诊断**: 
  部署完成后，请以管理员身份登录，进入 **后台管理 -> 系统状态 -> 系统诊断**。系统会自动检测数据库、存储、FFmpeg 等组件的连通性。

- **视频跨域播放**:
  如果需要在其他网站嵌入视频，请参考根目录下的 `CORS_CONFIG_GUIDE.md` 进行配置。

- **支持超大文件上传 (如 10GB)**:
  1. **Nginx 配置**: 修改 `client_max_body_size` 为 `10240M` (见上文 Nginx 配置部分)。
  2. **系统设置**: 登录管理员后台 -> **系统设置** -> **上传设置**，将 "VIP最大视频大小" 修改为 `10737418240` (字节，即 10GB)。
  3. **增加超时**: 这一步非常重要！请确保 Nginx 配置中的 `proxy_read_timeout` 至少为 `3600s` (1小时)，否则大文件在后端合并时会因超时而中断。
