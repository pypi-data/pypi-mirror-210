import importlib
from importlib import abc
import sys
import os
import functools
import pathlib


def patchonimport(module_name=None):
    def decorator(target_function):
        sys.meta_path.insert(0, ImportModulePatch({module_name: target_function}))

        def wrapper(*args, **kwargs):
            target_function(*args, **kwargs)

        return wrapper

    return decorator


class ImportModulePatch(abc.MetaPathFinder, abc.Loader):
    def __init__(self, patch_modules):
        # type: (Dict[str, Callable[[Module], None]]) -> None
        self._patch_modules = patch_modules
        self._in_create_module = False

    def find_module(self, fullname, path=None):
        spec = self.find_spec(fullname, path)
        if spec is None:
            return None
        return spec

    def create_module(self, spec):
        try:
            self._in_create_module = True

            from importlib.util import find_spec, module_from_spec
            real_spec = importlib.util.find_spec(spec.name)

            real_module = module_from_spec(real_spec)
            real_spec.loader.exec_module(real_module)

            self._in_create_module = False
            return real_module
        except:
            return None

    def exec_module(self, module):
        try:
            _ = sys.modules.pop(module.__name__)
        except KeyError:
            print("module %s is not in sys.modules", module.__name__)
        sys.modules[module.__name__] = module
        globals()[module.__name__] = module
        self._patch_modules[module.__name__](module)

    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self._patch_modules:
            return None
        if self._in_create_module:
            return None
        spec = importlib.machinery.ModuleSpec(fullname, self)
        return spec


class PatchesForRay(object):
    @staticmethod
    @patchonimport(module_name='botocore')
    def loader_patch(real_module):
        os.environ['AWS_DATA_PATH'] = str(pathlib.Path(__file__).parent)

    # @staticmethod
    # @patchonimport(module_name='boto3')
    # def client_patch(real_module):
    #     setattr(real_module, 'client',
    #             functools.partial(real_module.client, endpoint_url='https://glue.us-east-2.amazonaws.com', region_name='us-east-2'))

# For example, if used as below:
#
# import boto3
# import logging
#
# client = boto3.Session(profile_name='abc').client("glue")
# logging.getLogger(__file__).warning(f'Applied custom AWS_DATA_PATH {os.getenv("AWS_DATA_PATH")}')
# if 'BatchCreateLineageNodes' in client.meta.service_model.operation_names:
#     logging.getLogger(__file__).warning(f'Applied custom service-2 for {client.meta.service_model.metadata.get("uid")}')
# logging.getLogger(__file__).warning(f'Applied custom endpoint_url {client.meta.endpoint_url}')
# logging.getLogger(__file__).warning(f'Applied custom region-lock {client.meta.region_name}')
#
# print(client.list_sessions())


import ast
import base64
import json
from botocore.config import Config
from ipykernel.ipkernel import IPythonKernel
from IPython.display import publish_display_data
from inspect import currentframe

from importlib_metadata import version
import os
import sys
import uuid
import requests
import subprocess
from urllib3.util import parse_url

try:
    from asyncio import Future
except ImportError:

    class Future(object):
        """A class nothing will use."""

import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import boto3
import botocore
from botocore.exceptions import ClientError
from dateutil.tz import tzlocal

from ..glue_kernel_utils.GlueSessionsConstants import *
from hdijupyterutils.ipythondisplay import IpythonDisplay
from IPython import get_ipython
from ..glue_kernel_utils.KernelMagics import KernelMagics
import re
class GlueKernel(IPythonKernel):
    time_out = float("inf")
    spark_conf = None
    session_id = None
    new_session_id = None
    session_id_prefix = None
    request_origin = None
    glue_client = None
    sts_client = None
    implementation = "Python Glue Session"
    implementation_version = "1.0"
    language = "no-op"
    language_version = "0.1"
    language_info = {
        "name": "Python_Glue_Session",
        "mimetype": "text/x-python",
        "codemirror_mode": {"name": "python", "version": 3},
        "pygments_lexer": "python3",
        "file_extension": ".py",
    }
    session_language = "python"
    ipython_display = None

    def __init__(self, **kwargs):
        super(GlueKernel, self).__init__(**kwargs)
        self.execution_counter = 1
        self.glue_role_arn = None
        self.profile = None
        self.endpoint_url = None
        self.region = None
        self._set_default_arguments()
        self.connections = defaultdict()
        self.tags = defaultdict()
        self.security_config = None
        self.session_name = "AssumeRoleSession"
        self.max_capacity = None
        self.number_of_workers = 5
        self.worker_type = "G.1X"
        self.job_type = "glueetl"
        self.idle_timeout = 2880
        self.glue_version = "2.0"
        self.request_origin = "GluePySparkKernel"
        self.should_print_startup_text = True
        self.python_version = "3"

        if not self.ipython_display:
            self.ipython_display = IpythonDisplay()

        self._register_magics()
        self._setup_terminal_logging()

        # Setup environment variables
        os_env_request_origin = self._retrieve_os_env_variable(REQUEST_ORIGIN)
        os_env_region = self._retrieve_os_env_variable(REGION)
        os_env_session_id = self._retrieve_os_env_variable(SESSION_ID)
        os_env_glue_role_arn = self._retrieve_os_env_variable(GLUE_ROLE_ARN)
        os_env_glue_version = self._retrieve_os_env_variable(GLUE_VERSION)
        os_env_glue_job_type = self._retrieve_os_env_variable(GLUE_JOB_TYPE)
        if os_env_request_origin:
            self.set_request_origin(os_env_request_origin)
        if os_env_region:
            self.set_region(os_env_region)
        if os_env_session_id:
            self.set_new_session_id(os_env_session_id)
        if os_env_glue_role_arn:
            self.set_glue_role_arn(os_env_glue_role_arn)
        if os_env_glue_version:
            self.set_glue_version(os_env_glue_version)
        if os_env_glue_job_type:
            JobType.lookup(os_env_glue_job_type).apply(self)

    def _set_default_arguments(self):
        self.default_arguments = {
            "--glue_kernel_version": self._get_current_kernel_version("aws-glue-sessions"),
            "--enable-glue-datacatalog": "true",
        }

    def display_result(self, statement_output):
        if 'Data' in statement_output:
            statement_output_data = statement_output['Data']

            # The default case would be a text/plain response, but an image result may also be accompanied by a text output.
            if MimeTypes.TextPlain.name in statement_output_data and len(statement_output_data) == 1:
                # The value for dictionary key in the result is: text/plain
                self._send_output(statement_output_data[MimeTypes.TextPlain.name])
            elif 'MimeType' in statement_output_data:
                result = statement_output_data['Result']
                mime_type = statement_output_data['MimeType']
                stdout_text = None
                stderr_text = None

                # Unpack the inline vs. indirect std streams
                if mime_type == MimeTypes.S3URI.value:
                    stdout_text = self.get_results(statement_output_data['StdOut']) if 'StdOut' in statement_output_data else ""
                    stderr_text = self.get_results(statement_output_data['StdErr']) if 'StdErr' in statement_output_data else ""
                else:
                    stdout_text = statement_output_data['StdOut'] if 'StdOut' in statement_output_data else ""
                    stderr_text = statement_output_data['StdErr'] if 'StdErr' in statement_output_data else ""

                if mime_type == MimeTypes.S3URI.value:
                    response = self.get_results(statement_output_data['Result'])
                    result = json.loads(response)
                    if len(result) == 0:
                        # Semantically this case corresponds to the 'stream' result,
                        # which is is meant to be "send_output'd" and actually
                        # arrives on stdout which is headed there anyway.
                        result = None
                        mime_type = None
                    elif result.get(MimeTypes.ImagePng.value):
                        result = result.get(MimeTypes.ImagePng.value)
                        mime_type = MimeTypes.ImagePng.value
                    elif result.get(MimeTypes.TextPlain.value):
                        result = result.get(MimeTypes.TextPlain.value)
                        mime_type = MimeTypes.TextPlain.value

                if mime_type and ';' in mime_type:
                    mime_type_list = mime_type.replace(' ','').split(';')
                    if 'base64' in mime_type_list:
                        result = base64.b64decode(str(result))
                        mime_type_list.remove('base64')
                        mime_type = ';'.join(mime_type_list)

                # Dispatch of results for display
                if stdout_text:
                    self._send_output(stdout_text)
                if stderr_text:
                    self._send_error_output(stderr_text)

                if result and mime_type:
                    display_data = {
                        mime_type: result
                    }
                    publish_display_data(data=display_data, metadata={mime_type: {"width": 640, "height": 480}})




    async def do_execute(
            self, code: str, silent: bool, store_history=True, user_expressions=None, allow_stdin=False
    ):
        # Print help text upon startup
        if self.should_print_startup_text:
            await self._print_startup_text()
        code = await self._execute_magics(
            code, silent, store_history, user_expressions, allow_stdin
        )
        statement_id = None

        if not code:
            return await self._complete_cell()

        # Create glue client and session
        try:
            if not self.glue_client:
                self.glue_client = self._create_glue_client()

            if (
                not self.get_session_id()
                or self.get_current_session_status() in UNHEALTHY_SESSION_STATUS
            ):
                if self.profile:
                    self._get_configs_from_profile()
                self.create_session()
                if self.get_current_session_status() in UNHEALTHY_SESSION_STATUS:
                    self._send_error_output(f'Current session is in an unhealthy terminal state. If you wish to create a new session use %stop_session before executing any further statements.')
                    return await self._complete_cell()
        except Exception as e:
            if RAY_INVALID_REGION_ERROR in (e.args[0]):
                self._send_output(Colour.Red + Colour.Bold + f'Glue Ray job type is not available in selected region.')
                return await self._complete_cell()
            else:
                sys.stderr.write(f"Exception encountered while creating session: {e} \n")
                self._print_traceback(e)
                return await self._complete_cell()

        try:
            # Run statement
            statement_id = self.glue_client.run_statement(
                SessionId=self.get_session_id(), Code=code
            )["Id"]
            start_time = time.time()

            try:
                while time.time() - start_time <= self.time_out:
                    statement = self.glue_client.get_statement(
                        SessionId=self.get_session_id(), Id=statement_id
                    )["Statement"]
                    if statement["State"] in FINAL_STATEMENT_STATUS:
                        return self._construct_reply_content(statement)

                    time.sleep(WAIT_TIME)

                sys.stderr.write(f"Timeout occurred with statement (statement_id={statement_id})")

            except KeyboardInterrupt:
                self._send_output(
                    f"Execution Interrupted. Attempting to cancel the statement (statement_id={statement_id})"
                )
                self._cancel_statement(statement_id)
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']

            if error_code in 'InvalidInputException':
                if self.get_current_session_status() == TIMEOUT_SESSION_STATUS:
                    self._send_error_output(
                        f"session_id={self.get_session_id()} has reached {self.get_current_session_status()} status. ")
                    self._send_error_output(
                        f"Please re-run the same cell to restart the session. You may also need to re-run "
                        f"previous cells if trying to use pre-defined variables.")
                    self.reset_kernel()
                return await self._complete_cell()

            else:
                self._send_error_output(error_message)
                self._cancel_statement(statement_id)
                return await self._complete_cell()

        except Exception as e:
            sys.stderr.write(f"Exception encountered while running statement: {e} \n")
            self._print_traceback(e)
            self._cancel_statement(statement_id)
            return await self._complete_cell()

    def authenticate(self, glue_role_arn=None, profile=None):
        if not glue_role_arn:
            self.set_glue_role_arn(self._get_iam_role_using_sts())
            glue_role_arn = self.get_glue_role_arn()
        # either an IAM role for Glue must be provided or a profile must be set
        if not glue_role_arn and not profile:
            raise ValueError(f"Neither glue_role_arn nor profile were provided")
        # region must be set
        if not self.get_region():
            raise ValueError(f"Region must be set.")
        # If we are using a custom endpoint
        if not self.get_endpoint_url():
            self.set_endpoint_url(self._format_endpoint_url(self.get_region()))
        if glue_role_arn:
            self.set_glue_role_arn(glue_role_arn)
        if profile:
            return self._authenticate_with_profile()
        else:
            self._send_output(
                f"Authenticating with environment variables and user-defined glue_role_arn: {glue_role_arn}"
            )
            self.create_sts_client()
            return boto3.Session().client(
                "glue", region_name=self.get_region(), endpoint_url=self.get_endpoint_url(),config=Config(retries=dict(max_attempts=10,mode='adaptive'))
            )

    def _get_available_profiles(self):
        return boto3.session.Session().available_profiles

    def _authenticate_with_profile(self):
        self._send_output(f"Authenticating with profile={self.get_profile()}")

        if self.get_profile() not in self._get_available_profiles():
            raise ValueError(f"Profile {self.get_profile()} not defined in config")

        custom_role_arn = self._retrieve_from_aws_config("glue_role_arn")

        # Check if a glue_role_arn is defined in the profile and a custom glue_role_arn hasn't been defined
        if not self.get_glue_role_arn() and custom_role_arn is not None:
            self._send_output(f"glue_role_arn retrieved from profile: {custom_role_arn}")
            self.set_glue_role_arn(custom_role_arn)
        else:
            if self.get_glue_role_arn() is not None:
                self._send_output(f"glue_role_arn defined by user: {self.get_glue_role_arn()}")
            else:
                raise ValueError(
                    f"glue_role_arn not present in profile and was not defined by user"
                )

        self.create_sts_client()
        return boto3.Session(profile_name=self.get_profile()).client(
            "glue", region_name=self.get_region(), endpoint_url=self.get_endpoint_url(), config=Config(retries=dict(max_attempts=10))
        )

    def _retrieve_from_aws_config(self, key):
        custom_profile_session = botocore.session.Session(profile=self.get_profile())
        return custom_profile_session.full_config["profiles"][self.get_profile()].get(key)

    def _get_configs_from_profile(self):
        if not self.get_region():
            config_region = self._retrieve_from_aws_config("region")
            if config_region:
                self.set_region(config_region)
        if not self.get_glue_role_arn():
            config_glue_role_arn = self._retrieve_from_aws_config("glue_role_arn")
            if config_glue_role_arn:
                self.set_glue_role_arn(config_glue_role_arn)
        if not self.get_spark_conf():
            config_spark_conf = self._retrieve_from_aws_config("spark_conf")
            if config_spark_conf:
                self.set_spark_conf(config_spark_conf)

    def configure(self, configs_json):
        kernel_managed_params = {
            "profile",
            "endpoint",
            "region",
            "iam_role",
            "session_id",
            "max_capacity",
            "number_of_workers",
            "worker_type",
            "connections",
            "glue_version",
            "security_config",
            "idle_timeout",
            "tags",
        }
        try:
            configs = ast.literal_eval(configs_json)
            if "profile" in configs:
                self.set_profile(configs.get("profile"))
            if "endpoint" in configs:
                self.set_endpoint_url(configs.get("endpoint"))
            if "region" in configs:
                self.set_region(configs.get("region"))
            if "iam_role" in configs:
                self.set_glue_role_arn(configs.get("iam_role"))
            if "session_id" in configs:
                self.set_new_session_id(configs.get("session_id"))
            if "max_capacity" in configs:
                self.set_max_capacity(configs.get("max_capacity"))
            if "number_of_workers" in configs:
                self.set_number_of_workers(configs.get("number_of_workers"))
            if "worker_type" in configs:
                self.set_worker_type(configs.get("worker_type"))
            if "extra_jars" in configs:
                self.set_extra_jars(configs.get("extra_jars"))
            if "connections" in configs:
                self.set_connections(configs.get("connections"))
            if "security_config" in configs:
                self.set_security_config(configs.get("security_config"))
            if "glue_version" in configs:
                self.set_glue_version(configs.get("glue_version"))
            if "idle_timeout" in configs:
                self.set_idle_timeout(configs.get("idle_timeout"))
            if "tags" in configs:
                self.add_tag_to_resource(configs.get("tags"))
            for arg, val in configs.items():
                if arg not in kernel_managed_params:
                    self.add_default_argument(arg, val)
        except Exception as e:
            sys.stderr.write(
                f"The following exception was encountered while parsing the configurations provided: {e} \n"
            )
            self._print_traceback(e)
            return
        if not configs:
            sys.stderr.write("No configuration values were provided.")
        else:
            self._send_output(f"The following configurations have been updated: {configs}")

    def do_shutdown(self, restart):
        self.stop_session()
        return self._do_shutdown(restart)

    def _do_shutdown(self, restart):
        return super(GlueKernel, self).do_shutdown(restart)

    def set_profile(self, profile):
        self.profile = profile
        self._get_configs_from_profile()

    def set_glue_role_arn(self, glue_role_arn):
        self.glue_role_arn = glue_role_arn

    def get_profile(self):
        # Attempt to retrieve default profile if a profile is not already set
        if not self.profile and botocore.session.Session().full_config["profiles"].get("default"):
            self.set_profile("default")
        return self.profile

    def get_glue_role_arn(self):
        return self.glue_role_arn

    def get_sessions(self):
        if not self.glue_client:
            self.glue_client = self._create_glue_client()
        return self.glue_client.list_sessions()

    def get_session_id(self):
        return self.session_id

    def get_new_session_id(self):
        return self.new_session_id

    def set_session_id(self, session_id):
        self.session_id = session_id

    def set_new_session_id(self, new_session_id=None):
        self.new_session_id = self._generate_session_id(new_session_id)

    def set_endpoint_url(self, endpoint_url):
        self.endpoint_url = endpoint_url

    def get_endpoint_url(self):
        return self.endpoint_url

    def set_region(self, region):
        region = region.lower()
        self.region = region

    def get_region(self):
        if not self.region:
            region = os.environ.get("AWS_REGION", None)
            if region:
                self.set_region(region)
        return self.region

    def set_job_type(self, job_type):
        self.job_type = job_type

    def get_job_type(self):
        return self.job_type

    def set_python_version(self, python_version):
        self.python_version = python_version

    def get_python_version(self):
        return self.python_version


    def add_default_argument(self, arg, val):

        if arg in REMAP_DEFAULT_ARGUMENTS:
            arg = REMAP_DEFAULT_ARGUMENTS[arg]

        arg = str(arg) if str(arg).startswith("--") else f'--{arg}'
        val = str(val)

        self.default_arguments[arg] = val

    def get_default_arguments(self):
        if self.default_arguments:
            self._send_output(f"Applying the following default arguments:")
            for arg, val in self.default_arguments.items():
                self._send_output(f"{arg} {val}")
        return self.default_arguments

    def set_enable_glue_datacatalog(self):
        self.add_default_argument("enable-glue-datacatalog", "true")

    def set_extra_py_files(self, extra_py_files):
        self.add_default_argument("extra-py-files", extra_py_files)

    def set_extra_jars(self, extra_jars):
        self.add_default_argument("extra-jars", extra_jars)

    def set_additional_python_modules(self, modules):
        self.add_default_argument("additional-python-modules", modules)

    def set_temp_dir(self, temp_dir):
        self.add_default_argument("TempDir", temp_dir)

    def get_connections(self):
        return self.connections

    def set_connections(self, connections):
        self.connections["Connections"] = list(connections.split(","))

    def get_account_id(self):
        sts_client = self.get_sts_client()
        return sts_client.get_caller_identity().get('Account')

    def get_tags(self):
        return self.tags

    def create_resource_arn(self):
        region = self.get_region()
        if region in CHINA_REGIONS:
            resource_arn = 'arn:aws-cn:glue:' + str(self.get_region()) + ':' + str(self.get_account_id()) + ':session/' + str(self.get_session_id())
        elif region in US_GOV_REGIONS:
            resource_arn = 'arn:aws-us-gov:glue:' + str(self.get_region()) + ':' + str(self.get_account_id()) + ':session/' + str(self.get_session_id())
        else:
            resource_arn = 'arn:aws:glue:' + str(self.get_region()) + ':' + str(self.get_account_id()) + ':session/' + str(self.get_session_id())
        return resource_arn

    def get_tags_from_resource(self):
        if not self.glue_client:
            self.glue_client = self._create_glue_client()
        resource_arn = self.create_resource_arn()
        session_id = self.get_session_id()
        try:
            response = self.glue_client.get_tags(ResourceArn = resource_arn).get("Tags")
            return response
        except Exception:
            self.handle_exception(Exception(f"Unable to fetch tags for the session: {session_id}"))

    def add_tags_to_resource_ready_state(self, tags):
        if not self.glue_client:
            self.glue_client = self._create_glue_client()
        resource_arn = self.create_resource_arn()
        session_id = self.get_session_id()
        if tags:
            try:
                response = self.glue_client.tag_resource(ResourceArn= resource_arn,TagsToAdd=tags)
            except Exception:
                self.handle_exception(Exception(f"Unable to add tags for the session: {session_id}"))
        else:
            return

    def set_tags(self, tags):
        self.tags = tags

    def add_tag(self, key, value):
        self.value = value
        self.tags[key] = self.value

    def add_tag_to_resource(self, tags):
        if tags:
            for (key, value) in tags.items():
                self.add_tag(key, value)

    def remove_tag(self, key):
        del self.tags[key]

    def get_request_origin(self):
        return self.request_origin

    def set_request_origin(self, request_origin):
        self.request_origin = request_origin

    def get_glue_version(self):
        return self.glue_version

    def set_glue_version(self, glue_version):
        glue_version = str(glue_version)
        if glue_version not in VALID_GLUE_VERSIONS:
            try:
                raise Exception(
                    f"Incorrect Glue version value selected. Supported Glue versions are: {VALID_GLUE_VERSIONS}"
                    f"\nNo change will be made to your session.")
            except Exception as e:
                self.handle_exception(e)
        self.glue_version = glue_version

    def get_session_name(self):
        return self.session_name

    def get_max_capacity(self):
        return self.max_capacity

    def set_max_capacity(self, max_capacity):
        self.max_capacity = float(max_capacity)
        self.number_of_workers = None
        self.worker_type = None

    def get_number_of_workers(self):
        return self.number_of_workers

    def set_number_of_workers(self, number_of_workers):
        self.number_of_workers = int(number_of_workers)
        self.max_capacity = None

    def get_worker_type(self):
        return self.worker_type

    def set_worker_type(self, worker_type):
        self.worker_type = worker_type
        self.max_capacity = None

    def get_security_config(self):
        return self.security_config

    def set_security_config(self, security_config):
        self.security_config = security_config

    def get_idle_timeout(self):
        return self.idle_timeout

    def set_idle_timeout(self, idle_timeout):
        self.idle_timeout = int(idle_timeout)

    def set_spark_conf(self, conf):
        self.spark_conf = conf
        return self.add_default_argument("conf", self.spark_conf)

    def get_spark_conf(self):
        return self.spark_conf

    def set_object_memory_head(self, object_memory_head):
        self.add_default_argument("object_store_memory_head", object_memory_head)

    def set_object_memory_worker(self, object_memory_worker):
        self.add_default_argument("object_store_memory_worker", object_memory_worker)

    def set_min_workers(self, min_workers):
        self.add_default_argument("auto-scaling-ray-min-workers", min_workers)

    def set_session_id_prefix(self, session_id_prefix):
        self.session_id_prefix = session_id_prefix

    def get_session_id_prefix(self):
        if self.session_id_prefix:
            return self.session_id_prefix
        if self.get_profile():
            prefix_from_profile = self._retrieve_from_aws_config("session_id_prefix")
            if prefix_from_profile:
                return prefix_from_profile
        # sts_client = self.get_sts_client()
        # return sts_client.get_caller_identity().get('UserId')
        return ""

    def _generate_session_id(self, custom_id=None):
        prefix = self.get_session_id_prefix()
        if prefix:
            if not custom_id:
                return f"{prefix}-{uuid.uuid4()}"
            return f"{prefix}-{custom_id}"
        else:
            if not custom_id:
                return f"{uuid.uuid4()}"
            return custom_id

    def disconnect(self):
        if self.get_session_id():
            session_id = self.get_session_id()
            self.set_session_id(None)
            self.set_new_session_id(None)
            self._send_output(f"Disconnected from session {session_id}")
        else:
            sys.stderr.write(f"Not currently connected to a session. \n")

    def reconnect(self, session_id):
        if self.get_session_id():
            self.disconnect()
        self._send_output(f"Trying to connect to {session_id}")
        self.set_session_id(session_id)
        # Verify that this session exists.
        try:
            # TODO: create glue client if it doesn't exist
            self.glue_client.get_session(Id=self.get_session_id())
            self._send_output(f"Connected to {session_id}")
        except Exception as e:
            sys.stderr.write(f"Exception encountered while connecting to session: {e} \n")
            self._print_traceback(e)

    def create_session(self):
        self._send_output("Trying to create a Glue session for the kernel.")
        if self.get_max_capacity() and (self.get_number_of_workers() and self.get_worker_type()):
            raise ValueError(
                f"Either max_capacity or worker_type and number_of_workers must be set, but not both."
            )

        # Generate new session ID with UUID if no custom ID is set
        if not self.get_new_session_id():
            self.set_new_session_id()
            if not self.get_new_session_id():
                raise ValueError(f"Session ID was not set.")

        # Print Max Capacity if it is set. Else print Number of Workers and Worker Type
        if self.get_max_capacity():
            self._send_output(f"Max Capacity: {self.get_max_capacity()}")
        else:
            if self.get_job_type() != JobType.glue_ray.value:
                self._send_output(f"Worker Type: {self.get_worker_type()}")
            else:
                self.set_worker_type("Z.2X")
                self._send_output(f"Worker Type: {self.get_worker_type()}")
            self._send_output(f"Number of Workers: {self.get_number_of_workers()}")

        self._send_output(f"Session ID: {self.get_new_session_id()}")
        self._send_output(f"Job Type: {self.get_job_type()}")

        additional_args = self._get_additional_arguments()
        response = self.glue_client.create_session(
            Role=self.get_glue_role_arn(),
            DefaultArguments=self.get_default_arguments(),
            Id=self.get_new_session_id(),
            Command={"Name": self.get_job_type(), "PythonVersion": self.get_python_version()},
            **additional_args,
        )
        self.set_session_id(
            response["Session"]["Id"]
        )

        self._send_output(
            f"Waiting for session {self.get_session_id()} to get into ready status..."
        )
        start_time = time.time()
        current_status = None
        while time.time() - start_time <= self.time_out:
            current_status = self.get_current_session_status()
            if current_status == READY_SESSION_STATUS:
                break
            elif current_status == PROVISIONING_SESSION_STATUS:
                time.sleep(WAIT_TIME)
                continue
            elif current_status in UNHEALTHY_SESSION_STATUS:
                break
            else:
                time.sleep(WAIT_TIME)
                continue

        if time.time() - start_time > self.time_out:
            self._send_error_output(f"Timed out after {self.time_out} seconds waiting for session to reach {READY_SESSION_STATUS} status.")
        elif current_status in UNHEALTHY_SESSION_STATUS:
            self._send_error_output(f"Session failed to reach {READY_SESSION_STATUS} instead reaching terminal state {self.get_current_session_status()}.")
        elif current_status != READY_SESSION_STATUS:
            self._send_error_output(f"Session failed to reach {READY_SESSION_STATUS} status.")
        else:
            self._send_output(f"Session {self.get_session_id()} has been created.")

    def _get_additional_arguments(self):
        additional_args = {}
        if self.get_max_capacity():
            additional_args["MaxCapacity"] = self.get_max_capacity()
        if self.get_number_of_workers():
            additional_args["NumberOfWorkers"] = self.get_number_of_workers()
        if self.get_worker_type():
            additional_args["WorkerType"] = self.get_worker_type()
        if self.get_security_config() and self.get_job_type() != JobType.glue_ray.value:
            additional_args["SecurityConfiguration"] = self.get_security_config()
        if self.get_idle_timeout():
            additional_args["IdleTimeout"] = self.get_idle_timeout()
        if self.get_connections() and self.get_job_type() != JobType.glue_ray.value:
            additional_args["Connections"] = self.get_connections()
        if self.get_glue_version():
            additional_args["GlueVersion"] = self.get_glue_version()
        if self.get_request_origin():
            additional_args["RequestOrigin"] = self.get_request_origin()

        # add tags
        if self.get_request_origin() == GLUE_STUDIO_NOTEBOOK_IDENTIFIER:
            user_id = self._retrieve_os_env_variable(USER_ID)
        else:
            user_id = self._get_user_id()
        if user_id:  # check if user ID exists and if so, add it as a tag
            self.add_tag(OWNER_TAG, user_id)
        tags = self.get_tags()
        if len(tags) > 0:
            additional_args["Tags"] = tags

        return additional_args

    def stop_session(self):
        if self.get_session_id():
            try:
                self._send_output(f"Stopping session: {self.get_session_id()}")
                # TODO: how do we stop session if our security token expires?
                self.glue_client.stop_session(Id=self.get_session_id())
                self.reset_kernel()
            except Exception as e:
                sys.stderr.write(
                    f"Exception encountered while stopping session {self.get_session_id()}: {e} \n"
                )
                self._print_traceback(e)

    def _cancel_statement(self, statement_id: str):
        if not statement_id:
            return

        try:
            self.glue_client.cancel_statement(SessionId=self.get_session_id(), Id=statement_id)
            start_time = time.time()
            is_ready = False

            while time.time() - start_time <= self.time_out and not is_ready:
                status = self.glue_client.get_statement(
                    SessionId=self.get_session_id(), Id=statement_id
                )["Statement"]["State"]

                if status == CANCELLED_STATEMENT_STATUS:
                    self._send_output(f"Statement {statement_id} has been cancelled")
                    is_ready = True

                time.sleep(WAIT_TIME)

            if not is_ready:
                sys.stderr.write(f"Failed to cancel the statement {statement_id}")
        except Exception as e:
            sys.stderr.write(
                f"Exception encountered while canceling statement {statement_id}: {e} \n"
            )
            self._print_traceback(e)

    def get_session_status(self):
        if self.get_session_id() is None:
            return
        else:
            try:
                return self.glue_client.get_session(Id=self.get_session_id())["Session"].get("Status")
            except Exception as e:
                return None

    def get_current_session_status(self):
        try:
            return self.get_current_session()["Status"]
        except Exception as e:
            sys.stderr.write(f"Failed to retrieve session status \n")

    # def get_current_session_duration_in_seconds(self):
    #     try:
    #         time_in_seconds = datetime.now(tzlocal()) - self.get_current_session()["CreatedOn"]
    #         return time_in_seconds.total_seconds()
    #     except Exception as e:
    #         sys.stderr.write(f"Failed to retrieve session duration \n")

    def get_current_session_role(self):
        try:
            return self.get_current_session()["Role"]
        except Exception as e:
            sys.stderr.write(f"Failed to retrieve session role \n")

    def get_current_session(self):
        if self.get_session_id() is None:
            sys.stderr.write(f"No current session.")
        else:
            try:
                current_session = self.glue_client.get_session(Id=self.get_session_id())["Session"]
                return NOT_FOUND_SESSION_STATUS if not current_session else current_session
            except Exception as e:
                sys.stderr.write(f"Exception encountered while retrieving session: {e} \n")
                self._print_traceback(e)

    def get_sts_client(self):
        if not self.sts_client:
            self.create_sts_client()
        return self.sts_client

    def create_sts_client(self):
        if not self.get_region():
            raise ValueError(f"Region must be set.")
        if self.get_profile():
            self.sts_client = boto3.Session(profile_name=self.get_profile()).client(
                "sts", region_name=self.get_region()
            )
        else:
            self.sts_client = boto3.Session().client(
                "sts",
                region_name=self.get_region(),
                endpoint_url=self._get_sts_endpoint_url(self.get_region()),
            )

    def _handle_sql_code(self, lines):
        sql_code = "\n".join(lines[1:])
        return f'spark.sql("""{sql_code.rstrip()}""").show()'


    def _send_markdown_output(self, output):
        self.send_response(self.iopub_socket, 'display_data', {
            'metadata': {},
            'data': {
                'text/markdown': output
            }
        })

    def _send_output(self, output):
        stream_content = {"name": "stdout", "text": f"{output}\n"}
        self.send_response(self.iopub_socket, "stream", stream_content)

    def _send_error_output(self, output):
        stream_content = {"name": "stderr", "text": f"{output}\n"}
        self.send_response(self.iopub_socket, "stream", stream_content)

    def _construct_reply_content(self, statement):

        statement_output = statement["Output"]
        status = statement["State"]
        reply_content = {
            "execution_count": self.execution_counter,
            "user_expressions": {},
            "payload": [],
        }

        if status in (AVAILABLE_STATEMENT_STATUS, COMPLETED_STATEMENT_STATUS):
            self.execution_counter += 1
            if status == COMPLETED_STATEMENT_STATUS or ('Status' in statement_output and statement_output["Status"] == "ok"):
                reply_content["status"] = "ok"
                self.display_result(statement_output)
            else:
                reply_content["status"] = "error"
                reply_content.update(
                    {
                        "traceback": statement_output["Traceback"],
                        "ename": statement_output["ErrorName"],
                        "evalue": statement_output["ErrorValue"],
                    }
                )
                self._send_output(
                    f"{statement_output['ErrorName']}: {statement_output['ErrorValue']}"
                )
        elif status == ERROR_STATEMENT_STATUS:
            self.execution_counter += 1
            sys.stderr.write(str(statement_output))
            reply_content.update(self._construct_reply_error(statement_output))
        elif status == FAILED_STATEMENT_STATUS:
            self.execution_counter += 1
            reply_content.update(self._construct_reply_error(statement_output))
            if 'Data' in statement_output:
                statement_output_data = statement_output['Data']
                stdout_text = self.get_results(statement_output_data['StdOut']) if 'StdOut' in statement_output_data else ""
                if len(stdout_text):
                    self._send_output(stdout_text)
                failure_reason = self.get_results(statement_output_data['Result']) if 'Result' in statement_output_data else ""
                if len(failure_reason):
                    self._send_error_output(failure_reason)
                stderr_text = self.get_results(statement_output_data['StdErr']) if 'StdErr' in statement_output_data else ""
                if len(stderr_text):
                    self._send_error_output(stderr_text)

        elif status == CANCELLED_STATEMENT_STATUS:
            self.execution_counter += 1
            reply_content.update(self._construct_reply_error(statement_output))
            self._send_output("This statement is cancelled")

        return reply_content

    def _construct_reply_error(self, statement_output):
        if (not statement_output) or (not all(map(lambda x: x in statement_output, ['TraceBack', 'ErrorName', 'ErrorValue']))):
            return dict({"status": "abort"})
        else:
            return dict({
                "status": "error",
                "traceback": statement_output["Traceback"],
                "ename": statement_output["ErrorName"],
                "evalue": statement_output["ErrorValue"],
            })

    def get_results(self, s3_path):
        if not s3_path.startswith("s3"):
            self._send_output(f"No output file found at {s3_path}")
            return "No output file found"
        try:
            s3session = boto3.Session(profile_name=self.get_profile())
            s3client = s3session.client("s3", region_name=self.get_region(), config=Config(retries=dict(max_attempts=10)))

            urlparts = parse_url(s3_path)
            s3_object = s3client.get_object(Bucket=urlparts.host,Key=urlparts.path[1:])
            return s3_object["Body"].read().decode("utf-8")
        except botocore.exceptions.ClientError as e:
            self._send_output(f"Response from get_object with {s3_path} was {e}")
            raise RuntimeError("Error while getting calculation results", e)

    def split_s3_path(self, s3_path):
        path_parts = s3_path.replace("s3://", "").split("/")
        bucket = path_parts.pop(0)
        key = "/".join(path_parts)
        return bucket, key

    async def _do_execute(self, code, silent, store_history, user_expressions, allow_stdin):
        res = await self._execute_cell(code, silent, store_history, user_expressions, allow_stdin)
        return res

    async def _execute_cell(
            self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        reply_content = await self._execute_cell_for_user(
            code, silent, store_history, user_expressions, allow_stdin
        )
        return reply_content

    async def _execute_cell_for_user(
            self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        result = await super(GlueKernel, self).do_execute(
            code, silent, store_history, user_expressions, allow_stdin
        )
        if isinstance(result, Future):
            result = result.result()
        return result

    async def _execute_magics(self, code, silent, store_history, user_expressions, allow_stdin):
        try:
            magic_lines = 0
            lines = code.splitlines()
            for line in lines:
                # If there is a cell magic, we simply treat all the remaining code as part of the cell magic
                if any(line.startswith(cell_magic) for cell_magic in CELL_MAGICS):
                    if line.startswith(SQL_CELL_MAGIC):
                        return self._handle_sql_code(lines)
                    else:
                        code = "\n".join(lines[magic_lines:])
                        await self._do_execute(
                            code, silent, store_history, user_expressions, allow_stdin
                        )
                    return None
                # If we encounter a line magic, we execute this line magic and continue
                if line.startswith("%") or line.startswith("!"):
                    await self._do_execute(
                        line, silent, store_history, user_expressions, allow_stdin
                    )
                    magic_lines += 1
                # We ignore comments and empty lines
                elif line.startswith("#") or not line:
                    magic_lines += 1
                else:
                    break
            code = "\n".join(lines[magic_lines:])
            return code
        except Exception as e:
            sys.stderr.write(f"Exception encountered: {e} \n")
            self._print_traceback(e)
            return await self._complete_cell()

    async def _complete_cell(self):
        """A method that runs a cell with no effect. Call this and return the value it
        returns when there's some sort of error preventing the user's cell from executing; this
        will register the cell from the Jupyter UI as being completed."""
        return await self._execute_cell("None", False, True, None, False)

    def _register_magics(self):
        ip = get_ipython()
        magics = KernelMagics(ip, "", self)
        ip.register_magics(magics)

    def _print_traceback(self, e):
        traceback.print_exception(type(e), e, e.__traceback__)

    async def _print_startup_text(self):
        self._send_output("Welcome to the Glue Interactive Sessions Kernel")
        self._send_output(
            "For more information on available magic commands, please type %help in any new cell.\n"
        )
        self._send_output(
            "Please view our Getting Started page to access the most up-to-date information on the Interactive Sessions kernel: https://docs.aws.amazon.com/glue/latest/dg/interactive-sessions.html"
        )
        self.should_print_startup_text = False
        current_kernel_version = self._get_current_kernel_version("aws-glue-sessions")
        latest_kernel_version = self._get_latest_kernel_version("aws-glue-sessions")
        if (
                latest_kernel_version
                and current_kernel_version
                and latest_kernel_version != current_kernel_version
        ):
            self._send_output(
                f"It looks like there is a newer version of the kernel available. The latest version is {latest_kernel_version} and you have {current_kernel_version} installed."
            )
            self._send_output(
                "Please run `pip install --upgrade aws-glue-sessions` to upgrade your kernel"
            )
        elif latest_kernel_version is None and current_kernel_version is not None:
            self._send_output(f"Installed kernel version: {current_kernel_version} ")

    def _get_latest_kernel_version(self, name):
        if not self.request_origin == "GlueStudioNotebook":
            try:
                response = requests.get("https://pypi.org/pypi/{}/json".format(name))
                data = response.json()
                latest_version = data["info"]["version"]
                return str(latest_version)
            except Exception:
                return None

    def _get_current_kernel_version(self, name):
        try:
            current_version = version(name)
            return str(current_version)
        except Exception:
            return None

    def reset_kernel(self):
        self.glue_client = None
        self.set_session_id(None)
        self.set_new_session_id(None)
        self.execution_counter = 1
        self.set_tags(defaultdict())

    # https://github.com/ipython/ipykernel/issues/795
    # Redirect logs to only print in terminal
    def _setup_terminal_logging(self):
        for std, __std__ in [
            (sys.stdout, sys.__stdout__),
            (sys.stderr, sys.__stderr__),
        ]:
            if getattr(std, "_original_stdstream_copy", None) is not None:
                # redirect captured pipe back to original FD
                os.dup2(std._original_stdstream_copy, __std__.fileno())
                std._original_stdstream_copy = None

    def _log_to_terminal(self, log):
        print(f"LOG: {log}", file=sys.__stdout__, flush=True)

    def _get_user_id(self):
        sts_client = self.get_sts_client()
        return sts_client.get_caller_identity().get("UserId")

    def _get_iam_role_using_sts(self):
        try:
            sts_client = self.get_sts_client()
            role_arn = sts_client.get_caller_identity().get("Arn")
        except Exception:
            return None
        regex = r"arn:aws[^:]*:sts::[0-9]*:assumed-role/(.+)/.+"
        m = re.match(regex, role_arn)
        if m:
            role_arn = self._get_role_arn_from_iam(m.group(1))
            return role_arn

        return None

    def _get_role_arn_from_iam(self, role_name):
        client = boto3.client("iam", region_name=self.get_region())
        return client.get_role(RoleName=role_name).get("Role", {}).get("Arn", None)

    def _retrieve_os_env_variable(self, key):
        if self.get_request_origin() not in SAGEMAKER_STUDIO_NOTEBOOK_IDENTIFIERS:
            return os.environ.get(key)
        else:
            _, output = subprocess.getstatusoutput(f"echo ${key}")
            return os.getenv(key, output)

    def _create_glue_client(self):
        return self.authenticate(glue_role_arn=self.get_glue_role_arn(), profile=self.get_profile())

    def _get_sts_endpoint_url(self, region):
        if region in CHINA_REGIONS:
            return f"https://sts.{region}.amazonaws.com.cn"
        return f"https://sts.{region}.amazonaws.com"

    def _format_endpoint_url(self, region):
        if region in CHINA_REGIONS:
            return f"https://glue.{region}.amazonaws.com.cn"
        return f"https://glue.{region}.amazonaws.com"

    def handle_exception(self, e):
        print(Colour.Red + "Error: " + str(e))


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=GlueKernel)
