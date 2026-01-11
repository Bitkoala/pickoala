# Casdoor 自定义 UI 模板示例 (优化版)

这些模板已针对宽度和高度进行优化，去除了冗余边距，防止页面出现滚动条。

## 1. 侧边栏 (Side Panel HTML) - 紧凑型

```html
<div style="
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    height: 100%;
    color: #333;
    padding: 0 24px;
    box-sizing: border-box;
    font-family: -apple-system, system-ui, sans-serif;
">
    <div style="margin-bottom: 20px;">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="#4F46E5" stroke-width="2"/>
            <path d="M8 12L11 15L16 9" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>

    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 8px; color: #111827;">
        PicKoala 智能云图床
    </h2>

    <div style="font-size: 14px; line-height: 1.6; color: #6B7280; max-width: 280px; text-align: left;">
        <ul style="list-style: none; padding: 0; margin: 16px 0;">
            <li style="margin-bottom: 8px; display: flex; align-items: flex-start; gap: 8px;">
                <span style="color: #4F46E5;">✓</span> 
                <span><strong>多云存储</strong>：支持 S3, OSS, COS 等主流协议</span>
            </li>
            <li style="margin-bottom: 8px; display: flex; align-items: flex-start; gap: 8px;">
                <span style="color: #4F46E5;">✓</span> 
                <span><strong>全球分发</strong>：CDN 加速，图片即刻呈现</span>
            </li>
            <li style="margin-bottom: 8px; display: flex; align-items: flex-start; gap: 8px;">
                <span style="color: #4F46E5;">✓</span> 
                <span><strong>智能审核</strong>：AI 识别，确保内容合规安全</span>
            </li>
            <li style="margin-bottom: 8px; display: flex; align-items: flex-start; gap: 8px;">
                <span style="color: #4F46E5;">✓</span> 
                <span><strong>高效管理</strong>：精美 UI，支持相册与权限控制</span>
            </li>
        </ul>
    </div>

    <div style="font-size: 11px; color: #9CA3AF; margin-top: 20px;">
        &copy; 2026 PicKoala · 统一身份认证
    </div>
</div>
```

---

## 2. 页头 (Header HTML) - 极简型

```html
<header style="
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-sizing: border-box;
    z-index: 100;
">
    <div style="display: flex; align-items: center; gap: 8px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <rect width="24" height="24" rx="4" fill="#4F46E5"/>
            <path d="M12 6V18M6 12H18" stroke="white" stroke-width="2"/>
        </svg>
        <span style="font-weight: 700; font-size: 14px; color: #1F2937;">PicKoala ID</span>
    </div>
</header>
```

---

## 3. 页脚 (Footer HTML) - 极简型

```html
<footer style="
    position: fixed;
    bottom: 0;
    width: 100%;
    padding: 12px;
    text-align: center;
    font-size: 12px;
    color: #9CA3AF;
    box-sizing: border-box;
">
    <div>
        &copy; <span id="year">2026</span> PicKoala.
        <a href="#" style="text-decoration: none; color: #6B7280; margin-left: 10px;">隐私</a>
        <a href="#" style="text-decoration: none; color: #6B7280; margin-left: 10px;">条款</a>
    </div>
    <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</footer>
```

---

## 4. 自定义 CSS (Form CSS) - 完整合并版

**用途**：包含您原本的面板样式，以及新增的第三方登录图标放大样式。请直接将以下内容全部复制到 Casdoor 应用设置中的 **"Form CSS"** 字段。

```css
/* --- 1. 您原本的面板样式 --- */
<style>
.login-panel {
  padding: 40px 70px 0 70px;
  border-radius: 10px;
  background-color: #ffffff;
  box-shadow: 0 0 30px 20px rgba(0, 0, 0, 0.20);
}

.login-panel-dark {
  padding: 40px 70px 0 70px;
  border-radius: 10px;
  background-color: #333333;
  box-shadow: 0 0 30px 20px rgba(255, 255, 255, 0.20);
}

.forget-content {
  padding: 10px 100px 20px;
  margin: 30px auto;
  border: 2px solid #fff;
  border-radius: 7px;
  background-color: rgb(255 255 255);
  box-shadow: 0 0 20px rgb(0 0 0 / 20%);
}

/* --- 2. 新增：进一步放大第三方登录图标 --- */
.provider-item {
  width: 54px !important;    /* 从 42px 增加到 54px */
  height: 54px !important;
  margin: 10px !important;   /* 稍微增加间距 */
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  border-radius: 10px !important; /* 稍微加大圆角配合大图标 */
  transition: all 0.3s !important;
}

.provider-item:hover {
  transform: scale(1.1);
  background-color: #f3f4f6 !important;
}

.provider-item img {
  width: 34px !important;    /* 从 26px 增加到 34px */
  height: 34px !important;
  object-fit: contain !important;
}
</style>
```
<style>
/* 针对桌面端的背景优化 */
body {
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

/* 针对手机端的背景优化 */
@media (max-width: 768px) {
    body {
        background-size: cover !important;
        background-position: center top !important; /* 手机端背景通常靠上排列 */
    }
}
</style>