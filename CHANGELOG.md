# 更新日志

> 说明：本项目尚未发布正式版本。以下内容列出“当前已支持的特性”和“未来可发展方向”，不按版本维护。

## 当前支持的特性

### 核心
- 轻量级 DataClass 风格的数据建模（装饰器 @dataclass）
- 自定义字段类型系统：可声明字段、默认值、别名、必填与可选
- 字段访问方式：属性访问、字典风格访问、get(key, default)
- 实例序列化：to_dict()

### 已内置字段类型
- StringField（长度、正则、枚举等）
- NumberField（最小/最大值、枚举等）
- ListField（长度、元素类型校验、嵌套 dataclass 列表）
- 支持嵌套 dataclass 作为字段

### 验证能力
- 必填校验（包含 None 和空字符串场景）
- 长度约束（min_length, max_length）
- 数值范围（minvalue, maxvalue）
- 正则匹配（regex）
- 枚举限制（choices）
- 列表项类型与嵌套对象校验
- 自定义字段级验证（@validate 装饰器，支持跨字段逻辑）

### 自定义错误消息系统
- 在字段上通过 error_messages 定制错误消息
- 模板格式化：{min_length}、{maxvalue}、{choices} 等占位符
- 缺参容错：格式化参数缺失时优雅降级为原模板
- 多语言文案支持（示例含中英文）

### Getter/计算属性
- 支持定义 get_<field>() 自定义 getter，读取属性时自动应用
- Getter 优先级正确，避免递归访问

### 兼容性与质量保障
- Python 2.7 与 Python 3.x 双版本兼容（统一使用 .format 文本格式化）
- 完整测试覆盖：单元测试与示例脚本均通过
- 示例与文档齐全，便于快速上手

---

## 未来路线图（建议）

以下方向结合 Web 应用最佳实践、数据建模与校验经验提出，供后续演进参考：

### 1) 字段与类型系统扩展
- 更多内置字段：Email、URL、UUID、Decimal、Boolean、Date/DateTime、Timedelta、IPAddress、Enum
- 组合/联合类型：Union/OneOf、AllOf、AnyOf、Not 等复合约束
- 复杂集合类型：SetField、DictField（键/值类型校验）、TupleField（定长/变长）
- 工厂默认值（default_factory）与不可变字段（frozen/readonly）

### 2) 验证模型与约束增强
- 条件/依赖验证：If-Then-Else、基于其它字段值的动态约束
- 跨字段/对象级校验：唯一性、相互排斥、必需同时出现、范围关系
- 国际化与本地化：错误消息按 locale/时区/数字格式自动化
- 可配置的空值策略：空字符串/空列表/零值的标准化与归一化

### 3) 可用性与开发者体验
- 更丰富的错误结构：错误代码、路径、批量错误聚合、机器可读结构
- 校验前置/后置钩子（pre/post processing）、字段 transform（strip、lower、coerce）
- 更友好的调试输出与失败定位（附上下文样例）
- 配置系统：基于环境/文件的全局或局部校验策略

### 4) 集成与生态
- Schema 导入/导出：JSON Schema、OpenAPI/Swagger、Protobuf、Avro
- Web 框架集成：FastAPI/Flask/Django 的请求体验证与响应序列化
- ORM/ODM 集成：SQLAlchemy、Django ORM、MongoEngine（模型映射与约束同步）
- 表单/前端协作：表单自动生成、校验规则下发至前端（共享 Schema）

### 5) 性能与可观测性
- 校验缓存与重复子结构去重
- 批量数据校验优化（矢量化/并行）
- 度量指标与追踪（校验耗时、失败率、字段热点）

### 6) 安全与合规
- 输入标准化与清洗（XSS/SQL 注入字符清理的职责边界与建议）
- 隐私字段标记/脱敏（PII/敏感数据）
- 合规约束模板（如手机号/邮箱/身份证等区域性规范的可插拔规则）

---

> 注：在正式发布第一个版本（v1.0.0）之前，CHANGELOG 将继续以“特性清单 + 路线图”的形式维护。
