# Cloudflare Cache Rules 备忘录 (Free 版)

针对 PicKoala 图床系统优化的 Cloudflare 缓存规则。

---

## 附录：如何获取 Cloudflare 凭据

### 1. 区域 ID (Zone ID)
1. 登录 [Cloudflare 控制面板](https://dash.cloudflare.com/)。
2. 在“站点”列表中点击进入您的域名。
3. 在左侧菜单中点击 **概览 (Overview)**。
4. 在页面右侧栏（手机版在最下方）找到 **API** 栏目。
5. **区域 ID** 直接显示在该栏目中。

### 2. API 令牌 (API Token)
1. 在“概览”页右侧 API 栏目下，点击 **获取您的 API 令牌 (Get your API token)**。
2. 点击 **创建令牌 (Create Token)**。
3. 找到 **清除缓存 (Clear Cache)** 模板，点击右侧的 **使用模板 (Use template)**。
4. 在 **区域资源 (Zone Resources)** 部分：
   - 选择 **包括 (Include)** -> **特定区域 (Specific zone)** -> **您的域名**。
5. 点击页面底部的 **继续以显示摘要 (Continue to summary)**。
6. 点击 **创建令牌 (Create Token)**。
7. 复制生成的令牌并填入 PicPanda 后台的 `cf_api_token`项。

## 规则 1：动态接口与认证 (必须绕过缓存)
**目的**：确保登录、API、Casdoor 回调不会被缓存。
*   **匹配规则 (表达式)**:
    ```
    starts_with(http.request.uri.path, "/api/") or starts_with(http.request.uri.path, "/auth/")
    ```
*   **设置 (操作)**:
    *   **缓存资格 (Cache eligibility)**: 绕过缓存 (Bypass cache)

---

## 规则 2：前端静态资源 (全量缓存)
**目的**：加速 JS/CSS 加载。因为 Vite 资源带 Hash，即使浏览器缓存一年也没问题。
*   **匹配规则 (表达式)**:
    ```
    starts_with(http.request.uri.path, "/assets/") or (http.request.uri.path contains ".js") or (http.request.uri.path contains ".css") or (http.request.uri.path contains ".woff2")
    ```
*   **设置 (操作)**:
    *   **缓存资格 (Cache eligibility)**: 符合缓存条件 (Eligible for cache)
    *   **边缘 TTL (Edge TTL)**: 1 个月
    *   **浏览器 TTL (Browser TTL)**: 重写为... (Override to...) -> 1 年

---

## 规则 3：图床图片 (长期缓存)
**目的**：减少 S3/OSS 流量开销。
*   **匹配规则 (表达式)**:
    ```
    starts_with(http.request.uri.path, "/i/") or starts_with(http.request.uri.path, "/view/")
    ```
*   **设置 (操作)**:
    *   **缓存资格 (Cache eligibility)**: 符合缓存条件 (Eligible for cache)
    *   **边缘 TTL (Edge TTL)**: 1 个月
    *   **缓存密钥 (Cache Key)**: 勾选“忽略查询字符串 (Ignore query string)”

---

*   **Override to**: 重写为

---

## �️ 如何清理缓存 (Purge Cache)
当你在图床删除了图片或修改了配置，需要让 CF 立即生效时：

### 方法 1：手动清理 (最快最简单)
1.  登录 Cloudflare 仪表板。
2.  进入 **Caching (缓存)** -> **Configuration (配置)**。
3.  点击 **Purge Custom URLs (清除自定义 URL)**。
4.  在输入框中填入该图片的完整 URL（例如 `https://img.com/i/abc.jpg`）。
5.  点击 **Purge (清除)**。

### 方法 2：API 自动清理 (进阶)
如果你希望删除图片时自动清理，可以调用 CF 的 API：
*   **Endpoint**: `POST https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache`
*   **Header**: `Authorization: Bearer <API_TOKEN>`
*   **Body**: `{"files": ["https://img.com/i/abc.jpg"]}`

### 方法 3：全量清除 (慎用)
点击 **Purge Everything (清除所有内容)**。这会导致全站缓存失效，瞬间回源，服务器压力会陡增。建议仅在更换主题或大版本更新时使用。
