from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class TestResourceBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_tests_resource"
    template = "test_resource"

    def _get_output_module(self):
        return f'{self.current_model.definition["tests"]["module"]}.test_resource'
