from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class TestServiceBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_tests_service"
    template = "test_service"

    def _get_output_module(self):
        return f'{self.current_model.definition["tests"]["module"]}.test_service'
