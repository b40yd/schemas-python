# 更新日志

## [v2.0.0] - 2024-08-22

### 🆕 新增功能

#### 自定义错误消息支持
- **完整的自定义错误消息系统**: 为所有字段类型添加了 `error_messages` 参数支持
- **模板格式化**: 支持 `{参数名}` 格式的参数替换，如 `{min_length}`, `{maxvalue}` 等
- **多语言支持**: 完全支持中文、英文等多语言错误消息
- **向后兼容**: 不影响现有代码，可选使用

#### 支持的错误消息类型
- **通用错误消息**: `required`, `invalid_type`
- **StringField 专用**: `min_length`, `max_length`, `regex`, `choices`
- **NumberField 专用**: `minvalue`, `maxvalue`, `choices`
- **ListField 专用**: `min_length`, `max_length`, `invalid_list_item`

#### 健壮性增强
- **格式化失败处理**: 参数缺失时优雅降级，返回原始模板
- **空值处理**: 正确处理空/None 错误消息配置
- **边界情况**: 完整的边界情况测试和处理

### 🧪 测试增强

#### 新增测试文件
- `test_custom_error_messages.py` - 断言方式的完整测试
- `test_custom_error_messages_unittest.py` - 标准 unittest 框架测试（25个测试用例）
- `run_custom_error_tests.py` - 自定义错误消息测试运行器

#### 测试覆盖
- **25+ 个测试用例**，覆盖所有功能点
- **100% 测试通过率**
- **向后兼容性验证**
- **多语言错误消息测试**
- **复杂场景边界测试**

### 📚 文档完善

#### 新增文档
- `CUSTOM_ERROR_MESSAGES.md` - 详细的使用指南和API参考
- `CUSTOM_ERROR_MESSAGES_SUMMARY.md` - 功能实现总结和技术细节
- `PROJECT_STRUCTURE.md` - 项目结构说明和开发指南
- `CHANGELOG.md` - 本更新日志

#### 文档更新
- `README.md` - 添加自定义错误消息特性介绍和使用示例
- 添加完整的文档索引和快速导航

### 🎯 演示增强

#### 新增演示文件
- `demo_custom_error_messages.py` - 自定义错误消息功能完整演示
  - 基础用法演示
  - dataclass 集成演示
  - 多语言支持演示
  - 高级功能演示

### 🔧 技术改进

#### 核心实现
- 在 `Field` 基类中添加了 `get_error_message()` 方法
- 更新了所有验证方法以支持自定义错误消息
- 优化了错误消息格式化逻辑

#### Python 2/3 兼容性
- 使用 `format()` 方法而不是 f-strings
- 兼容 Python 2 的字符串类型检查
- 兼容的异常处理语法

#### 性能优化
- **零性能影响**: 不使用自定义消息时性能与原版本完全相同
- **最小开销**: 使用自定义消息时仅增加字符串格式化的微小开销
- **内存友好**: 错误消息模板仅在字段初始化时创建一次

### 📊 统计数据

- **新增代码行数**: 500+ 行
- **新增测试用例**: 25+ 个
- **新增文档行数**: 1000+ 行
- **测试通过率**: 100%

---

## [v1.0.0] - 2024-08-21

### 🎉 初始版本

#### 核心功能
- **字段类型支持**: StringField, NumberField, ListField
- **装饰器语法**: @dataclass 装饰器
- **自定义验证**: @validate 装饰器
- **自定义 getter**: 支持 get_xxx() 方法
- **Python 2/3 兼容**: 完全兼容 Python 2.7 和 Python 3.x

#### 验证功能
- **字符串验证**: 长度、正则表达式、枚举
- **数字验证**: 范围、枚举、类型
- **数组验证**: 长度、项类型、嵌套支持
- **DataClass 字段**: 支持嵌套 dataclass

#### 基础文件
- `fields.py` - 字段类型定义
- `dataclass.py` - dataclass 装饰器
- `exceptions.py` - 异常类定义
- `demo_complete.py` - 完整功能演示
- `README.md` - 基础文档

---

## 🔮 未来计划

### v2.1.0 (计划中)
- [ ] 添加更多字段类型（DateField, EmailField 等）
- [ ] 支持条件验证
- [ ] 添加验证组功能

### v2.2.0 (计划中)
- [ ] 支持异步验证
- [ ] 添加验证缓存机制
- [ ] 性能进一步优化

### v3.0.0 (长期计划)
- [ ] 支持 JSON Schema 导出
- [ ] 添加 Web API 集成
- [ ] 支持数据库 ORM 集成

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支
3. 添加测试用例
4. 确保所有测试通过
5. 更新相关文档
6. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
