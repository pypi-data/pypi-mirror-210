from typing import List
import os


def check_environment_variables(env_vars_to_check: List[str]):
    missing = []
    for var in env_vars_to_check:
        if os.getenv(var) is None:
            missing.append(var)
    if len(missing) > 0:
        from whitson_tool_helper import MissingEnvironmentVariableError

        raise MissingEnvironmentVariableError(missing)
