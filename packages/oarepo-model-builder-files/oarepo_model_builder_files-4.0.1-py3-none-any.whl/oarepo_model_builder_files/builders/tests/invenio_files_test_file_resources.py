from oarepo_model_builder_files.builders.parent_builder import InvenioFilesParentBuilder


class InvenioFilesTestFileResourcesBuilder(InvenioFilesParentBuilder):
    TYPE = "invenio_files_test_files_resources"
    template = "files-test-file-resources"

    def _get_output_module(self):
        return f'{self.current_model.definition["tests"]["module"]}.files.test_file_resources'
