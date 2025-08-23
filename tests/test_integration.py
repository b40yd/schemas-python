# -*- coding: utf-8 -*-
"""
集成测试 - 测试复杂场景和组件间交互
"""

import pytest
from schema_dataclass import (
    StringField,
    NumberField,
    ListField,
    ValidationError,
    dataclass,
    validate,
)


class TestNestedDataClass:
    """嵌套 DataClass 测试"""

    @pytest.fixture
    def nested_dataclasses(self):
        """创建嵌套的 dataclass 结构"""

        @dataclass
        class Address(object):
            street = StringField(min_length=1, max_length=100)
            city = StringField(min_length=1, max_length=50)
            zipcode = StringField(regex=r"^\d{5}$")

        @dataclass
        class Person(object):
            name = StringField(min_length=1, max_length=50)
            age = NumberField(minvalue=0, maxvalue=150)
            email = StringField(
                regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )

            @validate("name")
            def validate_name_alpha(self, name):
                if not name.replace(" ", "").isalpha():
                    raise ValidationError("Name must contain only letters and spaces")

        @dataclass
        class Company(object):
            name = StringField(min_length=1, max_length=100)
            address = Address  # dataclass 字段
            ceo = Person  # dataclass 字段
            employees = ListField(item_type=Person)  # 包含 dataclass 的列表字段

        return Address, Person, Company

    @pytest.mark.integration
    def test_nested_dataclass_creation(self, nested_dataclasses):
        """测试嵌套 dataclass 创建"""
        Address, Person, Company = nested_dataclasses

        company = Company(
            name="Tech Corp",
            address={
                "street": "123 Main St",
                "city": "San Francisco",
                "zipcode": "94105",
            },
            ceo={"name": "John Doe", "age": 45, "email": "john@techcorp.com"},
            employees=[
                {"name": "Alice Smith", "age": 30, "email": "alice@techcorp.com"},
                {"name": "Bob Johnson", "age": 28, "email": "bob@techcorp.com"},
            ],
        )

        # 验证公司信息
        assert company.name == "Tech Corp"

        # 验证地址信息（应该是 Address 实例）
        assert isinstance(company.address, Address)
        assert company.address.street == "123 Main St"
        assert company.address.city == "San Francisco"
        assert company.address.zipcode == "94105"

        # 验证 CEO 信息（应该是 Person 实例）
        assert isinstance(company.ceo, Person)
        assert company.ceo.name == "John Doe"
        assert company.ceo.age == 45
        assert company.ceo.email == "john@techcorp.com"

        # 验证员工信息（应该是 Person 实例列表）
        assert len(company.employees) == 2
        assert all(isinstance(emp, Person) for emp in company.employees)
        assert company.employees[0].name == "Alice Smith"
        assert company.employees[1].name == "Bob Johnson"

    @pytest.mark.integration
    def test_nested_dataclass_reassignment(self, nested_dataclasses):
        """测试嵌套 dataclass 重新赋值"""
        Address, Person, Company = nested_dataclasses

        company = Company(
            name="Tech Corp",
            address={
                "street": "123 Main St",
                "city": "San Francisco",
                "zipcode": "94105",
            },
            ceo={"name": "John Doe", "age": 45, "email": "john@techcorp.com"},
            employees=[],
        )

        # 重新赋值地址
        company.address = {
            "street": "456 Oak Ave",
            "city": "Los Angeles",
            "zipcode": "90210",
        }

        assert isinstance(company.address, Address)
        assert company.address.street == "456 Oak Ave"
        assert company.address.city == "Los Angeles"
        assert company.address.zipcode == "90210"

        # 重新赋值 CEO
        company.ceo = {"name": "Jane Wilson", "age": 38, "email": "jane@techcorp.com"}

        assert isinstance(company.ceo, Person)
        assert company.ceo.name == "Jane Wilson"
        assert company.ceo.age == 38
        assert company.ceo.email == "jane@techcorp.com"

    @pytest.mark.integration
    def test_nested_validation_errors(self, nested_dataclasses):
        """测试嵌套验证错误"""
        Address, Person, Company = nested_dataclasses

        # 测试无效邮编
        with pytest.raises(ValidationError) as exc_info:
            Company(
                name="Bad Corp",
                address={
                    "street": "123 Bad St",
                    "city": "Bad City",
                    "zipcode": "invalid",  # 无效邮编
                },
                ceo={"name": "Bad CEO", "age": 50, "email": "bad@example.com"},
                employees=[],
            )
        assert "does not match pattern" in str(exc_info.value)

        # 测试无效姓名（包含数字）
        with pytest.raises(ValidationError) as exc_info:
            Company(
                name="Bad Corp",
                address={
                    "street": "123 Bad St",
                    "city": "Bad City",
                    "zipcode": "12345",
                },
                ceo={
                    "name": "John123",
                    "age": 40,
                    "email": "john@example.com",
                },  # 包含数字
                employees=[],
            )
        assert "must contain only letters and spaces" in str(exc_info.value)

        # 测试无效邮箱
        with pytest.raises(ValidationError) as exc_info:
            Company(
                name="Bad Corp",
                address={
                    "street": "123 Bad St",
                    "city": "Bad City",
                    "zipcode": "12345",
                },
                ceo={"name": "Bad CEO", "age": 50, "email": "bad-email"},  # 无效邮箱
                employees=[],
            )
        assert "does not match pattern" in str(exc_info.value)

    @pytest.mark.integration
    def test_nested_to_dict(self, nested_dataclasses):
        """测试嵌套 to_dict 方法"""
        Address, Person, Company = nested_dataclasses

        company = Company(
            name="Tech Corp",
            address={
                "street": "123 Main St",
                "city": "San Francisco",
                "zipcode": "94105",
            },
            ceo={"name": "John Doe", "age": 45, "email": "john@techcorp.com"},
            employees=[
                {"name": "Alice Smith", "age": 30, "email": "alice@techcorp.com"}
            ],
        )

        company_dict = company.to_dict()

        # 验证结构
        assert isinstance(company_dict, dict)
        assert company_dict["name"] == "Tech Corp"

        # 验证嵌套字典
        assert isinstance(company_dict["address"], dict)
        assert company_dict["address"]["street"] == "123 Main St"

        assert isinstance(company_dict["ceo"], dict)
        assert company_dict["ceo"]["name"] == "John Doe"

        # 验证嵌套列表
        assert isinstance(company_dict["employees"], list)
        assert len(company_dict["employees"]) == 1
        assert isinstance(company_dict["employees"][0], dict)
        assert company_dict["employees"][0]["name"] == "Alice Smith"


class TestComplexValidationScenarios:
    """复杂验证场景测试"""

    @pytest.mark.integration
    @pytest.mark.validation
    def test_conditional_validation(self):
        """测试条件验证"""

        @dataclass
        class Product(object):
            name = StringField()
            category = StringField(choices=["electronics", "clothing", "books"])
            price = NumberField(minvalue=0)

            @validate("price")
            def validate_category_price_rules(self, price):
                """不同类别的价格规则"""
                category = self.__dict__.get("category")
                if category == "electronics" and price < 10:
                    raise ValidationError("Electronics must cost at least $10")
                elif category == "books" and price > 100:
                    raise ValidationError("Books cannot cost more than $100")

        # 测试有效产品
        electronics = Product(name="Phone", category="electronics", price=500)
        assert electronics.price == 500

        book = Product(name="Python Guide", category="books", price=50)
        assert book.price == 50

        # 测试无效电子产品价格
        with pytest.raises(ValidationError) as exc_info:
            Product(name="Cheap Electronics", category="electronics", price=5)
        assert "must cost at least $10" in str(exc_info.value)

        # 测试无效书籍价格
        with pytest.raises(ValidationError) as exc_info:
            Product(name="Expensive Book", category="books", price=150)
        assert "cannot cost more than $100" in str(exc_info.value)

    @pytest.mark.integration
    @pytest.mark.validation
    def test_cross_field_validation(self):
        """测试跨字段验证"""

        @dataclass
        class DateRange(object):
            start_date = StringField(regex=r"^\d{4}-\d{2}-\d{2}$")
            end_date = StringField(regex=r"^\d{4}-\d{2}-\d{2}$")

            @validate("end_date")
            def validate_date_order(self, end_date):
                """结束日期必须晚于开始日期"""
                start_date = self.__dict__.get("start_date")
                if start_date and end_date <= start_date:
                    raise ValidationError("End date must be after start date")

        # 测试有效日期范围
        date_range = DateRange(start_date="2023-01-01", end_date="2023-12-31")
        assert date_range.start_date == "2023-01-01"
        assert date_range.end_date == "2023-12-31"

        # 测试无效日期范围
        with pytest.raises(ValidationError) as exc_info:
            DateRange(start_date="2023-12-31", end_date="2023-01-01")
        assert "must be after start date" in str(exc_info.value)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_dataset_validation(self):
        """测试大数据集验证"""

        @dataclass
        class DataPoint(object):
            id = NumberField(minvalue=1)
            value = NumberField()
            category = StringField(choices=["A", "B", "C"])

        @dataclass
        class Dataset(object):
            name = StringField(min_length=1)
            points = ListField(item_type=DataPoint)

        # 创建大量数据点
        large_data = []
        for i in range(1000):
            large_data.append(
                {"id": i + 1, "value": i * 0.1, "category": ["A", "B", "C"][i % 3]}
            )

        # 测试大数据集创建和验证
        dataset = Dataset(name="Large Dataset", points=large_data)

        assert dataset.name == "Large Dataset"
        assert len(dataset.points) == 1000
        assert all(isinstance(point, DataPoint) for point in dataset.points)
        assert dataset.points[0].id == 1
        assert dataset.points[999].id == 1000


class TestErrorHandlingAndRecovery:
    """错误处理和恢复测试"""

    @pytest.mark.integration
    def test_partial_validation_failure(self):
        """测试部分验证失败"""

        @dataclass
        class MultiFieldClass(object):
            field1 = StringField(min_length=5)
            field2 = NumberField(minvalue=10)
            field3 = StringField(choices=["A", "B", "C"])

        # 第一个字段失败
        with pytest.raises(ValidationError):
            MultiFieldClass(field1="abc", field2=15, field3="A")

        # 第二个字段失败
        with pytest.raises(ValidationError):
            MultiFieldClass(field1="valid", field2=5, field3="A")

        # 第三个字段失败
        with pytest.raises(ValidationError):
            MultiFieldClass(field1="valid", field2=15, field3="D")

        # 所有字段有效
        obj = MultiFieldClass(field1="valid", field2=15, field3="A")
        assert obj.field1 == "valid"
        assert obj.field2 == 15
        assert obj.field3 == "A"

    @pytest.mark.integration
    def test_validation_error_context(self):
        """测试验证错误上下文"""

        @dataclass
        class NestedClass(object):
            items = ListField(item_type=NumberField(minvalue=0))

        # 测试列表项验证错误包含索引信息
        with pytest.raises(ValidationError) as exc_info:
            NestedClass(items=[1, 2, -3, 4])  # -3 无效

        error_message = str(exc_info.value)
        # 错误消息应该包含有用的上下文信息
        assert "must be at least" in error_message
