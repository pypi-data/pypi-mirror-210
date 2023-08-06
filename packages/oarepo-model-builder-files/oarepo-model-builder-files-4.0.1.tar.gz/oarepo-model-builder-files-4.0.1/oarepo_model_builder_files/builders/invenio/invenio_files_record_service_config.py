from oarepo_model_builder_files.builders.base import BaseBuilder


class InvenioRecordServiceConfigBuilder(BaseBuilder):
    TYPE = "invenio_files_record_service_config"
    section = "service-config"
    template = "files-service-config"
