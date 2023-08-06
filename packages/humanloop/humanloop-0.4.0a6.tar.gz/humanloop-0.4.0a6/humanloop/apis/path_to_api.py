import typing_extensions

from humanloop.paths import PathValues
from humanloop.apis.paths.completion import Completion
from humanloop.apis.paths.completion_deployed import CompletionDeployed
from humanloop.apis.paths.completion_experiment import CompletionExperiment
from humanloop.apis.paths.completion_model_config import CompletionModelConfig
from humanloop.apis.paths.chat import Chat
from humanloop.apis.paths.chat_deployed import ChatDeployed
from humanloop.apis.paths.chat_experiment import ChatExperiment
from humanloop.apis.paths.chat_model_config import ChatModelConfig
from humanloop.apis.paths.logs import Logs
from humanloop.apis.paths.logs_id import LogsId
from humanloop.apis.paths.feedback import Feedback
from humanloop.apis.paths.projects import Projects
from humanloop.apis.paths.projects_id import ProjectsId
from humanloop.apis.paths.projects_id_configs import ProjectsIdConfigs
from humanloop.apis.paths.projects_id_active_config import ProjectsIdActiveConfig
from humanloop.apis.paths.projects_id_active_experiment import ProjectsIdActiveExperiment
from humanloop.apis.paths.projects_id_feedback_types import ProjectsIdFeedbackTypes
from humanloop.apis.paths.projects_id_export import ProjectsIdExport
from humanloop.apis.paths.model_configs import ModelConfigs
from humanloop.apis.paths.model_configs_id import ModelConfigsId
from humanloop.apis.paths.projects_project_id_experiments import ProjectsProjectIdExperiments
from humanloop.apis.paths.experiments_experiment_id import ExperimentsExperimentId
from humanloop.apis.paths.experiments_experiment_id_model_config import ExperimentsExperimentIdModelConfig
from humanloop.apis.paths.sessions import Sessions
from humanloop.apis.paths.sessions_id import SessionsId
from humanloop.apis.paths.traces import Traces

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.COMPLETION: Completion,
        PathValues.COMPLETIONDEPLOYED: CompletionDeployed,
        PathValues.COMPLETIONEXPERIMENT: CompletionExperiment,
        PathValues.COMPLETIONMODELCONFIG: CompletionModelConfig,
        PathValues.CHAT: Chat,
        PathValues.CHATDEPLOYED: ChatDeployed,
        PathValues.CHATEXPERIMENT: ChatExperiment,
        PathValues.CHATMODELCONFIG: ChatModelConfig,
        PathValues.LOGS: Logs,
        PathValues.LOGS_ID: LogsId,
        PathValues.FEEDBACK: Feedback,
        PathValues.PROJECTS: Projects,
        PathValues.PROJECTS_ID: ProjectsId,
        PathValues.PROJECTS_ID_CONFIGS: ProjectsIdConfigs,
        PathValues.PROJECTS_ID_ACTIVECONFIG: ProjectsIdActiveConfig,
        PathValues.PROJECTS_ID_ACTIVEEXPERIMENT: ProjectsIdActiveExperiment,
        PathValues.PROJECTS_ID_FEEDBACKTYPES: ProjectsIdFeedbackTypes,
        PathValues.PROJECTS_ID_EXPORT: ProjectsIdExport,
        PathValues.MODELCONFIGS: ModelConfigs,
        PathValues.MODELCONFIGS_ID: ModelConfigsId,
        PathValues.PROJECTS_PROJECT_ID_EXPERIMENTS: ProjectsProjectIdExperiments,
        PathValues.EXPERIMENTS_EXPERIMENT_ID: ExperimentsExperimentId,
        PathValues.EXPERIMENTS_EXPERIMENT_ID_MODELCONFIG: ExperimentsExperimentIdModelConfig,
        PathValues.SESSIONS: Sessions,
        PathValues.SESSIONS_ID: SessionsId,
        PathValues.TRACES: Traces,
    }
)

path_to_api = PathToApi(
    {
        PathValues.COMPLETION: Completion,
        PathValues.COMPLETIONDEPLOYED: CompletionDeployed,
        PathValues.COMPLETIONEXPERIMENT: CompletionExperiment,
        PathValues.COMPLETIONMODELCONFIG: CompletionModelConfig,
        PathValues.CHAT: Chat,
        PathValues.CHATDEPLOYED: ChatDeployed,
        PathValues.CHATEXPERIMENT: ChatExperiment,
        PathValues.CHATMODELCONFIG: ChatModelConfig,
        PathValues.LOGS: Logs,
        PathValues.LOGS_ID: LogsId,
        PathValues.FEEDBACK: Feedback,
        PathValues.PROJECTS: Projects,
        PathValues.PROJECTS_ID: ProjectsId,
        PathValues.PROJECTS_ID_CONFIGS: ProjectsIdConfigs,
        PathValues.PROJECTS_ID_ACTIVECONFIG: ProjectsIdActiveConfig,
        PathValues.PROJECTS_ID_ACTIVEEXPERIMENT: ProjectsIdActiveExperiment,
        PathValues.PROJECTS_ID_FEEDBACKTYPES: ProjectsIdFeedbackTypes,
        PathValues.PROJECTS_ID_EXPORT: ProjectsIdExport,
        PathValues.MODELCONFIGS: ModelConfigs,
        PathValues.MODELCONFIGS_ID: ModelConfigsId,
        PathValues.PROJECTS_PROJECT_ID_EXPERIMENTS: ProjectsProjectIdExperiments,
        PathValues.EXPERIMENTS_EXPERIMENT_ID: ExperimentsExperimentId,
        PathValues.EXPERIMENTS_EXPERIMENT_ID_MODELCONFIG: ExperimentsExperimentIdModelConfig,
        PathValues.SESSIONS: Sessions,
        PathValues.SESSIONS_ID: SessionsId,
        PathValues.TRACES: Traces,
    }
)
