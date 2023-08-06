import marshmallow as ma
from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType


class TestSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    extra_fixtures = ma.fields.List(
        ma.fields.String(),
        data_key="extra-fixtures",
        attribute="extra-fixtures",
        required=False,
        load_default=[],
    )

    extra_code = ma.fields.String(
        data_key="extra-code", attribute="extra-code", load_default=""
    )

    module = ma.fields.String(load_default="tests")


class ModelTestComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]

    class ModelSchema(ma.Schema):
        tests = ma.fields.Nested(TestSchema, load_default=lambda: TestSchema().load({}))


components = [ModelTestComponent]
