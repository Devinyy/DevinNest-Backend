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
- **URL**: `/api/v1/backstage/auth/login`
- **Method**: `POST`
- **描述**: 用户名密码登录，获取 Token。
- **请求参数**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应数据**:
  ```json
  {
    "token": "string",
    "userInfo": "..."
  }
  ```

### 2.2 获取当前用户信息
- **URL**: `/api/v1/backstage/auth/me`
- **Method**: `GET`
- **描述**: 校验 Token 有效性并获取用户信息。
In a real app, you would decode the token to get the user ID.
- **响应数据**:
  ```json
  {
    "id": "string",
    "username": "string",
    "avatar": "string"
  }
  ```

### 2.3 退出登录
- **URL**: `/api/v1/backstage/auth/logout`
- **Method**: `POST`
- **描述**: 退出登录 (Client side clears token).
- **响应数据**:
  (无返回数据)

## 3. 仪表盘 (Dashboard)

### 3.1 获取统计数据
- **URL**: `/api/v1/backstage/dashboard/stats`
- **Method**: `GET`
- **描述**: 获取首页所需的各项统计指标。
- **响应数据**:
  ```json
  {
    "blogsCount": 0,
    "snippetsCount": 0,
    "categoriesCount": 0,
    "tagsCount": 0,
    "blogsNewThisMonth": 0,
    "snippetsNewThisMonth": 0,
    "latestActivity": [
      {
        "id": "string",
        "title": "string",
        "type": "string",
        "createdAt": "string"
      }
    ]
  }
  ```

## 4. 博客管理 (Blogs)

### 4.1 获取博客列表
- **URL**: `/api/v1/backstage/blogs`
- **Method**: `GET`
- **描述**: 获取博客列表，支持分页和筛选。
- **Query 参数**:
  - `page`: - 
  - `pageSize`: - 
  - `status`: - 
  - `keyword`: - 
  - `categoryId`: - 
- **响应数据**:
  ```json
  {
    "list": [
      "..."
    ],
    "total": 0
  }
  ```

### 4.2 Create Blog
- **URL**: `/api/v1/backstage/blogs/create`
- **Method**: `POST`
- **描述**: Create a new blog.
- **请求参数**:
  ```json
  {
    "title": "string",
    "subtitle": "any",
    "cover": "any",
    "categoryId": "string",
    "tagIds": [
      "..."
    ],
    "status": "string",
    "content": "string"
  }
  ```
- **响应数据**:
  ```json
  {
    "title": "string",
    "subtitle": "any",
    "cover": "any",
    "categoryId": "string",
    "tagIds": [
      "..."
    ],
    "status": "string",
    "id": "string",
    "content": "any",
    "views": 0,
    "createdAt": "string",
    "category": "any",
    "tags": [
      "..."
    ]
  }
  ```

### 4.3 获取博客详情
- **URL**: `/api/v1/backstage/blogs/{id}`
- **Method**: `GET`
- **描述**: 获取博客详情。
- **响应数据**:
  ```json
  {
    "title": "string",
    "subtitle": "any",
    "cover": "any",
    "categoryId": "string",
    "tagIds": [
      "..."
    ],
    "status": "string",
    "id": "string",
    "content": "any",
    "views": 0,
    "createdAt": "string",
    "category": "any",
    "tags": [
      "..."
    ]
  }
  ```

### 4.4 更新博客
- **URL**: `/api/v1/backstage/blogs/update`
- **Method**: `POST`
- **描述**: 更新博客文章。
- **请求参数**:
  ```json
  {
    "id": "string",
    "title": "string",
    "subtitle": "any",
    "cover": "any",
    "categoryId": "string",
    "tagIds": [
      "..."
    ],
    "status": "string",
    "content": "any"
  }
  ```
- **响应数据**:
  ```json
  {
    "title": "string",
    "subtitle": "any",
    "cover": "any",
    "categoryId": "string",
    "tagIds": [
      "..."
    ],
    "status": "string",
    "id": "string",
    "content": "any",
    "views": 0,
    "createdAt": "string",
    "category": "any",
    "tags": [
      "..."
    ]
  }
  ```

### 4.5 删除博客
- **URL**: `/api/v1/backstage/blogs/delete`
- **Method**: `POST`
- **描述**: 删除博客文章。
- **请求参数**:
  ```json
  {
    "id": "string"
  }
  ```
- **响应数据**:
  (无返回数据)

## 5. 碎片管理 (Snippets)

### 5.1 获取碎片列表
- **URL**: `/api/v1/backstage/snippets`
- **Method**: `GET`
- **Query 参数**:
  - `page`: - 
  - `pageSize`: - 
- **响应数据**:
  ```json
  [
    {
      "content": "...",
      "metadata": "...",
      "tags": "...",
      "id": "..."
    }
  ]
  ```

### 5.2 Create Snippet
- **URL**: `/api/v1/backstage/snippets/create`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "content": [
      "..."
    ],
    "metadata": "...",
    "tags": [
      "..."
    ]
  }
  ```
- **响应数据**:
  ```json
  {
    "content": [
      "..."
    ],
    "metadata": "...",
    "tags": [
      "..."
    ],
    "id": "string"
  }
  ```

### 5.3 获取碎片详情
- **URL**: `/api/v1/backstage/snippets/{id}`
- **Method**: `GET`
- **响应数据**:
  ```json
  {
    "content": [
      "..."
    ],
    "metadata": "...",
    "tags": [
      "..."
    ],
    "id": "string"
  }
  ```

### 5.4 更新碎片
- **URL**: `/api/v1/backstage/snippets/update`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "string",
    "content": [
      "..."
    ],
    "metadata": "...",
    "tags": [
      "..."
    ]
  }
  ```
- **响应数据**:
  ```json
  {
    "content": [
      "..."
    ],
    "metadata": "...",
    "tags": [
      "..."
    ],
    "id": "string"
  }
  ```

### 5.5 删除碎片
- **URL**: `/api/v1/backstage/snippets/delete`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "string"
  }
  ```
- **响应数据**:
  (无返回数据)

## 6. 分类与标签 (Taxonomy)

### 6.1 获取分类列表
- **URL**: `/api/v1/backstage/categories`
- **Method**: `GET`
- **响应数据**:
  ```json
  [
    {
      "name": "...",
      "icon": "...",
      "color": "...",
      "id": "...",
      "count": "..."
    }
  ]
  ```

### 6.2 创建分类
- **URL**: `/api/v1/backstage/categories/create`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "name": "string",
    "icon": "any",
    "color": "any"
  }
  ```
- **响应数据**:
  ```json
  {
    "name": "string",
    "icon": "any",
    "color": "any",
    "id": "string",
    "count": 0
  }
  ```

### 6.3 更新分类
- **URL**: `/api/v1/backstage/categories/update`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "string",
    "name": "string",
    "icon": "any",
    "color": "any"
  }
  ```
- **响应数据**:
  ```json
  {
    "name": "string",
    "icon": "any",
    "color": "any",
    "id": "string",
    "count": 0
  }
  ```

### 6.4 删除分类
- **URL**: `/api/v1/backstage/categories/delete`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "string"
  }
  ```
- **响应数据**:
  (无返回数据)

### 6.5 获取标签列表
- **URL**: `/api/v1/backstage/tags`
- **Method**: `GET`
- **响应数据**:
  ```json
  [
    {
      "name": "...",
      "color": "...",
      "id": "...",
      "count": "..."
    }
  ]
  ```

### 6.6 创建标签
- **URL**: `/api/v1/backstage/tags/create`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "name": "string",
    "color": "any"
  }
  ```
- **响应数据**:
  ```json
  {
    "name": "string",
    "color": "any",
    "id": "string",
    "count": 0
  }
  ```

### 6.7 更新标签
- **URL**: `/api/v1/backstage/tags/update`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "string",
    "name": "string",
    "color": "any"
  }
  ```
- **响应数据**:
  ```json
  {
    "name": "string",
    "color": "any",
    "id": "string",
    "count": 0
  }
  ```

### 6.8 删除标签
- **URL**: `/api/v1/backstage/tags/delete`
- **Method**: `POST`
- **请求参数**:
  ```json
  {
    "id": "string"
  }
  ```
- **响应数据**:
  (无返回数据)

## 7. 通用接口 (Common)

### 7.1 文件上传
- **URL**: `/api/v1/backstage/upload`
- **Method**: `POST`
- **描述**: 上传文件到服务器。
- **请求参数**:
- **响应数据**:
  ```json
  {
    "url": "string",
    "filename": "string"
  }
  ```

## 8. AI 服务 (LLM)

### 8.1 Chat Completion
- **URL**: `/api/v1/ai/chat`
- **Method**: `POST`
- **描述**: Generate a chat completion using the configured LLM.
- **请求参数**:
  ```json
  {
    "messages": [
      "..."
    ],
    "model": "string",
    "temperature": 0.0
  }
  ```
- **响应数据**:
  ```json
  {
    "id": "string",
    "choices": [
      "..."
    ],
    "created": 0,
    "model": "string"
  }
  ```

## 9. DevinNest 项目 (Projects)

### 9.1 Read Projects
- **URL**: `/api/v1/nest/projects/`
- **Method**: `GET`
- **描述**: Retrieve projects for the current user (DevinNest Web).
- **Query 参数**:
  - `skip`: - 
  - `limit`: - 
- **响应数据**:
  ```json
  [
    {
      "id": "...",
      "name": "...",
      "description": "...",
      "owner": "..."
    }
  ]
  ```

### 9.2 Create Project
- **URL**: `/api/v1/nest/projects/`
- **Method**: `POST`
- **描述**: Create a new project.
- **请求参数**:
  ```json
  {
    "id": 0,
    "name": "string",
    "description": "string",
    "owner": "string"
  }
  ```
- **响应数据**:
  ```json
  {
    "id": 0,
    "name": "string",
    "description": "string",
    "owner": "string"
  }
  ```

## 10. 前台首页 (Home)

### 10.1 获取最新文章
- **URL**: `/api/v1/nest/home/latest-articles`
- **Method**: `GET`
- **描述**: 获取首页展示的最新文章列表（最多4篇）。
- **响应数据**:
  ```json
  {
    "title": "string",
    "url": "string",
    "articles": [
      {
        "cover": "string",
        "title": "string",
        "subdesc": "string",
        "url": "string",
        "time": "string",
        "views": 0,
        "category": "string",
        "tags": [
          "string"
        ]
      }
    ]
  }
  ```

### 10.2 获取最新碎片
- **URL**: `/api/v1/nest/home/latest-snippets`
- **Method**: `GET`
- **描述**: 获取首页展示的最新日常碎片（最多4篇）。
- **响应数据**:
  ```json
  {
    "diaryCards": [
      {
        "title": "string",
        "url": "string",
        "bgStyle": "string",
        "textStyle": "string"
      }
    ]
  }
  ```

## 11. 前台博客 (Blog)

### 11.1 获取博客文章列表
- **URL**: `/api/v1/nest/blog/list`
- **Method**: `GET`
- **描述**: 获取博客文章列表，支持分页、分类/标签筛选、关键词搜索及按年份筛选。
- **Query 参数**:
  - `page`: 当前页码 (默认 1)
  - `pageSize`: 每页条数 (默认 10)
  - `categoryId`: 按分类ID筛选 (可选)
  - `tag`: 按标签名筛选 (可选)
  - `keyword`: 搜索关键词 (可选)
  - `year`: 按年份筛选 (可选)
- **响应数据**:
  ```json
  {
    "list": [
      {
        "id": "string",
        "title": "string",
        "desc": "string",
        "slug": "string",
        "cover": "string",
        "date": "string",
        "category": {
          "id": "string",
          "name": "string"
        },
        "tags": [
          "string"
        ],
        "views": 0
      }
    ],
    "total": 0,
    "totalPages": 0,
    "currentPage": 0
  }
  ```

### 11.2 获取博客文章详情
- **URL**: `/api/v1/nest/blog/{id}`
- **Method**: `GET`
- **描述**: 获取博客文章详情，包括正文内容。同时会增加文章的浏览量。仅能获取已发布（published）的文章。
- **响应数据**:
  ```json
  {
    "id": "string",
    "title": "string",
    "desc": "string",
    "slug": "string",
    "cover": "string",
    "date": "string",
    "content": "string",
    "category": {
      "id": "string",
      "name": "string"
    },
    "tags": [
      "string"
    ],
    "views": 0
  }
  ```

### 11.3 获取分类统计
- **URL**: `/api/v1/nest/blog/categories`
- **Method**: `GET`
- **描述**: 获取博客分类统计数据。
- **响应数据**:
  ```json
  [
    {
      "id": "string",
      "name": "string",
      "count": 0,
      "icon": "string"
    }
  ]
  ```

### 11.4 获取标签统计列表
- **URL**: `/api/v1/nest/blog/tags`
- **Method**: `GET`
- **描述**: 获取所有标签及其关联的文章数量统计。无关联文章的标签 count 为 0。
- **响应数据**:
  ```json
  [
    {
      "name": "string",
      "count": 0
    }
  ]
  ```

## 12. Other

### 11.1 Root
- **URL**: `/`
- **Method**: `GET`
- **响应数据**:
  (无返回数据)

