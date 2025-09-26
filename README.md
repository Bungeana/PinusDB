# TestDB 蛋白质搜索系统

这是一个功能完整的蛋白质搜索系统，由前端和后端组成。前端使用Vue 3 + Vite构建，后端使用FastAPI实现，支持蛋白质序列查询、BLAST比对和基因表达分析等功能。仅供测试用。

## 项目结构

```
TestDB/
├── backend/            # 后端代码目录
│   ├── main.py         # FastAPI主程序
│   ├── requirements.txt # Python依赖
│   └── jbrowse2/       # JBrowse2基因组浏览器
├── frontend/           # 前端代码目录
│   └── TestDB/         # Vue 3项目
│       ├── src/        # 前端源代码
│       │   ├── components/   # Vue组件
│       │   ├── views/        # 视图组件
│       │   ├── utils/        # 工具函数
│       │   ├── App.vue       # 根组件
│       │   └── main.js       # 入口文件
│       ├── dist/       # 构建输出目录
│       ├── package.json      # npm依赖配置
│       └── vite.config.js    # Vite配置
├── data/               # 数据目录
│   ├── expression/     # 表达数据
│   ├── gene/           # 基因序列数据
│   └── protein/        # 蛋白质数据
└── README.md           # 项目说明文档
```

## 本地开发环境设置

### 后端安装

1. 进入后端目录：

```bash
cd TestDB/backend
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 启动后端服务：

```bash
uvicorn main:app --reload
```

后端服务将运行在 http://127.0.0.1:8000

### 前端安装

1. 进入前端目录：

```bash
cd TestDB/frontend/TestDB
```

2. 安装依赖：

```bash
npm install
```

3. 启动开发服务器：

```bash
npm run dev
```

前端服务将运行在 http://127.0.0.1:5173

## API 接口说明

系统提供多个功能接口：

- GET `/api/protein/{protein_id}`: 根据蛋白质ID查询蛋白质信息

  - 参数: `protein_id` (字符串) - 蛋白质ID
  - 返回: 蛋白质信息（包含protein_id、length和file_path字段）
- POST `/api/blast`: 执行BLAST序列比对

  - 请求体: 包含序列和参数的JSON数据
  - 返回: BLAST比对结果
- GET `/api/expression/{gene_id}`: 获取基因表达数据

  - 参数: `gene_id` (字符串) - 基因ID
  - 返回: 基因表达数据

## 功能说明

系统提供以下核心功能：

1. **蛋白质搜索**: 通过蛋白质ID查询详细信息
2. **BLAST比对**: 进行序列相似度比对分析
3. **基因表达分析**: 查看基因在不同条件下的表达水平
4. **基因组浏览器**: 使用JBrowse2可视化基因组数据

## 服务器部署指南

### 准备工作

1. **服务器要求**:

   - Linux系统 (推荐Ubuntu 20.04或更高版本)
   - Python 3.8+ 和 Node.js 16+
   - Nginx
   - 至少2GB RAM
2. **服务器环境配置**:

```bash
# 更新系统
apt update && apt upgrade -y

# 安装必要软件
apt install -y nginx python3-pip python3-venv git

# 安装Node.js (使用NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
```

### 后端部署

1. **克隆项目**:

```bash
cd /var/www
git clone [项目仓库地址] TestDB
cd TestDB
```

2. **创建虚拟环境并安装依赖**:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]
```

3. **配置环境变量**:

```bash
# 创建.env文件
nano .env

# 添加必要的环境变量
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=testdb

# 保存并退出
```

4. **使用Gunicorn运行FastAPI应用**:

```bash
# 创建Gunicorn配置文件
nano gunicorn_conf.py

# 添加以下内容
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
```

5. **创建系统服务以持久化运行**:

```bash
nano /etc/systemd/system/testdb-backend.service

# 添加以下内容
[Unit]
Description=TestDB FastAPI Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/TestDB/backend
ExecStart=/var/www/TestDB/backend/venv/bin/gunicorn -c gunicorn_conf.py main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

6. **启动服务**:

```bash
systemctl daemon-reload
systemctl start testdb-backend
systemctl enable testdb-backend
```

### 前端部署

1. **构建前端项目**:

```bash
cd /var/www/TestDB/frontend/TestDB
npm install
npm run build
```

2. **配置Nginx服务前端**:

```bash
nano /etc/nginx/sites-available/testdb

# 添加以下配置
server {
    listen 80;
    server_name your_domain.com;

    location / {
        root /var/www/TestDB/frontend/TestDB/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 反向代理后端API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # JBrowse2配置
    location /jbrowse2 {
        root /var/www/TestDB/backend;
        try_files $uri $uri/ /jbrowse2/index.html;
    }
}
```

3. **启用Nginx配置**:

```bash
ln -s /etc/nginx/sites-available/testdb /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 安全配置

1. **配置防火墙**:

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

2. **配置HTTPS** (可选但推荐):

```bash
# 安装Certbot
apt install certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d your_domain.com
```

## 部署后验证

1. **检查服务状态**:

```bash
systemctl status testdb-backend
systemctl status nginx
```

2. **访问系统**:
   - 前端: http://your_domain.com
   - API文档: http://your_domain.com/api/docs

## 维护与更新

1. **更新代码**:

```bash
cd /var/www/TestDB
git pull

# 更新后端
source backend/venv/bin/activate
pip install -r backend/requirements.txt
systemctl restart testdb-backend

# 更新前端
cd frontend/TestDB
npm install
npm run build
```

2. **查看日志**:

```bash
# 后端日志
journalctl -u testdb-backend -f

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 注意事项

1. 确保数据库配置正确，后端服务能够正常连接到数据库
2. 生产环境中应修改默认的数据库连接信息，避免使用默认凭据
3. 定期备份数据库和重要配置文件
4. 监控服务器资源使用情况，根据需要调整Gunicorn的worker数量
5. 部署前确保已关闭开发模式的调试选项

## 故障排除

1. **后端服务无法启动**:

   - 检查环境变量配置
   - 确认数据库连接正常
   - 查看服务日志获取详细错误信息
2. **前端无法访问后端API**:

   - 确认Nginx反向代理配置正确
   - 检查跨域设置
   - 验证后端服务是否正常运行
3. **性能问题**:

   - 增加Gunicorn worker数量
   - 优化数据库查询
   - 考虑使用缓存机制
