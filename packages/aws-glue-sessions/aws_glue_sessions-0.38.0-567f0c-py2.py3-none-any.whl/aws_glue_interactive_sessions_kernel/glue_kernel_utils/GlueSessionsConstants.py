import pathlib
from enum import Enum, unique


# Symbols for referencing Mime types
class MimeTypes(Enum):
    TextPlain = ("text/plain")
    ImagePng = ("image/png")
    S3URI = ("text/uri-list")


# Symbols for referencing Job types
@unique
class JobType(Enum):

    def __new__(cls, value, pretty_name, valid_worker_types, python_version, idle_timeout, min_workers, supported_kernels):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._python_version = python_version
        obj._pretty_name = pretty_name
        obj._idle_timeout = idle_timeout
        obj._min_workers = min_workers
        obj._supported_kernels = supported_kernels
        if not hasattr(cls, '_logger'):
            import logging
            cls._logger = logging.getLogger(cls.__name__)
        cls._logger.debug(f'{cls} value={value} valid_worker_types={valid_worker_types}')
        if not hasattr(cls, '_VALID_WORKER_TYPES'):
            cls._VALID_WORKER_TYPES = dict()
        cls._VALID_WORKER_TYPES.update(
            {
                obj._value_: tuple(valid_worker_types)
            }
        )
        return obj

    @classmethod
    def lookup(cls, value):
        result = list(filter(lambda x: x._value_ == value, list(cls)))
        if result:
            return result[0]
        else:
            result = list(filter(lambda x: x.name == value, list(cls)))
            if result:
                return result[0]
            else:
                return cls(value)

    etl = ("glueetl", 'ETL', ["G.1X", "G.2X", "G.4X", "G.8X"], "3", 2800, None, ['GluePySparkKernel', 'GlueSparkKernel',
                                                                 'SageMakerStudioPySparkNotebook',
                                                                 'SageMakerStudioSparkNotebook', 'GlueStudioNotebook'])
    streaming = ("gluestreaming", 'Streaming', ["G.1X", "G.2X"], "3", 2880, None,
                 ['GluePySparkKernel', 'GlueSparkKernel', 'SageMakerStudioPySparkNotebook',
                  'SageMakerStudioSparkNotebook', 'GlueStudioNotebook'])
    glue_ray = ("glueray", 'Glue Ray', ["Z.2X"], "3.9", 60, "1", ['GluePySparkKernel', 'SageMakerStudioPySparkNotebook',
                                                                  'GlueStudioNotebook'])

    def worker_types(self):
        return list(self.__class__._VALID_WORKER_TYPES.get(self._value_))

    def default_worker(self):
        return self.worker_types()[0]

    def python_version(self):
        return self._python_version

    def apply(self, kernel):
        if kernel.request_origin not in self._supported_kernels:
            kernel._send_error_output(
                f'The requested job type "{self.value}" is not supported by kernel {kernel.request_origin}.')
        else:
            kernel._set_default_arguments()
            kernel.set_job_type(self._value_)
            kernel.set_python_version(self._python_version)
            kernel.set_worker_type(self.default_worker())
            kernel.set_idle_timeout(self._idle_timeout)
            if self._min_workers:
                kernel.set_min_workers(self._min_workers)

    def pretty_name(self):
        return self._pretty_name

WAIT_TIME = 1

READY_SESSION_STATUS = "READY"
PROVISIONING_SESSION_STATUS = "PROVISIONING"
NOT_FOUND_SESSION_STATUS = "NOT_FOUND"
FAILED_SESSION_STATUS = "FAILED"
STOPPING_SESSION_STATUS = "STOPPING"
STOPPED_SESSION_STATUS = "STOPPED"
TIMEOUT_SESSION_STATUS = "TIMEOUT"
UNHEALTHY_SESSION_STATUS = [NOT_FOUND_SESSION_STATUS, FAILED_SESSION_STATUS, STOPPING_SESSION_STATUS,
                            STOPPED_SESSION_STATUS]

ERROR_STATEMENT_STATUS = "ERROR"
FAILED_STATEMENT_STATUS = "FAILED"
CANCELLED_STATEMENT_STATUS = "CANCELLED"
AVAILABLE_STATEMENT_STATUS = "AVAILABLE"
COMPLETED_STATEMENT_STATUS = "COMPLETED"
FINAL_STATEMENT_STATUS = [FAILED_STATEMENT_STATUS, ERROR_STATEMENT_STATUS, CANCELLED_STATEMENT_STATUS,
                          AVAILABLE_STATEMENT_STATUS, COMPLETED_STATEMENT_STATUS]
SQL_CELL_MAGIC = "%%sql"

CELL_MAGICS = {"%%configure", "%%sql", "%%ray_conf", "%%tags"}

VALID_GLUE_VERSIONS = {"2.0", "3.0", "4.0"}

CHINA_REGIONS = {"cn-north-1", "cn-northwest-1"}

US_GOV_REGIONS = {"us-gov-east-1","us-gov-west-1"}


class Colour:
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Magenta = "\033[35m"
    Cyan = "\033[36m"
    LightGray = "\033[37m"
    DarkGray = "\033[90m"
    LightRed = "\033[91m"
    LightGreen = "\033[92m"
    LightYellow = "\033[93m"
    LightBlue = "\033[94m"
    LightMagenta = "\033[95m"
    LightCyan = "\033[96m"
    White = "\033[97m"
    Bold = "\033[1m"
    Reset = "\033[0m"


HELP_TEXT = f'''
# Available Magic Commands

## Sessions Magic

----
    %help                             Return a list of descriptions and input types for all magic commands. 
    %profile            String        Specify a profile in your aws configuration to use as the credentials provider.
    %region             String        Specify the AWS region in which to initialize a session. 
                                      Default from ~/.aws/config on Linux or macOS, 
                                      or C:\\Users\\ USERNAME \\.aws\\config" on Windows.
    %idle_timeout       Int           The number of minutes of inactivity after which a session will timeout. 
                                      Default: 2880 minutes (48 hours).
    %session_id_prefix  String        Define a String that will precede all session IDs in the format 
                                      [session_id_prefix]-[session_id]. If a session ID is not provided,
                                      a random UUID will be generated.
    %status                           Returns the status of the current Glue session including its duration, 
                                      configuration and executing user / role.
    %session_id                       Returns the session ID for the running session. 
    %list_sessions                    Lists all currently running sessions by ID.
    %stop_session                     Stops the current session.
    %glue_version       String        The version of Glue to be used by this session. 
                                      Currently, the only valid options are 2.0, 3.0 and 4.0. 
                                      Default: 2.0.
----

## Selecting Job Types

----
    %streaming          String        Sets the session type to Glue Streaming.
    %etl                String        Sets the session type to Glue ETL.
    %glue_ray           String        Sets the session type to Glue Ray.
----

## Glue Config Magic 
*(common across all job types)*

----

    %%configure         Dictionary    A json-formatted dictionary consisting of all configuration parameters for 
                                      a session. Each parameter can be specified here or through individual magics.
    %iam_role           String        Specify an IAM role ARN to execute your session with.
                                      Default from ~/.aws/config on Linux or macOS, 
                                      or C:\\Users\\%USERNAME%\\.aws\\config` on Windows.
    %number_of_workers  int           The number of workers of a defined worker_type that are allocated 
                                      when a session runs.
                                      Default: 5.
    %additional_python_modules  List  Comma separated list of additional Python modules to include in your cluster 
                                      (can be from Pypi or S3).
    %%tags        Dictionary          Specify a json-formatted dictionary consisting of tags to use in the session.
----

                                      
## Magic for Spark Jobs (ETL & Streaming)

----
    %worker_type        String        Set the type of instances the session will use as workers. 
                                      {JobType.etl.pretty_name()} and {JobType.streaming.pretty_name()} support {", ".join(JobType.etl.worker_types()[:-1])} and {JobType.etl.worker_types()[-1]}. 
                                      Default: {JobType.etl.default_worker()}.
    %connections        List          Specify a comma separated list of connections to use in the session.
    %extra_py_files     List          Comma separated list of additional Python files From S3.
    %extra_jars         List          Comma separated list of additional Jars to include in the cluster.
    %spark_conf         String        Specify custom spark configurations for your session. 
                                      E.g. %spark_conf spark.serializer=org.apache.spark.serializer.KryoSerializer
----
                                      
## Magic for Ray Job

----
    %min_workers        Int           The minimum number of workers that are allocated to a Ray job. 
                                      Default: 1.
    %object_memory_head Int           The percentage of free memory on the instance head node after a warm start. 
                                      Minimum: 0. Maximum: 100.
    %object_memory_worker Int         The percentage of free memory on the instance worker nodes after a warm start. 
                                      Minimum: 0. Maximum: 100.
----

## Action Magic

----

    %%sql               String        Run SQL code. All lines after the initial %%sql magic will be passed
                                      as part of the SQL code.  
----

'''

OWNER_TAG = "owner"
GLUE_STUDIO_NOTEBOOK_IDENTIFIER = "GlueStudioNotebook"
SAGEMAKER_STUDIO_NOTEBOOK_IDENTIFIERS = ['SageMakerStudioPySparkNotebook', 'SageMakerStudioSparkNotebook']

# GlueStudio Env Variables
REQUEST_ORIGIN = "request_origin"
REGION = "region"
SESSION_ID = "session_id"
GLUE_ROLE_ARN = "glue_role_arn"
GLUE_VERSION = "glue_version"
GLUE_JOB_TYPE = "glue_job_type"
USER_ID = "userId"

REMAP_DEFAULT_ARGUMENTS = {
    "min_workers": "auto-scaling-ray-min-workers",
    "object_memory_head": "object_store_memory_head",
    "object_memory_worker": "object_store_memory_worker"
}

RAY_INVALID_REGION_ERROR = "An error occurred (InvalidInputException) when calling the CreateSession operation: Account not allowed to submit Glue Ray session"
