from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class BaseBuilder(InvenioBaseClassPythonBuilder):
    def finish(self, **extra_kwargs):
        super().finish(
            parent_record=self.current_model.parent_record.definition, **extra_kwargs
        )
