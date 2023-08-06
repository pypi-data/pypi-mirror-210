from enum import Enum

from practicuscore.api_base import *  # DO NOT REMOVE


@dataclass_json
@dataclass
class CreateWorkerRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class CreateWorkerResponse(PRTResponse):
    worker_id: int = -1


@dataclass_json
@dataclass
class StartExtSvcRequest(PRTRequest):
    svc_name: str = ""
    port: Optional[int] = None
    dark_mode: bool = True
    auto_start_after_failure: bool = False
    singleton_service_per_node: bool = True
    additional_start_args: Optional[str] = None
    options: Optional[dict] = None


@dataclass_json
@dataclass
class StartExtSvcResponse(PRTResponse):
    port: int = -1
    options: Optional[dict] = None


@dataclass_json
@dataclass
class RestartNodeSvcRequest(PRTRequest):
    restart_reason_to_log: Optional[str] = None


@dataclass_json
@dataclass
class KillWorkerRequest(PRTRequest):
    worker_id: int = -1
    worker_uuid: Optional[str] = None


@dataclass_json
@dataclass
class KillWorkersRequest(PRTRequest):
    worker_id_list: Optional[List[int]] = None


@dataclass_json
@dataclass
class PingRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class HeartBeatRequest(PRTRequest):
    payload: Optional[dict] = None


@dataclass_json
@dataclass
class HeartBeatResponse(PRTResponse):
    payload: Optional[dict] = None


@dataclass_json
@dataclass
class CloneLogsRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class LoadRequest(PRTDataRequest):
    ws_uuid: Optional[str] = None  # ws_uuid of the app is synced with ws in Node, when possible.
    # response is csv, no class needed


@dataclass_json
@dataclass
class ExportDataRequest(PRTDataRequest):
    # conn_conf in base class is a mandatory field and is the destination of save
    source_conn_conf: Optional[Union[
        dict,
        NodeFileConnConf,
        SqLiteConnConf,
        S3ConnConf,
        MYSQLConnConf,
        PostgreSQLConnConf,
        RedshiftConnConf,
        SnowflakeConnConf,
        MSSQLConnConf,
        OracleConnConf,
        HiveConnConf,
        AthenaConnConf,
        TrinoConnConf,
        HanaConnConf,
        TeradataConnConf,
        Db2ConnConf,
        DynamoDBConnConf,
        CockroachDBConnConf,
        ClouderaConnConf,
        CustomDBConnConf,
    ]] = None
    step_dict_list: Optional[List[dict]] = None
    # response is op_result


@dataclass_json
@dataclass
class GetDFRequest(PRTRequest):
    sampling_method: Optional[str] = None
    sample_size_app: Optional[int] = None


class WSStateKeys:
    DF_FULL_TYPE_NAME = "DF_FULL_TYPE_NAME"
    DF_LOADED_ROWS_COUNT = "DF_LOADED_ROWS_COUNT"


@dataclass_json
@dataclass
class GetWSStateRequest(PRTRequest):
    wait_for_free_sec: float = 600
    generic_attributes_keys: Optional[List[str]] = None


@dataclass_json
@dataclass
class GetWSStateResponse(PRTResponse):
    busy: bool = False
    step_dict_list: Optional[List[dict]] = None
    async_op_issues_json_list: Optional[List[str]] = None
    generic_attributes_dict: Optional[dict] = None


@dataclass_json
@dataclass
class RunStepsRequest(PRTRequest):
    # used to run for "Node only" steps. Using dict, since Step is not dataclass
    step_dict_list: Optional[List[dict]] = None
    reset_steps: bool = False


@dataclass_json
@dataclass
class GetObjectStorageMetaRequest(PRTDataRequest):
    prefix: Optional[str] = None
    max_size: Optional[int] = None
    starting_token: Optional[str] = None
    element_uuid: Optional[str] = None


class StorageMetaChildrenLoadStatus(str, Enum):
    NOT_LOADED = "NOT_LOADED"
    LOADED = "LOADED"
    WONT_LOAD = "WONT_LOAD"


@dataclass_json
@dataclass
class ObjectStorageMeta:
    key: Optional[str] = None
    name: Optional[str] = None
    prefix: Optional[str] = None
    is_folder: Optional[bool] = None
    size: Optional[int] = None
    last_modified: Optional[datetime] = None
    level: int = 0
    children: Optional[List['ObjectStorageMeta']] = None
    children_loaded: StorageMetaChildrenLoadStatus = StorageMetaChildrenLoadStatus.NOT_LOADED

    @property
    def is_file(self) -> bool:
        return not self.is_folder


@dataclass_json
@dataclass
class GetObjectStorageMetaResponse(PRTResponse):
    meta_list: Optional[List[ObjectStorageMeta]] = None


@dataclass_json
@dataclass
class ConnSelectionStats:
    # statistics about a selected key or keys
    size_per_row: Optional[int] = None
    sample_size_in_bytes: Optional[int] = None
    sample_rows: Optional[int] = None
    total_size_in_bytes: Optional[int] = None
    total_rows: Optional[int] = None


@dataclass_json
@dataclass
class PreviewRequest(PRTDataRequest):
    pass


@dataclass_json
@dataclass
class PreviewResponse(PRTResponse):
    selection_stats: Optional[ConnSelectionStats] = None
    csv_str: Optional[str] = None


@dataclass_json
@dataclass
class TestRelationalConnRequest(PRTDataRequest):
    pass


@dataclass_json
@dataclass
class GetFileStatusRequest(PRTRequest):
    node_path_list: Optional[List[str]] = None
    recursive: bool = False


@dataclass_json
@dataclass
class FileStatus:
    file_path: str
    file_size: int
    file_epoch: float


@dataclass_json
@dataclass
class GetFileStatusResponse(PRTResponse):
    file_status_list: Optional[List[FileStatus]] = None


@dataclass_json
@dataclass
class UploadFilesRequest(PRTRequest):
    # opens a multi-part app to Cloud Worker communication channel. files/file parts are communicated chunk by chunk
    pass


@dataclass_json
@dataclass
class UploadFilesToCloudRequest(PRTRequest):
    conn_conf: Optional[Union[
        S3ConnConf
    ]] = None


@dataclass_json
@dataclass
class UploadNodeFilesToCloudRequest(PRTRequest):
    conn_conf: Optional[Union[
        S3ConnConf
    ]] = None
    source_path_list: Optional[List[str]] = None
    target_dir_path: Optional[str] = None
    source_path_to_cut: Optional[str] = None


@dataclass_json
@dataclass
class DownloadFilesRequest(PRTRequest):
    node_path_list: Optional[List[str]] = None
    recursive: bool = False


@dataclass_json
@dataclass
class CopyFilesRequest(PRTRequest):
    source_path_list: Optional[List[str]] = None
    target_dir_path: Optional[str] = None
    source_path_to_cut: Optional[str] = None


@dataclass_json
@dataclass
class ProfileWSRequest(PRTRequest):
    profile_uuid: Optional[str] = None
    title: Optional[str] = None
    compare_to_original: Optional[bool] = None


@dataclass_json
@dataclass
class ProfileWSResponse(PRTResponse):
    started_profiling: Optional[bool] = None


@dataclass_json
@dataclass
class ViewLogsRequest(PRTRequest):
    view_practicus_log: bool = True
    view_practicus_audit_log: bool = True
    log_size_mb: int = 10


@dataclass_json
@dataclass
class ViewLogsResponse(PRTResponse):
    practicus_log: Optional[str] = None
    practicus_audit_log: Optional[str] = None


@dataclass_json
@dataclass
class TestGenericRequest(PRTRequest):
    some_str: Optional[str] = None


@dataclass_json
@dataclass
class TestGenericResponse(PRTResponse):
    some_result: Optional[str] = None


@dataclass_json
@dataclass
class RunScriptRequest(PRTRequest):
    script_path: Optional[str] = None
    run_as_sudo: bool = False
    timeout_secs: int = 120
    wait_for_end: bool = True


@dataclass_json
@dataclass
class RunScriptResponse(PRTResponse):
    std_out: str = ""
    std_err: str = ""


@dataclass_json
@dataclass
class FlushLogsRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class XLImportRequest(PRTRequest):
    file_name: str = ""


@dataclass_json
@dataclass
class XLImportResponse(PRTResponse):
    dp_content: str = ""
    dp_err_warning: str = ""


@dataclass_json
@dataclass
class TestCodeRequest(PRTRequest):
    sampling_method: str = "ALL"
    sample_size: int = 1000
    code_block_encoded: Optional[str] = None
    is_sql: Optional[bool] = None
    sql_table_name: Optional[str] = None


@dataclass_json
@dataclass
class TestCodeResponse(PRTResponse):
    test_result_csv_b: Optional[str] = None


@dataclass_json
@dataclass
class GenerateCodeRequest(PRTRequest):
    engine: Optional[str] = None
    template_list: Optional[List[str]] = None
    worksheet_name: Optional[str] = None
    app_user_name: Optional[str] = None
    export_name: Optional[str] = None
    export_data_step_dict: Optional[dict] = None
    build_model_step_dict: Optional[dict] = None
    dag_flow: Optional[str] = None
    save_conn_in_files: bool = True
    save_cloud_credentials: bool = False
    params: Optional[dict] = None  # Cloud Worker + auth details (if requested by user)


@dataclass_json
@dataclass
class GenerateCodeResponse(PRTResponse):
    generated_file_paths: Optional[List[str]] = None


@dataclass_json
@dataclass
class CreateFolderRequest(PRTDataRequest):
    full_path: Optional[str] = None


@dataclass_json
@dataclass
class ModelConfig:
    state: Optional[str] = None
    percent_complete: int = 0
    model_name: Optional[str] = None
    model_desc: Optional[str] = None
    target: Optional[str] = None
    re_sample_size: Optional[int] = None
    model_dir: Optional[str] = None
    short_model_name: Optional[str] = None
    version_name: Optional[str] = None
    problem_type: Optional[str] = None
    limit_to_models: Optional[str] = None
    use_gpu: Optional[bool] = False
    explain: Optional[bool] = None
    sensitive_features: Optional[str] = None
    user_name: Optional[str] = None
    node_name: Optional[str] = None
    node_instance_id: Optional[str] = None
    # Binary or Excel model
    build_full_fledged: Optional[bool] = None
    build_for_excel: Optional[bool] = None
    excel_rows_to_export: Optional[int] = None
    model_signature_json: Optional[str] = None
    # Feature selection
    feature_selection_percent: Optional[int] = None
    features_ignored: Optional[str] = None
    # Time Series
    time_feature: Optional[str] = None
    time_frequency: Optional[str] = None
    # Clustering
    num_clusters: Optional[int] = None
    # Engines etc. versions
    py_version: Optional[str] = None
    auto_ml_engine: Optional[str] = None
    auto_ml_version: Optional[str] = None
    # Experiment logging
    log_experiments: Optional[bool] = None
    log_exp_name: Optional[str] = None
    log_db_conn_str: Optional[str] = None
    log_artifacts_url: Optional[str] = None
    log_exp_id: Optional[str] = None
    log_exp_full_parent_run_id: Optional[str] = None
    log_exp_full_final_run_id: Optional[str] = None
    log_exp_excel_parent_run_id: Optional[str] = None
    log_exp_excel_final_run_id: Optional[str] = None
    final_model: Optional[str] = None
    score: Optional[float] = None
    errors: Optional[str] = None
    excel_final_model: Optional[str] = None
    excel_score: Optional[float] = None
    excel_errors: Optional[str] = None
    summary: str = ""


class ModelConfFactory:
    @staticmethod
    def create_or_get(model_conf_json_dict_or_obj) -> ModelConfig:
        if isinstance(model_conf_json_dict_or_obj, str):
            import json
            model_conf_json_dict_or_obj = json.loads(model_conf_json_dict_or_obj)

        if isinstance(model_conf_json_dict_or_obj, dict):
            return ModelConfig.from_dict(model_conf_json_dict_or_obj)


@dataclass_json
@dataclass
class CreateModelRequest(PRTRequest):
    model_config: Optional[ModelConfig] = None
    status_check: bool = False
    last_reported_log_byte: int = 0


@dataclass_json
@dataclass
class CreateModelResponse(PRTResponse):
    model_config: Optional[ModelConfig] = None
    current_log: Optional[str] = None
    last_reported_log_byte: int = 0


@dataclass_json
@dataclass
class RegisterModelRequest(PRTRequest):
    model_dir: Optional[str] = None


@dataclass_json
@dataclass
class ModelSearchResult:
    model_name: Optional[str] = None
    latest_v: Optional[int] = None
    latest_v_timestamp: Optional[int] = None
    latest_staging_v: Optional[int] = None
    latest_staging_timestamp: Optional[int] = None
    latest_prod_v: Optional[int] = None
    latest_prod_timestamp: Optional[int] = None


@dataclass_json
@dataclass
class ModelSearchResults:
    results: Optional[List[ModelSearchResult]] = None


@dataclass_json
@dataclass
class SearchModelsRequest(PRTRequest):
    mlflow_tracking_uri: Optional[str] = None
    filter_string_b64: Optional[str] = None
    max_results: int = 100


@dataclass_json
@dataclass
class SearchModelsResponse(PRTResponse):
    model_search_results: Optional[ModelSearchResults] = None


@dataclass_json
@dataclass
class GetModelMetaRequest(PRTRequest):
    mlflow_tracking_uri: Optional[str] = None
    model_uri: Optional[str] = None
    model_json_path: Optional[str] = None


@dataclass_json
@dataclass
class GetModelMetaResponse(PRTResponse):
    model_config_json: Optional[str] = None
    prepare_ws_b64: Optional[str] = None


# todo: do we need the below xl model requests?

@dataclass_json
@dataclass
class XLModelRequest(PRTRequest):
    model_conf_path: str = ""
    xl_name: str = ""
    num_rows: int = 1_000


@dataclass_json
@dataclass
class XLModelResponse(PRTResponse):
    xl_path: str = ""


@dataclass_json
@dataclass
class GetSystemStatRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class GetSystemStatResponse(PRTResponse):
    system_stat: Optional[dict] = None
    node_version: Optional[str] = None


@dataclass_json
@dataclass
class DeleteKeysRequest(PRTDataRequest):
    keys: Optional[List[str]] = None
    delete_sub_keys: bool = False


@dataclass_json
@dataclass
class ListBucketsRequest(PRTDataRequest):
    pass


@dataclass_json
@dataclass
class ListBucketsResponse(PRTResponse):
    buckets: Optional[List[str]] = None


@dataclass_json
@dataclass
class ReplicateNodeRequest(PRTRequest):
    source_node_name: Optional[str] = None
    source_node_dns: Optional[str] = None
    source_node_pem_data: Optional[str] = None
    timeout_secs: int = 30 * 60  # 30 minutes
