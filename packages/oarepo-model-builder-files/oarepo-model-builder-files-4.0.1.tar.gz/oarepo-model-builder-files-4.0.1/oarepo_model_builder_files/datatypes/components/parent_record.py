from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import (
    DefaultsModelComponent,
    RecordMetadataModelComponent,
    ServiceModelComponent,
)
from oarepo_model_builder.datatypes.components.model.utils import (
    append_array,
    prepend_array,
)


class ParentRecordComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [
        DefaultsModelComponent,
        RecordMetadataModelComponent,
        ServiceModelComponent,
    ]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if context["profile"] == "files":
            return
        prepend_array(datatype, "record-metadata", "base-classes", "RecordMetadataBase")
        prepend_array(datatype, "record-metadata", "base-classes", "db.Model")

        append_array(
            datatype,
            "record-metadata",
            "imports",
            {"import": "invenio_db.db"},
        )
        append_array(
            datatype,
            "record-metadata",
            "imports",
            {"import": "invenio_records.models.RecordMetadataBase"},
        )

        append_array(
            datatype,
            "service-config",
            "imports",
            {
                "import": "invenio_records_resources.services.records.components.FilesOptionsComponent"
            },
        )
        append_array(datatype, "service-config", "components", "FilesOptionsComponent")
