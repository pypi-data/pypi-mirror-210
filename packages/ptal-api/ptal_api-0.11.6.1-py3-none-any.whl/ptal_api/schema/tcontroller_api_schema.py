import sgqlc.types


tcontroller_api_schema = sgqlc.types.Schema()



########################################################################
# Scalars and Enumerations
########################################################################
Boolean = sgqlc.types.Boolean

class ConceptTransformConfigSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('description', 'id', 'systemRegistrationDate', 'systemUpdateDate')


class ConceptTransformTaskSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('config', 'createTime', 'state')


class ConceptTransformTaskState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('failed', 'ok', 'pending')


class ExportEntityType(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('concept', 'document')


class ExportTaskSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('createTime', 'exporter', 'state')


class ExportTaskState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('failed', 'ok', 'pending')


class ExporterSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('id', 'lastTaskTime', 'menuTitle', 'title')


Float = sgqlc.types.Float

ID = sgqlc.types.ID

Int = sgqlc.types.Int

class ItemState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('duplicate', 'failed', 'ok', 'pending')


class ItemsSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('priority', 'timestamp', 'topic')


class JSON(sgqlc.types.Scalar):
    __schema__ = tcontroller_api_schema


class KafkaTopicSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('activeMessages', 'configDescription', 'configId', 'description', 'duplicateMessages', 'failedMessages', 'okMessages', 'pendingMessages', 'pipelineIsActive', 'priority', 'stopped', 'systemRegistrationDate', 'systemUpdateDate', 'topic')


class Long(sgqlc.types.Scalar):
    __schema__ = tcontroller_api_schema


class MessagePriority(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('Background', 'High', 'Normal', 'VeryHigh')


class MessageSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('priority', 'timestamp')


class PipelineConfigSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('description', 'id', 'systemRegistrationDate', 'systemUpdateDate')


class SortDirection(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('ascending', 'descending')


String = sgqlc.types.String

class UnixTime(sgqlc.types.Scalar):
    __schema__ = tcontroller_api_schema


class Upload(sgqlc.types.Scalar):
    __schema__ = tcontroller_api_schema


class UserPipelineTransformSort(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('description', 'id', 'state', 'systemRegistrationDate', 'systemUpdateDate')


class UserServiceState(sgqlc.types.Enum):
    __schema__ = tcontroller_api_schema
    __choices__ = ('buildFailed', 'imageNotReady', 'noImage', 'ready')



########################################################################
# Input Objects
########################################################################
class ConceptTransformConfigFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('system_registration_date', 'system_update_date', 'creator_id', 'last_updater_id', 'title', 'description', 'can_transform_one_entity', 'can_transform_multiple_entities', 'can_transform_concept_type_ids', 'can_be_used')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')
    title = sgqlc.types.Field(String, graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')
    can_transform_one_entity = sgqlc.types.Field(Boolean, graphql_name='canTransformOneEntity')
    can_transform_multiple_entities = sgqlc.types.Field(Boolean, graphql_name='canTransformMultipleEntities')
    can_transform_concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='canTransformConceptTypeIds')
    can_be_used = sgqlc.types.Field(Boolean, graphql_name='canBeUsed')


class ConceptTransformConfigInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('title', 'description', 'concept_type_ids', 'can_transform_one_entity', 'can_transform_multiple_entities', 'priority')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    can_transform_one_entity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canTransformOneEntity')
    can_transform_multiple_entities = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canTransformMultipleEntities')
    priority = sgqlc.types.Field(Int, graphql_name='priority')


class ConceptTransformTaskFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('config', 'creator_id', 'state', 'id', 'system_registration_date')
    config = sgqlc.types.Field(ID, graphql_name='config')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    state = sgqlc.types.Field(ConceptTransformTaskState, graphql_name='state')
    id = sgqlc.types.Field(ID, graphql_name='id')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')


class ConceptTransformTaskInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('config', 'concept_ids')
    config = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='config')
    concept_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='conceptIds')


class ExportEntityInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('type', 'id')
    type = sgqlc.types.Field(sgqlc.types.non_null(ExportEntityType), graphql_name='type')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ExportTaskFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('exporter', 'creator_id', 'state', 'id', 'system_registration_date')
    exporter = sgqlc.types.Field(ID, graphql_name='exporter')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    state = sgqlc.types.Field(ExportTaskState, graphql_name='state')
    id = sgqlc.types.Field(ID, graphql_name='id')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')


class ExportTaskInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('entities', 'params')
    entities = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExportEntityInput))), graphql_name='entities')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')


class ExporterFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('can_export_document', 'can_export_concept', 'can_export_one_entity', 'can_export_multiple_entities', 'can_export_concept_type_ids', 'title', 'menu_title', 'creator_id', 'last_updater_id')
    can_export_document = sgqlc.types.Field(Boolean, graphql_name='canExportDocument')
    can_export_concept = sgqlc.types.Field(Boolean, graphql_name='canExportConcept')
    can_export_one_entity = sgqlc.types.Field(Boolean, graphql_name='canExportOneEntity')
    can_export_multiple_entities = sgqlc.types.Field(Boolean, graphql_name='canExportMultipleEntities')
    can_export_concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='canExportConceptTypeIds')
    title = sgqlc.types.Field(String, graphql_name='title')
    menu_title = sgqlc.types.Field(String, graphql_name='menuTitle')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')


class ExporterInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('menu_title', 'description', 'default_params', 'can_export_one_entity', 'can_export_multiple_entities', 'concept_type_ids')
    menu_title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='menuTitle')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    default_params = sgqlc.types.Field(JSON, graphql_name='defaultParams')
    can_export_one_entity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportOneEntity')
    can_export_multiple_entities = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportMultipleEntities')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')


class ItemsFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('input_text', 'interval', 'topic', 'state')
    input_text = sgqlc.types.Field(String, graphql_name='inputText')
    interval = sgqlc.types.Field('TimestampInterval', graphql_name='interval')
    topic = sgqlc.types.Field(String, graphql_name='topic')
    state = sgqlc.types.Field(ItemState, graphql_name='state')


class KafkaTopicFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('name', 'system_registration_date', 'system_update_date', 'creator_id', 'last_updater_id', 'description', 'pipeline_config', 'pipeline_config_description', 'stopped', 'has_pipeline_config', 'pipeline_is_active')
    name = sgqlc.types.Field(String, graphql_name='name')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')
    description = sgqlc.types.Field(String, graphql_name='description')
    pipeline_config = sgqlc.types.Field(ID, graphql_name='pipelineConfig')
    pipeline_config_description = sgqlc.types.Field(String, graphql_name='pipelineConfigDescription')
    stopped = sgqlc.types.Field(Boolean, graphql_name='stopped')
    has_pipeline_config = sgqlc.types.Field(Boolean, graphql_name='hasPipelineConfig')
    pipeline_is_active = sgqlc.types.Field(Boolean, graphql_name='pipelineIsActive')


class KafkaTopicUpdate(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description', 'clear_description', 'pipeline', 'clear_pipeline', 'priority', 'request_timeout_ms', 'clear_request_timeout_ms', 'move_to_on_timeout', 'clear_move_to_on_timeout', 'stopped')
    description = sgqlc.types.Field(String, graphql_name='description')
    clear_description = sgqlc.types.Field(Boolean, graphql_name='clearDescription')
    pipeline = sgqlc.types.Field('PipelineSetupInput', graphql_name='pipeline')
    clear_pipeline = sgqlc.types.Field(Boolean, graphql_name='clearPipeline')
    priority = sgqlc.types.Field(Int, graphql_name='priority')
    request_timeout_ms = sgqlc.types.Field(Int, graphql_name='requestTimeoutMs')
    clear_request_timeout_ms = sgqlc.types.Field(Boolean, graphql_name='clearRequestTimeoutMs')
    move_to_on_timeout = sgqlc.types.Field(String, graphql_name='moveToOnTimeout')
    clear_move_to_on_timeout = sgqlc.types.Field(Boolean, graphql_name='clearMoveToOnTimeout')
    stopped = sgqlc.types.Field(Boolean, graphql_name='stopped')


class MessageFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'input_text', 'parent_id', 'parent_or_self_id')
    id = sgqlc.types.Field(String, graphql_name='id')
    input_text = sgqlc.types.Field(String, graphql_name='inputText')
    parent_id = sgqlc.types.Field(String, graphql_name='parentId')
    parent_or_self_id = sgqlc.types.Field(String, graphql_name='parentOrSelfId')


class PipelineConfigFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('in_type', 'system_registration_date', 'system_update_date', 'creator_id', 'last_updater_id', 'description', 'has_transform', 'has_transforms')
    in_type = sgqlc.types.Field(String, graphql_name='inType')
    system_registration_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field('TimestampInterval', graphql_name='systemUpdateDate')
    creator_id = sgqlc.types.Field(ID, graphql_name='creatorId')
    last_updater_id = sgqlc.types.Field(ID, graphql_name='lastUpdaterId')
    description = sgqlc.types.Field(String, graphql_name='description')
    has_transform = sgqlc.types.Field(ID, graphql_name='hasTransform')
    has_transforms = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='hasTransforms')


class PipelineConfigInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'description', 'transforms')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PipelineTransformSetupInput'))), graphql_name='transforms')


class PipelineSetupInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('pipeline_config',)
    pipeline_config = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='pipelineConfig')


class PipelineTransformFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('in_type',)
    in_type = sgqlc.types.Field(String, graphql_name='inType')


class PipelineTransformSetupInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'params')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')


class TimestampInterval(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('start', 'end')
    start = sgqlc.types.Field(UnixTime, graphql_name='start')
    end = sgqlc.types.Field(UnixTime, graphql_name='end')


class UserPipelineTransformFilter(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('in_type',)
    in_type = sgqlc.types.Field(String, graphql_name='inType')


class UserServiceEnvironmentVariableInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('name', 'value')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class UserServiceInput(sgqlc.types.Input):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('mem_limit', 'mem_request', 'cpu_limit', 'cpu_request', 'max_pods', 'environment')
    mem_limit = sgqlc.types.Field(Int, graphql_name='memLimit')
    mem_request = sgqlc.types.Field(Int, graphql_name='memRequest')
    cpu_limit = sgqlc.types.Field(Int, graphql_name='cpuLimit')
    cpu_request = sgqlc.types.Field(Int, graphql_name='cpuRequest')
    max_pods = sgqlc.types.Field(Int, graphql_name='maxPods')
    environment = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(UserServiceEnvironmentVariableInput)), graphql_name='environment')



########################################################################
# Output Objects and Interfaces
########################################################################
class RecordInterface(sgqlc.types.Interface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('system_registration_date', 'system_update_date', 'creator', 'last_updater')
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='systemRegistrationDate')
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name='systemUpdateDate')
    creator = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='creator')
    last_updater = sgqlc.types.Field('User', graphql_name='lastUpdater')


class ActiveMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ActiveMessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ActiveMessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('MessageInProgress'), graphql_name='info')


class CompletedOkMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CompletedOkMessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class CompletedOkMessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('MessageOk'), graphql_name='info')


class ConceptTransformConfigList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('configs', 'total')
    configs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTransformConfig'))), graphql_name='configs')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ConceptTransformResults(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('concepts', 'error')
    concepts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='concepts')
    error = sgqlc.types.Field(String, graphql_name='error')


class ConceptTransformTaskList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('tasks', 'total')
    tasks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ConceptTransformTask'))), graphql_name='tasks')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DuplicateMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DuplicateMessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class DuplicateMessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('MessageDuplicate'), graphql_name='info')


class ExportEntity(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('type', 'id')
    type = sgqlc.types.Field(sgqlc.types.non_null(ExportEntityType), graphql_name='type')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ExportResults(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('file', 'message', 'error')
    file = sgqlc.types.Field(String, graphql_name='file')
    message = sgqlc.types.Field(String, graphql_name='message')
    error = sgqlc.types.Field(String, graphql_name='error')


class ExportTaskList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('tasks', 'total')
    tasks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ExportTask'))), graphql_name='tasks')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class ExporterList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('exporters', 'total')
    exporters = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Exporter'))), graphql_name='exporters')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class FailedMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class Item(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('job_id', 'timestamp', '_uuid', '_url', 'id', 'attachments_num', 'status', 'item')
    job_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='job_id')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='timestamp')
    _uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='_uuid')
    _url = sgqlc.types.Field(String, graphql_name='_url')
    id = sgqlc.types.Field(String, graphql_name='id')
    attachments_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='attachmentsNum')
    status = sgqlc.types.Field(sgqlc.types.non_null('MessageStatus'), graphql_name='status')
    item = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='item')


class ItemsList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('total', 'items')
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='total')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Item))), graphql_name='items')


class JobIds(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('job_id', 'task_id', 'periodic_job_id', 'periodic_task_id')
    job_id = sgqlc.types.Field(ID, graphql_name='jobId')
    task_id = sgqlc.types.Field(ID, graphql_name='taskId')
    periodic_job_id = sgqlc.types.Field(ID, graphql_name='periodicJobId')
    periodic_task_id = sgqlc.types.Field(ID, graphql_name='periodicTaskId')


class JobMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('job_id', 'metrics')
    job_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='jobId')
    metrics = sgqlc.types.Field(sgqlc.types.non_null('MessageMetrics'), graphql_name='metrics')


class KafkaTopicList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('topics', 'total')
    topics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('KafkaTopic'))), graphql_name='topics')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class KafkaTopicMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'lag', 'active_messages', 'pipeline_is_active', 'failed', 'ok', 'ok_cumulative', 'duplicate', 'pending')
    messages = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='messages')
    lag = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='lag')
    active_messages = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='activeMessages')
    pipeline_is_active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='pipelineIsActive')
    failed = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='failed')
    ok = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='ok')
    ok_cumulative = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='okCumulative')
    duplicate = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='duplicate')
    pending = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='pending')


class MessageDuplicate(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'start_time', 'finish_time', 'topic', 'result', 'original_id', 'deleted', 'message', 'priority')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    start_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='startTime')
    finish_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='finishTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')
    result = sgqlc.types.Field(String, graphql_name='result')
    original_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='originalId')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleted')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')


class MessageError(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('description',)
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')


class MessageFailed(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'start_time', 'finish_time', 'topic', 'stage', 'error', 'deleted', 'duplicate_of', 'message', 'priority')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    start_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='startTime')
    finish_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='finishTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')
    stage = sgqlc.types.Field(sgqlc.types.non_null('PipelineTransformSetup'), graphql_name='stage')
    error = sgqlc.types.Field(sgqlc.types.non_null(MessageError), graphql_name='error')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleted')
    duplicate_of = sgqlc.types.Field(String, graphql_name='duplicateOf')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')


class MessageInProgress(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'start_time', 'topic', 'stage', 'message', 'priority')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    start_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='startTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')
    stage = sgqlc.types.Field(sgqlc.types.non_null('PipelineTransformSetup'), graphql_name='stage')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')


class MessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class MessageMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('pending', 'failed', 'ok', 'duplicate')
    pending = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='pending')
    failed = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='failed')
    ok = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='ok')
    duplicate = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='duplicate')


class MessageNotHandled(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'topic', 'not_handled', 'message', 'priority')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')
    not_handled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='notHandled')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')


class MessageOk(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('create_time', 'start_time', 'finish_time', 'topic', 'result', 'deleted', 'message', 'priority')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    start_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='startTime')
    finish_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='finishTime')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')
    result = sgqlc.types.Field(String, graphql_name='result')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleted')
    message = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='message')
    priority = sgqlc.types.Field(sgqlc.types.non_null(MessagePriority), graphql_name='priority')


class MessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('MessageStatusInfo'), graphql_name='info')


class MessageUnknown(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('unknown',)
    unknown = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='unknown')


class Mutation(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('add_pipeline_config', 'copy_pipeline_config', 'import_pipeline_config', 'update_pipeline_config', 'delete_pipeline_config', 'put_kafka_topic', 'update_kafka_topics', 'delete_kafka_topic', 'retry_failed_in_topic', 'retry_failed_message', 'copy_pending_to_kafka', 'reprocess_message', 'reprocess_messages', 'update_exporter', 'add_exporter_task', 'cancel_export_task', 'add_concept_transform_config', 'copy_concept_transform_config', 'update_concept_transform_config', 'update_concept_transform_config_transforms', 'delete_concept_transform_config', 'add_concept_transform_task', 'cancel_concept_transform_task', 'add_user_pipeline_transform', 'update_user_pipeline_transform', 'delete_user_pipeline_transform', 'service_stats', 'add_message')
    add_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='addPipelineConfig', args=sgqlc.types.ArgDict((
        ('description', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='description', default=None)),
        ('transforms', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransformSetupInput))), graphql_name='transforms', default=None)),
))
    )
    copy_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='copyPipelineConfig', args=sgqlc.types.ArgDict((
        ('source_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='sourceId', default=None)),
        ('description', sgqlc.types.Arg(String, graphql_name='description', default=None)),
))
    )
    import_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='importPipelineConfig', args=sgqlc.types.ArgDict((
        ('export', sgqlc.types.Arg(sgqlc.types.non_null(Upload), graphql_name='export', default=None)),
))
    )
    update_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='updatePipelineConfig', args=sgqlc.types.ArgDict((
        ('pipeline_config', sgqlc.types.Arg(sgqlc.types.non_null(PipelineConfigInput), graphql_name='pipelineConfig', default=None)),
))
    )
    delete_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='deletePipelineConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    put_kafka_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='putKafkaTopic', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
        ('description', sgqlc.types.Arg(String, graphql_name='description', default=None)),
        ('pipeline', sgqlc.types.Arg(PipelineSetupInput, graphql_name='pipeline', default=None)),
        ('priority', sgqlc.types.Arg(Int, graphql_name='priority', default=0)),
        ('request_timeout_ms', sgqlc.types.Arg(Int, graphql_name='requestTimeoutMs', default=None)),
        ('move_to_on_timeout', sgqlc.types.Arg(String, graphql_name='moveToOnTimeout', default=None)),
        ('stopped', sgqlc.types.Arg(Boolean, graphql_name='stopped', default=False)),
))
    )
    update_kafka_topics = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='updateKafkaTopics', args=sgqlc.types.ArgDict((
        ('topics', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='topics', default=None)),
        ('update', sgqlc.types.Arg(sgqlc.types.non_null(KafkaTopicUpdate), graphql_name='update', default=None)),
))
    )
    delete_kafka_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='deleteKafkaTopic', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    retry_failed_in_topic = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='retryFailedInTopic', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    retry_failed_message = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='retryFailedMessage', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    copy_pending_to_kafka = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='copyPendingToKafka', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    reprocess_message = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='reprocessMessage', args=sgqlc.types.ArgDict((
        ('message_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='messageId', default=None)),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
        ('use_kb', sgqlc.types.Arg(Boolean, graphql_name='useKb', default=False)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
))
    )
    reprocess_messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='reprocessMessages', args=sgqlc.types.ArgDict((
        ('message_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='messageIds', default=None)),
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
        ('use_kb', sgqlc.types.Arg(Boolean, graphql_name='useKb', default=False)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
))
    )
    update_exporter = sgqlc.types.Field(sgqlc.types.non_null('Exporter'), graphql_name='updateExporter', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('data', sgqlc.types.Arg(sgqlc.types.non_null(ExporterInput), graphql_name='data', default=None)),
))
    )
    add_exporter_task = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='addExporterTask', args=sgqlc.types.ArgDict((
        ('exporter', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='exporter', default=None)),
        ('task', sgqlc.types.Arg(sgqlc.types.non_null(ExportTaskInput), graphql_name='task', default=None)),
))
    )
    cancel_export_task = sgqlc.types.Field(sgqlc.types.non_null('ExportTask'), graphql_name='cancelExportTask', args=sgqlc.types.ArgDict((
        ('task_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='taskId', default=None)),
))
    )
    add_concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='addConceptTransformConfig', args=sgqlc.types.ArgDict((
        ('concept_transform', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTransformConfigInput), graphql_name='conceptTransform', default=None)),
))
    )
    copy_concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='copyConceptTransformConfig', args=sgqlc.types.ArgDict((
        ('source_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='sourceId', default=None)),
        ('title', sgqlc.types.Arg(String, graphql_name='title', default=None)),
))
    )
    update_concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='updateConceptTransformConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('concept_transform', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTransformConfigInput), graphql_name='conceptTransform', default=None)),
))
    )
    update_concept_transform_config_transforms = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='updateConceptTransformConfigTransforms', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('transforms', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransformSetupInput))), graphql_name='transforms', default=None)),
))
    )
    delete_concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='deleteConceptTransformConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    add_concept_transform_task = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='addConceptTransformTask', args=sgqlc.types.ArgDict((
        ('task', sgqlc.types.Arg(sgqlc.types.non_null(ConceptTransformTaskInput), graphql_name='task', default=None)),
))
    )
    cancel_concept_transform_task = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformTask'), graphql_name='cancelConceptTransformTask', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    add_user_pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransform'), graphql_name='addUserPipelineTransform', args=sgqlc.types.ArgDict((
        ('description', sgqlc.types.Arg(String, graphql_name='description', default=None)),
        ('service_image', sgqlc.types.Arg(Upload, graphql_name='serviceImage', default=None)),
        ('service', sgqlc.types.Arg(UserServiceInput, graphql_name='service', default=None)),
))
    )
    update_user_pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransform'), graphql_name='updateUserPipelineTransform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('description', sgqlc.types.Arg(String, graphql_name='description', default=None)),
        ('service_image', sgqlc.types.Arg(Upload, graphql_name='serviceImage', default=None)),
        ('service', sgqlc.types.Arg(UserServiceInput, graphql_name='service', default=None)),
))
    )
    delete_user_pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransform'), graphql_name='deleteUserPipelineTransform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    service_stats = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ServiceStats'))), graphql_name='serviceStats', args=sgqlc.types.ArgDict((
        ('reset', sgqlc.types.Arg(Boolean, graphql_name='reset', default=False)),
))
    )
    add_message = sgqlc.types.Field(sgqlc.types.non_null(MessageStatus), graphql_name='addMessage', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='topic', default=None)),
        ('message', sgqlc.types.Arg(sgqlc.types.non_null(JSON), graphql_name='message', default=None)),
        ('priority', sgqlc.types.Arg(MessagePriority, graphql_name='priority', default='Normal')),
))
    )


class ParamsSchema(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('schema', 'ui_schema')
    schema = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='schema')
    ui_schema = sgqlc.types.Field(JSON, graphql_name='uiSchema')


class PendingMessageList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('messages', 'total')
    messages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PendingMessageStatus'))), graphql_name='messages')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class PendingMessageStatus(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'info')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    info = sgqlc.types.Field(sgqlc.types.non_null('PendingMessageStatusInfo'), graphql_name='info')


class PeriodicJobMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('periodic_job_id', 'metrics')
    periodic_job_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='periodicJobId')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(MessageMetrics), graphql_name='metrics')


class PeriodicTaskMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('periodic_task_id', 'metrics')
    periodic_task_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='periodicTaskId')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(MessageMetrics), graphql_name='metrics')


class PipelineConfigList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('pipeline_configs', 'total')
    pipeline_configs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PipelineConfig'))), graphql_name='pipelineConfigs')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class PipelineSetup(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('pipeline_config',)
    pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='pipelineConfig')


class PipelineTransform(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'description', 'in_type', 'out_type', 'params_schema', 'version')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    in_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='inType')
    out_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='outType')
    params_schema = sgqlc.types.Field(sgqlc.types.non_null(ParamsSchema), graphql_name='paramsSchema')
    version = sgqlc.types.Field(String, graphql_name='version')


class PipelineTransformList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('transforms', 'total')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransform))), graphql_name='transforms')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class PipelineTransformSetup(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'params', 'transform')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')
    transform = sgqlc.types.Field(sgqlc.types.non_null(PipelineTransform), graphql_name='transform')


class Query(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('pipeline_transforms', 'pipeline_transform', 'pipeline_configs', 'pipeline_config', 'export_pipeline_config', 'kafka_pipeline_start_type', 'kafka_topics', 'kafka_topic', 'message_status', 'message_topic', 'message_statuses', 'message_source_available', 'failed_messages', 'pending_messages', 'active_messages', 'completed_ok_messages', 'duplicate_messages', 'messages_by_parent_id', 'exporter', 'exporters', 'export_task', 'export_tasks', 'job_items2', 'periodic_job_items2', 'task_items2', 'periodic_task_items2', 'job_ids_by_message_uuid2', 'job_metrics2', 'periodic_job_metrics2', 'task_metrics2', 'periodic_task_metrics2', 'concept_transform_configs', 'concept_transform_config', 'concept_transform_message_type', 'concept_transform_task', 'concept_transform_tasks', 'user_pipeline_transforms', 'user_pipeline_transform', 'debug_dump_extensions')
    pipeline_transforms = sgqlc.types.Field(sgqlc.types.non_null(PipelineTransformList), graphql_name='pipelineTransforms', args=sgqlc.types.ArgDict((
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('filter', sgqlc.types.Arg(PipelineTransformFilter, graphql_name='filter', default=None)),
))
    )
    pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null(PipelineTransform), graphql_name='pipelineTransform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    pipeline_configs = sgqlc.types.Field(sgqlc.types.non_null(PipelineConfigList), graphql_name='pipelineConfigs', args=sgqlc.types.ArgDict((
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('filter', sgqlc.types.Arg(PipelineConfigFilter, graphql_name='filter', default=None)),
        ('sort_by', sgqlc.types.Arg(PipelineConfigSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
))
    )
    pipeline_config = sgqlc.types.Field(sgqlc.types.non_null('PipelineConfig'), graphql_name='pipelineConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    export_pipeline_config = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='exportPipelineConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    kafka_pipeline_start_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='kafkaPipelineStartType')
    kafka_topics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicList), graphql_name='kafkaTopics', args=sgqlc.types.ArgDict((
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('filter', sgqlc.types.Arg(KafkaTopicFilter, graphql_name='filter', default=None)),
        ('sort_by', sgqlc.types.Arg(KafkaTopicSort, graphql_name='sortBy', default='topic')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
))
    )
    kafka_topic = sgqlc.types.Field(sgqlc.types.non_null('KafkaTopic'), graphql_name='kafkaTopic', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
))
    )
    message_status = sgqlc.types.Field(sgqlc.types.non_null(MessageStatus), graphql_name='messageStatus', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    message_topic = sgqlc.types.Field(ID, graphql_name='messageTopic', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    message_statuses = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MessageStatus))), graphql_name='messageStatuses', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    message_source_available = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='messageSourceAvailable', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    failed_messages = sgqlc.types.Field(sgqlc.types.non_null(FailedMessageList), graphql_name='failedMessages', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(MessageSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
))
    )
    pending_messages = sgqlc.types.Field(sgqlc.types.non_null(PendingMessageList), graphql_name='pendingMessages', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(ItemsSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
))
    )
    active_messages = sgqlc.types.Field(sgqlc.types.non_null(ActiveMessageList), graphql_name='activeMessages', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(ID, graphql_name='topic', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(ItemsSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
))
    )
    completed_ok_messages = sgqlc.types.Field(sgqlc.types.non_null(CompletedOkMessageList), graphql_name='completedOkMessages', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(MessageSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
))
    )
    duplicate_messages = sgqlc.types.Field(sgqlc.types.non_null(DuplicateMessageList), graphql_name='duplicateMessages', args=sgqlc.types.ArgDict((
        ('topic', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='topic', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(MessageSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
))
    )
    messages_by_parent_id = sgqlc.types.Field(sgqlc.types.non_null(MessageList), graphql_name='messagesByParentId', args=sgqlc.types.ArgDict((
        ('parent_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='parentId', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(ItemsSort, graphql_name='sortBy', default='timestamp')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(MessageFilter, graphql_name='filter', default=None)),
))
    )
    exporter = sgqlc.types.Field(sgqlc.types.non_null('Exporter'), graphql_name='exporter', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    exporters = sgqlc.types.Field(sgqlc.types.non_null(ExporterList), graphql_name='exporters', args=sgqlc.types.ArgDict((
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(ExporterSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
        ('filter', sgqlc.types.Arg(ExporterFilter, graphql_name='filter', default=None)),
))
    )
    export_task = sgqlc.types.Field(sgqlc.types.non_null('ExportTask'), graphql_name='exportTask', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    export_tasks = sgqlc.types.Field(sgqlc.types.non_null(ExportTaskList), graphql_name='exportTasks', args=sgqlc.types.ArgDict((
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(ExportTaskSort, graphql_name='sortBy', default='createTime')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(ExportTaskFilter, graphql_name='filter', default=None)),
))
    )
    job_items2 = sgqlc.types.Field(sgqlc.types.non_null(ItemsList), graphql_name='jobItems2', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('items_filter', sgqlc.types.Arg(ItemsFilter, graphql_name='itemsFilter', default={'inputText': None, 'interval': None, 'topic': None, 'state': None})),
        ('items_sort', sgqlc.types.Arg(ItemsSort, graphql_name='itemsSort', default='timestamp')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=10)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    periodic_job_items2 = sgqlc.types.Field(sgqlc.types.non_null(ItemsList), graphql_name='periodicJobItems2', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('items_filter', sgqlc.types.Arg(ItemsFilter, graphql_name='itemsFilter', default={'inputText': None, 'interval': None, 'topic': None, 'state': None})),
        ('items_sort', sgqlc.types.Arg(ItemsSort, graphql_name='itemsSort', default='timestamp')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=10)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    task_items2 = sgqlc.types.Field(sgqlc.types.non_null(ItemsList), graphql_name='taskItems2', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('items_filter', sgqlc.types.Arg(ItemsFilter, graphql_name='itemsFilter', default={'inputText': None, 'interval': None, 'topic': None, 'state': None})),
        ('items_sort', sgqlc.types.Arg(ItemsSort, graphql_name='itemsSort', default='timestamp')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=10)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    periodic_task_items2 = sgqlc.types.Field(sgqlc.types.non_null(ItemsList), graphql_name='periodicTaskItems2', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('items_filter', sgqlc.types.Arg(ItemsFilter, graphql_name='itemsFilter', default={'inputText': None, 'interval': None, 'topic': None, 'state': None})),
        ('items_sort', sgqlc.types.Arg(ItemsSort, graphql_name='itemsSort', default='timestamp')),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=10)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=0)),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
))
    )
    job_ids_by_message_uuid2 = sgqlc.types.Field(JobIds, graphql_name='jobIdsByMessageUUID2', args=sgqlc.types.ArgDict((
        ('message_uuid', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='messageUUID', default=None)),
))
    )
    job_metrics2 = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(JobMetrics))), graphql_name='jobMetrics2', args=sgqlc.types.ArgDict((
        ('job_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='jobIds', default=None)),
))
    )
    periodic_job_metrics2 = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PeriodicJobMetrics))), graphql_name='periodicJobMetrics2', args=sgqlc.types.ArgDict((
        ('periodic_job_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='periodicJobIds', default=None)),
))
    )
    task_metrics2 = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TaskMetrics'))), graphql_name='taskMetrics2', args=sgqlc.types.ArgDict((
        ('task_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='taskIds', default=None)),
))
    )
    periodic_task_metrics2 = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PeriodicTaskMetrics))), graphql_name='periodicTaskMetrics2', args=sgqlc.types.ArgDict((
        ('periodic_task_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='periodicTaskIds', default=None)),
))
    )
    concept_transform_configs = sgqlc.types.Field(sgqlc.types.non_null(ConceptTransformConfigList), graphql_name='conceptTransformConfigs', args=sgqlc.types.ArgDict((
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('filter', sgqlc.types.Arg(ConceptTransformConfigFilter, graphql_name='filter', default=None)),
        ('sort_by', sgqlc.types.Arg(ConceptTransformConfigSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='ascending')),
))
    )
    concept_transform_config = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformConfig'), graphql_name='conceptTransformConfig', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_transform_message_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='conceptTransformMessageType')
    concept_transform_task = sgqlc.types.Field(sgqlc.types.non_null('ConceptTransformTask'), graphql_name='conceptTransformTask', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    concept_transform_tasks = sgqlc.types.Field(sgqlc.types.non_null(ConceptTransformTaskList), graphql_name='conceptTransformTasks', args=sgqlc.types.ArgDict((
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(ConceptTransformTaskSort, graphql_name='sortBy', default='createTime')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(ConceptTransformTaskFilter, graphql_name='filter', default=None)),
))
    )
    user_pipeline_transforms = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransformList'), graphql_name='userPipelineTransforms', args=sgqlc.types.ArgDict((
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('sort_by', sgqlc.types.Arg(UserPipelineTransformSort, graphql_name='sortBy', default='id')),
        ('sort_direction', sgqlc.types.Arg(SortDirection, graphql_name='sortDirection', default='descending')),
        ('filter', sgqlc.types.Arg(UserPipelineTransformFilter, graphql_name='filter', default=None)),
))
    )
    user_pipeline_transform = sgqlc.types.Field(sgqlc.types.non_null('UserPipelineTransform'), graphql_name='userPipelineTransform', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    debug_dump_extensions = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='debugDumpExtensions')


class ServiceStats(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('name', 'duration', 'load', 'ok_requests', 'failed_requests', 'ok_request_max_duration')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    duration = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='duration')
    load = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='load')
    ok_requests = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='okRequests')
    failed_requests = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='failedRequests')
    ok_request_max_duration = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='okRequestMaxDuration')


class TaskMetrics(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('task_id', 'metrics')
    task_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='taskId')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(MessageMetrics), graphql_name='metrics')


class User(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class UserPipelineTransformList(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('transforms', 'total')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UserPipelineTransform'))), graphql_name='transforms')
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')


class UserService(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('mem_limit', 'mem_request', 'cpu_limit', 'cpu_request', 'max_pods', 'state', 'environment')
    mem_limit = sgqlc.types.Field(Int, graphql_name='memLimit')
    mem_request = sgqlc.types.Field(Int, graphql_name='memRequest')
    cpu_limit = sgqlc.types.Field(Int, graphql_name='cpuLimit')
    cpu_request = sgqlc.types.Field(Int, graphql_name='cpuRequest')
    max_pods = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='maxPods')
    state = sgqlc.types.Field(sgqlc.types.non_null(UserServiceState), graphql_name='state')
    environment = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UserServiceEnvironmentVariable')), graphql_name='environment')


class UserServiceEnvironmentVariable(sgqlc.types.Type):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('name', 'value')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class ConceptTransformConfig(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'title', 'description', 'concept_type_ids', 'can_transform_one_entity', 'can_transform_multiple_entities', 'transforms', 'last_task_time', 'metrics', 'priority', 'deleted')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    can_transform_one_entity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canTransformOneEntity')
    can_transform_multiple_entities = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canTransformMultipleEntities')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransformSetup))), graphql_name='transforms')
    last_task_time = sgqlc.types.Field(UnixTime, graphql_name='lastTaskTime')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicMetrics), graphql_name='metrics')
    priority = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='priority')
    deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleted')


class ConceptTransformTask(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'concept_ids', 'state', 'active', 'result', 'config')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    concept_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='conceptIds')
    state = sgqlc.types.Field(sgqlc.types.non_null(ConceptTransformTaskState), graphql_name='state')
    active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='active')
    result = sgqlc.types.Field(ConceptTransformResults, graphql_name='result')
    config = sgqlc.types.Field(ConceptTransformConfig, graphql_name='config')


class ExportTask(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'entities', 'params', 'state', 'active', 'result', 'create_time', 'exporter')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    entities = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExportEntity))), graphql_name='entities')
    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')
    state = sgqlc.types.Field(sgqlc.types.non_null(ExportTaskState), graphql_name='state')
    active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='active')
    result = sgqlc.types.Field(ExportResults, graphql_name='result')
    create_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name='createTime')
    exporter = sgqlc.types.Field('Exporter', graphql_name='exporter')


class Exporter(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'title', 'menu_title', 'description', 'params_schema', 'default_params_schema', 'default_params', 'concept_type_ids', 'can_export_document', 'can_export_concept', 'can_export_one_entity', 'can_export_multiple_entities', 'last_task_time', 'metrics')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    menu_title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='menuTitle')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    params_schema = sgqlc.types.Field(sgqlc.types.non_null(ParamsSchema), graphql_name='paramsSchema')
    default_params_schema = sgqlc.types.Field(sgqlc.types.non_null(ParamsSchema), graphql_name='defaultParamsSchema')
    default_params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='defaultParams')
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='conceptTypeIds')
    can_export_document = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportDocument')
    can_export_concept = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportConcept')
    can_export_one_entity = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportOneEntity')
    can_export_multiple_entities = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canExportMultipleEntities')
    last_task_time = sgqlc.types.Field(UnixTime, graphql_name='lastTaskTime')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicMetrics), graphql_name='metrics')


class KafkaTopic(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('topic', 'description', 'pipeline', 'metrics', 'priority', 'request_timeout_ms', 'move_to_on_timeout', 'stopped', 'system_topic')
    topic = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='topic')
    description = sgqlc.types.Field(String, graphql_name='description')
    pipeline = sgqlc.types.Field(PipelineSetup, graphql_name='pipeline')
    metrics = sgqlc.types.Field(sgqlc.types.non_null(KafkaTopicMetrics), graphql_name='metrics')
    priority = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='priority')
    request_timeout_ms = sgqlc.types.Field(Int, graphql_name='requestTimeoutMs')
    move_to_on_timeout = sgqlc.types.Field(String, graphql_name='moveToOnTimeout')
    stopped = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='stopped')
    system_topic = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='systemTopic')


class PipelineConfig(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'description', 'transforms', 'transform_count', 'used_in_topics')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    transforms = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PipelineTransformSetup))), graphql_name='transforms')
    transform_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='transformCount')
    used_in_topics = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='usedInTopics')


class UserPipelineTransform(sgqlc.types.Type, RecordInterface):
    __schema__ = tcontroller_api_schema
    __field_names__ = ('id', 'description', 'in_type', 'out_type', 'used_in_pipeline_configs', 'version', 'service')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    description = sgqlc.types.Field(String, graphql_name='description')
    in_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='inType')
    out_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='outType')
    used_in_pipeline_configs = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='usedInPipelineConfigs')
    version = sgqlc.types.Field(String, graphql_name='version')
    service = sgqlc.types.Field(sgqlc.types.non_null(UserService), graphql_name='service')



########################################################################
# Unions
########################################################################
class MessageStatusInfo(sgqlc.types.Union):
    __schema__ = tcontroller_api_schema
    __types__ = (MessageOk, MessageFailed, MessageDuplicate, MessageInProgress, MessageNotHandled, MessageUnknown)


class PendingMessageStatusInfo(sgqlc.types.Union):
    __schema__ = tcontroller_api_schema
    __types__ = (MessageInProgress, MessageNotHandled)



########################################################################
# Schema Entry Points
########################################################################
tcontroller_api_schema.query_type = Query
tcontroller_api_schema.mutation_type = Mutation
tcontroller_api_schema.subscription_type = None

