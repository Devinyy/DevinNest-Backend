# Devin's Nest API 接口文档

本文档描述了 Devin's Nest 后台管理系统所需的后端 API 接口。

## 1. 基础说明

- **Base URL**: `/api/v1`
- **认证方式**: Bearer Token (Header: `Authorization: Bearer <token>`)
- **数据格式**: JSON
- **响应结构**:

```typescript
interface ApiResponse<T> {
  code: number;      // 200: 成功, 非 200: 失败
  message: string;   // 提示信息
  data: T;           // 业务数据
}
```

## 2. 认证模块 (Auth)

### 2.1 用户登录
- **URL**: `/backstage/auth/login`
- **Method**: `POST`
- **描述**: 用户名密码登录，获取 Token。
- **请求参数**:
  ```json
  {
    "username": "admin",
    "password": "Base64(RSA_Encrypt(password))" // 使用 RSA 公钥加密后的 Base64 字符串
  }
  ```
- **响应数据**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userInfo": {
      "id": "1",
      "username": "admin",
      "avatar": "https://example.com/avatar.jpg"
    }
  }
  ```

### 2.2 获取当前用户信息
- **URL**: `/backstage/auth/me`
- **Method**: `GET`
- **描述**: 校验 Token 有效性并获取用户信息。

### 2.3 退出登录
- **URL**: `/backstage/auth/logout`
- **Method**: `POST`

## 3. 仪表盘 (Dashboard)

### 3.1 获取统计数据
- **URL**: `/backstage/dashboard/stats`
- **Method**: `GET`
- **描述**: 获取首页所需的各项统计指标。
- **响应数据**:
  ```json
  {
    "blogsCount": 120,
    "snippetsCount": 350,
    "categoriesCount": 8,
    "tagsCount": 24,
    "blogsNewThisMonth": 5,
    "snippetsNewThisMonth": 12,
    "latestActivity": [
      {
        "id": "1",
        "title": "React 19 新特性解析",
        "type": "blog",
        "createdAt": "2023-10-01T12:00:00Z"
      },
      {
        "id": "2",
        "title": "今日感悟...",
        "type": "snippet",
        "createdAt": "2023-10-02T09:30:00Z"
      }
    ]
  }
  ```

## 4. 博客管理 (Blogs)

### 4.1 获取博客列表
- **URL**: `/backstage/blogs`
- **Method**: `GET`
- **Query 参数**:
  - `page`: 页码 (默认 1)
  - `pageSize`: 每页数量 (默认 10)
  - `status`: 状态 (draft/published)
  - `keyword`: 搜索关键词 (标题/内容)
  - `categoryId`: 分类筛选
- **响应数据**:
  ```json
  {
    "list": [
      {
        "id": "1",
        "title": "React 19 新特性解析",
        "subtitle": "探索前端开发的未来",
        "cover": "https://example.com/cover.jpg",
        "category": { "id": "1", "name": "技术" },
        "tags": [{ "id": "1", "name": "React" }],
        "views": 1024,
        "status": "published",
        "createdAt": "2023-10-01T12:00:00Z"
      }
    ],
    "total": 100
  }
  ```

### 4.2 获取博客详情
- **URL**: `/backstage/blogs/:id`
- **Method**: `GET`
- **响应数据**: (包含 Markdown 内容)

### 4.3 创建博客
- **URL**: `/backstage/blogs/create`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "title": "文章标题",
    "subtitle": "副标题",
    "content": "# Markdown 内容...",
    "cover": "https://...",
    "categoryId": "1",
    "tagIds": ["1", "2"],
    "status": "published" // 或 'draft'
  }
  ```

### 4.4 更新博客
- **URL**: `/backstage/blogs/update`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "1",
    "title": "更新后的标题",
    "content": "..."
  }
  ```

### 4.5 删除博客
- **URL**: `/backstage/blogs/delete`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "1"
  }
  ```

## 5. 碎片管理 (Snippets)

### 5.1 获取碎片列表
- **URL**: `/backstage/snippets`
- **Method**: `GET`
- **Query 参数**: `page`, `pageSize`, `startDate`, `endDate`

### 5.2 获取碎片详情
- **URL**: `/backstage/snippets/:id`
- **Method**: `GET`

### 5.3 创建碎片
- **URL**: `/backstage/snippets/create`
- **Method**: `POST`
- **描述**: 碎片采用结构化 Block 存储。
- **请求参数**:
  ```json
  {
    "content": [ // Block 数组
      {
        "type": "text",
        "content": "今天天气真不错，去公园散步了。"
      },
      {
        "type": "image",
        "src": "https://...",
        "caption": "公园的一角"
      },
      {
        "type": "quote",
        "content": "Stay hungry, stay foolish.",
        "author": "Steve Jobs"
      }
    ],
    "metadata": {
      "weather": "Sunny",
      "mood": "Happy",
      "location": "Central Park",
      "date": "2023-10-05T10:00:00Z"
    },
    "tags": ["life", "daily"]
  }
  ```

### 5.4 更新碎片
- **URL**: `/backstage/snippets/update`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "1",
    "content": [...]
  }
  ```

### 5.5 删除碎片
- **URL**: `/backstage/snippets/delete`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "1"
  }
  ```

## 6. 分类与标签 (Taxonomy)

### 6.1 获取所有分类
- **URL**: `/backstage/categories`
- **Method**: `GET`
- **响应数据**: `[{ "id": "1", "name": "技术", "count": 10, "icon": "CodeOutlined", "color": "blue" }]`

### 6.2 创建分类
- **URL**: `/backstage/categories/create`
- **Method**: `POST`
- **请求参数**: `{ "name": "新分类", "icon": "...", "color": "..." }`

### 6.3 更新分类
- **URL**: `/backstage/categories/update`
- **Method**: `POST`
- **请求参数**: `{ "id": "1", "name": "更新分类", "icon": "...", "color": "..." }`

### 6.4 删除分类
- **URL**: `/backstage/categories/delete`
- **Method**: `POST`
- **请求参数**: `{ "id": "1" }`

### 6.5 获取所有标签
- **URL**: `/backstage/tags`
- **Method**: `GET`
- **响应数据**: `[{ "id": "1", "name": "React", "count": 5, "color": "cyan" }]`

### 6.6 创建标签
- **URL**: `/backstage/tags/create`
- **Method**: `POST`
- **请求参数**: `{ "name": "新标签", "color": "cyan" }`

### 6.7 更新标签
- **URL**: `/backstage/tags/update`
- **Method**: `POST`
- **请求参数**: `{ "id": "1", "name": "更新标签", "color": "blue" }`

### 6.8 删除标签
- **URL**: `/backstage/tags/delete`
- **Method**: `POST`
- **请求参数**: `{ "id": "1" }`

## 7. 通用接口 (Common)

### 7.1 文件上传
- **URL**: `/backstage/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **请求参数**: `file` (Binary)
- **响应数据**:
  ```json
  {
    "url": "https://your-oss-bucket.com/path/to/image.jpg",
    "filename": "image.jpg"
  }
  ```
