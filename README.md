# MatchIt Form System

## 项目概述
MatchIt Form System 是一个基于 Flask 的轻量级表单管理系统，旨在为用户提供便捷的表单创建、提交和数据管理功能。该系统具有用户认证机制，区分管理员和普通用户角色，不同角色拥有不同权限。管理员可以创建、编辑和管理表单，查看所有表单提交记录；普通用户可以填写表单并查看自己的提交记录。此外，系统还提供了数据统计分析功能，支持计算表单字段的平均值、最大值和最小值。

## 用途
MatchIt Form System 可广泛应用于各种需要表单收集数据的场景，如调查问卷、报名登记、信息收集等。其简洁的设计和模块化的架构，使其成为开发更复杂表单设计软件的理想基础框架。通过对该系统进行扩展和定制，可以满足不同用户的多样化需求，如添加更多的表单字段类型、实现数据可视化、集成第三方服务等。

## 功能特性
1. **用户认证**：支持管理员和普通用户登录，不同角色具有不同的权限，确保数据的安全性和隐私性。

![image](https://github.com/user-attachments/assets/c552c1e0-cd9e-4c78-a980-e7084ac33e99)


2. **表单管理**：管理员可以创建、编辑和启用/禁用表单，灵活配置表单的标题、描述和字段信息。

![image](https://github.com/user-attachments/assets/2ae22a67-d4fc-4b38-bba7-ad5aad412bfe)


![image](https://github.com/user-attachments/assets/c7a665f7-d6a8-4562-84cf-2d6a91465cb4)


3. **表单提交**：普通用户可以填写表单并提交，系统会自动保存提交记录。


![image](https://github.com/user-attachments/assets/e611fdde-4e52-4934-9fd7-3fa8aa59187e)


4. **数据查看**：管理员可以查看所有表单的提交记录，普通用户可以查看自己的提交记录，方便数据的管理和跟踪。


![image](https://github.com/user-attachments/assets/75f2dfab-6a36-4c3b-9af5-d5bf7f42b7a8)


5. **数据统计**：支持计算表单字段的平均值、最大值和最小值，为数据分析提供基础支持。


![image](https://github.com/user-attachments/assets/d0c2de5e-f32b-47e3-96a6-3b3368f5c854)


## 目录结构
```
MatchIt/
├── app.py                  # 主应用文件
├── function/
│   ├── calculate_average.py  # 计算字段平均值的模块
│   ├── calculate_maximum.py  # 计算字段最大值的模块
│   └── calculate_minimum.py  # 计算字段最小值的模块
├── templates/
│   ├── all_submissions.html  # 显示所有表单提交记录的模板
│   ├── base.html             # 基础模板
│   ├── form_submissions.html # 显示单个表单提交记录的模板
│   ├── login.html            # 登录页面模板
│   └── view_submission.html  # 查看单个提交记录详情的模板
├── static/
│   ├── css/
│   │   └── style.css         # 样式文件
│   └── js/
│       ├── average_calculator.js # 计算平均值的 JavaScript 文件
│       ├── maximum_calculator.js # 计算最大值的 JavaScript 文件
│       ├── minimum_calculator.js # 计算最小值的 JavaScript 文件
│       └── script.js           # 主 JavaScript 文件
└── data/
    ├── users.json            # 用户数据文件
    ├── forms.json            # 表单数据文件
    └── submissions.json      # 表单提交数据文件
```

## 安装与运行
### 安装依赖
确保你已经安装了 Python 和 Flask。可以使用以下命令安装 Flask：
```bash
pip install flask
```

### 运行项目
在项目根目录下运行以下命令启动应用：
```bash
python app.py
```

### 访问应用
打开浏览器，访问 `http://127.0.0.1:5000` 即可进入登录页面。

## 代码说明
### 主应用文件 `app.py`
- 定义了 Flask 应用的路由和主要逻辑，包括用户登录、表单管理、数据查看等功能。
- 使用 `session` 进行用户会话管理，确保用户登录状态的安全。
- 提供了 API 接口，用于获取表单和提交记录，以及计算字段的平均值、最大值和最小值。

### 计算模块
- `calculate_average.py`：计算表单字段的平均值。
- `calculate_maximum.py`：计算表单字段的最大值。
- `calculate_minimum.py`：计算表单字段的最小值。

### 模板文件
- 所有模板文件都使用 Jinja2 模板引擎，用于生成 HTML 页面。
- `base.html` 是基础模板，其他模板文件继承自该模板。

### JavaScript 文件
- `average_calculator.js`、`maximum_calculator.js` 和 `minimum_calculator.js` 分别用于计算平均值、最大值和最小值，并通过 AJAX 请求与后端交互。
- `script.js` 包含了表单验证、复选框处理和动态字段选项等功能。

## API 接口
### 获取表单提交记录
- **URL**：`/api/submissions/<form_id>`
- **方法**：`GET`
- **描述**：根据表单 ID 获取表单的提交记录。管理员可以获取所有提交记录，普通用户只能获取自己的提交记录。

### 计算字段平均值
- **URL**：`/api/calculate_average/<form_id>/<field_name>`
- **方法**：`GET`
- **描述**：计算指定表单字段的平均值。

### 计算字段最大值
- **URL**：`/api/calculate_maximum/<form_id>/<field_name>`
- **方法**：`GET`
- **描述**：计算指定表单字段的最大值。

### 计算字段最小值
- **URL**：`/api/calculate_minimum/<form_id>/<field_name>`
- **方法**：`GET`
- **描述**：计算指定表单字段的最小值。

## 移植与扩展
MatchIt Form System 的模块化设计使其易于移植和扩展。以下是一些可能的扩展方向：
1. **添加更多表单字段类型**：可以在 `form_editor.html` 模板和 `app.py` 中添加新的表单字段类型，如文件上传、日期时间选择器等。
2. **实现数据可视化**：可以使用第三方库（如 Chart.js）对表单提交数据进行可视化展示，如柱状图、折线图等。
3. **集成第三方服务**：可以集成第三方服务，如邮件发送、短信通知等，以实现更复杂的业务逻辑。
4. **优化用户界面**：可以使用更现代化的前端框架（如 React、Vue.js）对用户界面进行优化，提升用户体验。

## 注意事项
- 项目使用 JSON 文件存储数据，适合小型项目。在实际应用中，可以考虑使用数据库进行数据存储，以提高数据的安全性和性能。
- 确保 `app.py` 中的 `app.secret_key` 是安全的，建议在生产环境中使用随机生成的密钥。

## 贡献
如果你对该项目有任何建议或改进意见，欢迎提交 Pull Request 或 Issues。

## 许可证
本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT)。
