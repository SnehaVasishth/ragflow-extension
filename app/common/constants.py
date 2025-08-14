import json
import os
import httpx
from app.config.main import Config
from app.utils.logger import logger
from typing import Any, Dict, Set, List, Callable
from datetime import datetime

try:
    script_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../'))
    logger.info(f"Script directory: {script_dir}")
    git_version_path = os.path.join(script_dir, '../gitVersion.json')
    logger.info(f"Loading git version from: {git_version_path}")
    with open(git_version_path, 'r') as file:
        gitVersion = json.load(file)
except FileNotFoundError:
    logger.info("gitVersion.json file not found. Using default values.")
    gitVersion = {"branch": "unknown", "commit": "unknown"}

HTTP_CONSTANTS = {
    "METHOD_TYPE": {
        "POST": 'POST',
        "GET": 'GET',
        "PUT": 'PUT',
    },
    "HEADER_TYPE": {
        "URL_ENCODED": 'application/x-www-form-urlencoded',
        "APPLICATION_JSON": 'application/json',
    },
    "CONTENT_TYPE": {
        "URL_ENCODE": 'application/x-www-form-urlencoded',
    },
    "RESPONSE_STATUS": {
        "SUCCESS": True,
        "FAILURE": False,
    },
    "LOG_LEVEL_TYPE": {
        "INFO": 'info',
        "ERROR": 'error',
        "WARN": 'warn',
        "VERBOSE": 'verbose',
        "DEBUG": 'debug',
        "SILLY": 'silly',
        "FUNCTIONAL": 'functional',
        "HTTP_REQUEST": 'http request',
    },
}

API_SUCCESS_MESSAGE = {
    "FETCH_SUCCESS": 'Information fetched successfully',
    "POST_SUCCESS_MESSAGE": 'Information added successfully',
    "FETCH_FAILURE": "Failed to retrieve information",
}

API_FAILURE_MESSAGE = {
    "BAD_REQUEST": 'Bad Request!',
    "SESSION_EXPIRED": 'Session Expired!',
    "INVALID_REQUEST": 'Invalid Request',
    "INVALID_PARAMS": 'Invalid Parameters',
    "INTERNAL_SERVER_ERROR": 'Internal server Error',
    "INVALID_SESSION_TOKEN": 'Invalid session token',
    "SESSION_GENERATION": 'Unable to generate session!',
}

SERVICE_STATUS_HTML = (
    '<body style="font-family: Helvetica, Arial, sans-serif; background-color: #000; margin: 0; padding: 0;">'
    '<div style="display: flex;flex-direction: column;justify-content: center;align-items: center;min-height: 100vh;">'
    '<div style="font-size: 24px; color: #4d6efe;">'
    '⚡ ZBrain Multi Agentt 🔋 <span style="color: #05df4c;">MicroService is working fine</span>'
    '</div>'
    '<pre style="border: 1px gray solid; margin-top: 20px; color: #fff; background-color: #0f1219; padding: 20px; border-radius: 8px; font-size: 16px; line-height: 1.5; max-width: 80%; white-space: pre-wrap; word-wrap: break-word;">'
    f'{{\n&nbsp;&nbsp;&nbsp;<span style="color: #60baff;">"version"</span>: '
    f'<span style="color: #69e38d;">"{Config.get_environment()["VERSION"]}"</span>,\n'
    f'&nbsp;&nbsp;&nbsp;<span style="color: #60baff;">"branch"</span>: '
    f'<span style="color: #69e38d;">"{gitVersion["branch"]}"</span>,\n'
    f'&nbsp;&nbsp;&nbsp;<span style="color: #60baff;">"commit"</span>: '
    f'<span style="color: #69e38d;">"{gitVersion["commit"]}"</span>\n}}'
    '</pre></div></body>'
)

PROVIDERS = {
    "OPENAI": 'OPENAI',
    "CLAUDE": 'CLAUDE',
    "VOYAGE": 'VOYAGE',
    "AZURE_OPENAI": 'AZURE_OPENAI',
    'GOOGLE': 'GOOGLE',
    "GROQ": 'GROQ',
    "CLAUDE": 'CLAUDE',
    "META_LLAMA": 'META_LLAMA',
    "OPEN_ROUTER": 'OPEN_ROUTER',
    "CUSTOM": 'CUSTOM',
}
JS_TO_PYTHON_TYPE_MAP = {
    "string": "str",
    "number": "float",   
    "boolean": "bool",
    "bigint": "int",
    "symbol": "str",  
    "any": "Any",
    "date": "datetime.datetime",
    "array": "list",
    "object": "dict",
    "map": "dict",     
    "set": "set",
    "function": "Callable"
}

JS_TO_PYTHON_TYPE_MAP_v2 = {
    "string": str,
    "number": float,
    "boolean": bool,
    "bigint": int,
    "symbol": str,
    "any": Any,
    "date": datetime,
    "array": List[Any],
    "object": Dict[str, Any],
    "map": Dict[str, Any],
    "set": Set,
    "function": Callable
}

AGENT_GLOBAL_INSTRUCTIONS = """
Always format your response as: \n 
THINKING: Your detailed reasoning, including what you know, what you need to find out, and your plan to proceed and step by step analysis. \n 
ACTION: The action you will take, including any tools you will use. \n 
The conclusion of the step or the final answer if no further action is needed.
"""
HTTP_TIMEOUT = httpx.Timeout(
    connect=30.0,  # 30 seconds to establish connection
    read=300.0,    # 5 minutes to read response
    write=30.0,    # 30 seconds to send request
    pool=10.0      # 10 seconds to get connection from pool
)

STATUS_TYPES = {
    "SUCCEEDED": "SUCCEEDED",
    "FAILED": "FAILED",
    "COMPLETED": "COMPLETED",
    "ERRORED": "ERRORED",
}

AGENT_MEMORY_TYPES = {
    "NO_MEMORY": 'NO_MEMORY',
    "CREW_MEMORY": 'CREW_MEMORY',
    "TENANT_MEMORY": 'TENANT_MEMORY',
}
