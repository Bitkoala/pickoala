# 首页配置指南 (Homepage Configuration Guide)

PicPanda 支持通过 JSON 格式自定义首页的**特性文案**和**对比表格**，并支持多语言自动切换。

## 1. 特性文案 (Features)

控制首页顶部的特性圆点列表。
- **配置项**: `home_features`
- **格式**: JSON 数组 `Array`
- **说明**: 
    - 数量不限，前端会自动按每行 3 个进行排列。
    - 支持添加任意数量的对象。

**示例代码**:
```json
[
  {
    "zh": "全球 CDN 加速",
    "en": "Global CDN",
    "zh-TW": "全球 CDN 加速"
  },
  {
    "zh": "三地异地备份",
    "en": "Geo-redundant Backup",
    "zh-TW": "三地異地備份"
  },
  {
    "zh": "永久免费存储",
    "en": "Free Storage",
    "zh-TW": "永久免費存儲"
  },
  {
    "zh": "极速上传体验",
    "en": "Blazing Fast Upload",
    "zh-TW": "極速上傳體驗"
  },
  {
    "zh": "隐私加密保护",
    "en": "Privacy Protection",
    "zh-TW": "隱私加密保護"
  },
  {
    "zh": "原图无损保存",
    "en": "Lossless Storage",
    "zh-TW": "原圖無損保存"
  }
]
```

---

## 2. 表格列名 (Table Columns)

控制对比表格的表头（第一行）。
- **配置项**: `home_table_cols`
- **格式**: JSON 对象 `Object`
- **说明**: 
    - `key` 必须严格对应代码中的字段名：`col_guest` (游客), `col_user` (会员), `col_vip` (VIP)。
    - 不可随意更改 key 的名称。

**示例代码**:
```json
{
  "col_guest": {
    "zh": "游客用户",
    "en": "Guest",
    "zh-TW": "遊客用戶"
  },
  "col_user": {
    "zh": "注册会员",
    "en": "Member",
    "zh-TW": "註冊會員"
  },
  "col_vip": {
    "zh": "尊贵 VIP",
    "en": "Premium VIP",
    "zh-TW": "尊貴 VIP"
  }
}
```

---

## 3. 表格行名 (Table Rows)

控制对比表格的左侧标题列。
- **配置项**: `home_table_rows`
- **格式**: JSON 对象 `Object`
- **说明**: 
    - `key` 必须严格对应：
        - `row_single_file`: 单文件限制
        - `row_frequency`: 上传频率
        - `row_album`: 创建相册
        - `row_naming`: 图片命名
        - `row_management`: 图片管理

**示例代码**:
```json
{
  "row_single_file": {
    "zh": "单文件大小限制",
    "en": "Max File Size",
    "zh-TW": "單文件大小限制"
  },
  "row_frequency": {
    "zh": "上传频率限制",
    "en": "Upload Rate Limit",
    "zh-TW": "上傳頻率限制"
  },
  "row_album": {
    "zh": "创建私人相册",
    "en": "Create Albums",
    "zh-TW": "創建私人相冊"
  },
  "row_naming": {
    "zh": "自定义文件名",
    "en": "Custom Filename",
    "zh-TW": "自定義文件名"
  },
  "row_management": {
    "zh": "批量图片管理",
    "en": "Batch Management",
    "zh-TW": "批量圖片管理"
  }
}
```

## 4. 多语言匹配规则

系统会按照以下顺序自动匹配显示的语言：

1. **当前语言**: 如果用户选择了英文，优先寻找 `en` 字段。
2. **简体中文 (兜底)**: 如果当前语言未配置，寻找 `zh-CN` 或 `zh`。
3. **英文 (兜底)**: 如果还没有，寻找 `en`。
4. **默认值**: 如果以上都没有，直接显示 JSON 对象中的**第一个值**。
