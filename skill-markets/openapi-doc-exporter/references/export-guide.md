# 各框架导出 openapi.json 指引

> 本文档列出主流 Web 框架如何导出 OpenAPI 规范（openapi.json）。
> 导出后用 `scripts/render_md.py` 渲染为 Markdown。

## 1. FastAPI

FastAPI 原生支持 OpenAPI 3.x，自动从路由和 Pydantic 模型生成 spec。

**方式 A：从 app 对象导出**（推荐，离线可用）

```python
# export_openapi.py
import json
from main import app  # 你的 FastAPI 实例

spec = app.openapi()
with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(spec, f, ensure_ascii=False, indent=2)

print(f"paths: {len(spec.get('paths', {}))}")
print(f"schemas: {len(spec.get('components', {}).get('schemas', {}))}")
```

执行：`python export_openapi.py`

**方式 B：从运行中的服务拉取**

```bash
curl -s http://localhost:8000/openapi.json > openapi.json
```

**注意事项**：
- `app.openapi()` 不会触发 lifespan，无需启动服务
- 如果 import 时依赖环境变量（DB 路径、API Key），需提前 `os.environ.setdefault()` 或 `load_dotenv()`
- 自定义 schema 用 `Field(json_schema_extra=...)` 或 `model_config = ConfigDict(json_schema_extra=...)`

## 2. Flask + flask-smorest

flask-smorest 提供完整的 OpenAPI 3 支持。

```python
from flask import Flask
from flask_smorest import Api, Blueprint

app = Flask(__name__)
app.config["API_SPEC_OPTIONS"] = {
    "components": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer"}
        }
    }
}
api = Api(app)
# 注册 blp...
spec = api.spec.to_dict()

import json
with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(spec, f, ensure_ascii=False, indent=2)
```

## 3. Flask + apispec

apispec 是更底层的 OpenAPI 生成器，需手动注册 schema。

```python
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

spec = APISpec(
    title="My API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[MarshmallowPlugin()],
)
# spec.components.schema("User", schema=UserSchema)
# spec.path(view=my_view, operations=...)

with open("openapi.json", "w") as f:
    json.dump(spec.to_dict(), f, indent=2)
```

## 4. Express + swagger-jsdoc

swagger-jsdoc 从 JSDoc 注释生成 OpenAPI spec。

```javascript
const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: { title: 'My API', version: '1.0.0' },
  },
  apis: ['./routes/*.js'], // 包含 @openapi 注释的文件
};

const openapiSpecification = swaggerJsdoc(options);
const fs = require('fs');
fs.writeFileSync('openapi.json', JSON.stringify(openapiSpecification, null, 2));
```

## 5. NestJS + @nestjs/swagger

NestJS 通过装饰器自动生成 OpenAPI spec。

```typescript
// 从运行中的服务拉取（最简单）
// 启动后访问 http://localhost:3000/api-json

// 或编程式导出
import { NestFactory } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function exportOpenapi() {
  const app = await NestFactory.create(AppModule);
  const config = new DocumentBuilder()
    .setTitle('My API')
    .setVersion('1.0')
    .build();
  const document = SwaggerModule.createDocument(app, config);
  require('fs').writeFileSync('openapi.json', JSON.stringify(document, null, 2));
  await app.close();
}
exportOpenapi();
```

## 6. Spring Boot + springdoc-openapi

springdoc-openapi 自动扫描 Controller 生成 OpenAPI 3 spec。

**方式 A：从运行中的服务拉取**

```bash
# 默认端点
curl -s http://localhost:8080/v3/api-docs > openapi.json

# 指定 group
curl -s http://localhost:8080/v3/api-docs/user > openapi-user.json
```

**方式 B：编程式导出**

```java
@Autowired
private OpenAPI openAPI;

public void exportSpec() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    mapper.writeValue(new File("openapi.json"), openAPI);
}
```

**Maven 依赖**：
```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

## 7. Django + drf-spectacular

drf-spectacular 为 Django REST framework 生成 OpenAPI 3 spec。

**方式 A：管理命令**

```bash
python manage.py spectacular --color --file openapi.json
```

**方式 B：从运行中的服务拉取**

```bash
curl -s http://localhost:8000/api/schema/ > openapi.json
```

**方式 C：编程式**

```python
from drf_spectacular.generators import SchemaGenerator
generator = SchemaGenerator()
schema = generator.get_schema(request=None, public=True)

import json
with open("openapi.json", "w") as f:
    json.dump(schema, f, indent=2)
```

## 8. 手动构造

如果框架无原生 OpenAPI 支持（如纯 Express 无 swagger-jsdoc、老版本框架），可手动写 openapi.json：

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "My API",
    "version": "1.0.0",
    "description": "手动维护的 API spec"
  },
  "paths": {
    "/api/users": {
      "get": {
        "summary": "获取用户列表",
        "operationId": "listUsers",
        "responses": {
          "200": {
            "description": "成功",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": { "$ref": "#/components/schemas/User" }
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "User": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" }
        },
        "required": ["id", "name"]
      }
    }
  }
}
```

> 手动构造适合接口数少（< 20）的场景。接口多时建议引入框架的 OpenAPI 支持。

## 通用注意事项

1. **JSON 编码**：保存时用 `ensure_ascii=False` 保留中文（Python），或确保其他语言的序列化器不转义非 ASCII 字符。
2. **schema 完整性**：确保 `components.schemas` 中引用的所有 `$ref` 都能解析。
3. **版本一致性**：`openapi` 字段建议 `3.0.3` 或 `3.1.0`，避免过老的 2.x 版本（本工具不支持 Swagger 2.0）。
4. **环境隔离**：从 app 对象导出时，避免触发 DB 连接、外部 API 调用等副作用。
