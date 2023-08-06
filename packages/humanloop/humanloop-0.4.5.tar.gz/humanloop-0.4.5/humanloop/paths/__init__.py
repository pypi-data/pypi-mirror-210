# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from humanloop.apis.path_to_api import path_to_api

import enum


class PathValues(str, enum.Enum):
    COMPLETION = "/completion"
    COMPLETIONDEPLOYED = "/completion-deployed"
    COMPLETIONEXPERIMENT = "/completion-experiment"
    COMPLETIONMODELCONFIG = "/completion-model-config"
    CHAT = "/chat"
    CHATDEPLOYED = "/chat-deployed"
    CHATEXPERIMENT = "/chat-experiment"
    CHATMODELCONFIG = "/chat-model-config"
    LOGS = "/logs"
    LOGS_ID = "/logs/{id}"
    FEEDBACK = "/feedback"
    PROJECTS = "/projects"
    PROJECTS_ID = "/projects/{id}"
    PROJECTS_ID_CONFIGS = "/projects/{id}/configs"
    PROJECTS_ID_ACTIVECONFIG = "/projects/{id}/active-config"
    PROJECTS_ID_ACTIVEEXPERIMENT = "/projects/{id}/active-experiment"
    PROJECTS_ID_FEEDBACKTYPES = "/projects/{id}/feedback-types"
    PROJECTS_ID_EXPORT = "/projects/{id}/export"
    MODELCONFIGS = "/model-configs"
    MODELCONFIGS_ID = "/model-configs/{id}"
    PROJECTS_PROJECT_ID_EXPERIMENTS = "/projects/{project_id}/experiments"
    EXPERIMENTS_EXPERIMENT_ID = "/experiments/{experiment_id}"
    EXPERIMENTS_EXPERIMENT_ID_MODELCONFIG = "/experiments/{experiment_id}/model-config"
    SESSIONS = "/sessions"
    SESSIONS_ID = "/sessions/{id}"
    TRACES = "/traces"
