"""
`ad_parser`
=======================================================================
Parser to pull job contexts from azure-pipelines.yml files
* Author(s): Jimmy Gomez
"""
import logging
import re
from embedops_cli.yaml_tools import open_yaml
from ..eo_types import BadYamlFileException, LocalRunContext

_logger = logging.getLogger(__name__)


def get_job_name_list(adyml_filename: str):
    """Get list of job names from the given YAML object"""

    try:
        adyml = open_yaml(adyml_filename)
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc

    job_name_list = []

    try:
        for job_def in adyml["jobs"]:
            if "job" in job_def:
                job_name_list.append(job_def["job"])

        if not all(isinstance(job_name, str) for job_name in job_name_list):
            raise BadYamlFileException()

        return job_name_list
    except (KeyError) as err:
        raise BadYamlFileException() from err


def get_job_list(adyml_filename: str) -> list:
    """Return the list of LocalRunContexts found in the given yaml object"""

    try:
        adyml = open_yaml(adyml_filename)
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc

    default_image = "ubuntu:latest"

    try:
        job_list = _parse_job_context(adyml, default_image)

        return job_list
    except (KeyError, AttributeError, TypeError) as err:
        raise BadYamlFileException() from err


def _parse_job_context(adyml, default_image):
    job_list = []
    for job_def in adyml["jobs"]:
        image = default_image
        var_dict = {}
        script_list = []
        if "steps" in job_def:
            for step in job_def["steps"]:
                if "script" in step:
                    script_list += _parse_script(step)
        if "container" in job_def:
            if isinstance(job_def["container"], str):
                image = job_def["container"]
            elif isinstance(job_def["container"], dict):
                if "image" in job_def["container"]:
                    image = job_def["container"]["image"]
                if "env" in job_def["container"]:
                    var_dict.update(job_def["container"]["env"])
        # ignore variable syntax for using azure repo variable
        for var_name, var_value in var_dict.copy().items():
            if re.match(r"\$\(.*\)$", var_value):
                del var_dict[var_name]
        job_list.append(LocalRunContext(job_def["job"], image, script_list, var_dict))
    return job_list


def _parse_script(step):
    script_list = []
    if isinstance(step["script"], list):
        for line in step["script"]:
            script_list.append(line)
    elif isinstance(step["script"], str):
        script_list += step["script"].split("\n")
        if script_list[-1] == "":
            # Remove the last empty command
            script_list.pop(-1)
    else:
        raise BadYamlFileException()
    return script_list
