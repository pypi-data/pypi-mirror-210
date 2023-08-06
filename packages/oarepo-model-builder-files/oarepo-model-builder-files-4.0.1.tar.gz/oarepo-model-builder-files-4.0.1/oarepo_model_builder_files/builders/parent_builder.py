from oarepo_model_builder_files.builders.base import BaseBuilder


class InvenioFilesParentBuilder(BaseBuilder):
    def _get_output_module(self):
        module = self.current_model.parent_record.definition[self.section]["module"]
        return module
