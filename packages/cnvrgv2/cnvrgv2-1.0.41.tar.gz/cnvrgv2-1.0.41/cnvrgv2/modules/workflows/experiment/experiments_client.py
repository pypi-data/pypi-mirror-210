import io
import os
import shlex
import subprocess
import sys
import threading
import re
from contextlib import redirect_stdout, redirect_stderr
import inspect
from cnvrgv2.modules.images.image import Image
from cnvrgv2.config.error_messages import MISSING_EXPERIMENT_ARGUMENT, NOT_A_DATASET_LIST_OBJECT, NOT_A_VOLUME_OBJECT, \
    EXPERIMENT_CANNOT_BE_A_FUNCTION, EXPERIMENT_MISSING_COMMAND_ARGUMENT
from cnvrgv2.context import SCOPE
from cnvrgv2.config import routes
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.modules.base.workflows_base import WorkflowsBase
from cnvrgv2.modules.volumes.volume import Volume
from cnvrgv2.modules.dataset import Dataset
from cnvrgv2.modules.workflows import Experiment
from cnvrgv2.modules.workflows.workflow_utils import WorkflowUtils, WorkflowStatuses
from cnvrgv2.proxy import HTTP
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.log_utils import LOGS_TYPE_OUTPUT, LOGS_TYPE_ERROR, log_buffer
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.utils.validators import validate_types_in_list, validate_hyper_parameters
from cnvrgv2.utils.env_helper import ENV_KEYS


class ExperimentsClient(WorkflowsBase):
    def __init__(self, project):
        super().__init__(Experiment, "Experiment", project._context)

        scope = self._context.get_scope(SCOPE.PROJECT)
        self.project = project
        self._route = routes.EXPERIMENTS_BASE.format(scope["organization"], scope["project"])

    def init(self, title=None, **kwargs):
        """
        Creates an experiment that doesn't run anything locally or on remote
        @param title: Title of the experiment
        @param kwargs: Additional arguments
        @return: The new experiment object
        """
        kwargs = {
            "clean_experiment": True,
            **kwargs
        }
        return self.create(title=title, local=True, sync_before=False, sync_after=False, **kwargs)

    def create(
            self,
            title=None,
            templates=None,
            local=False,
            command=None,
            local_arguments=None,
            datasets=None,
            volume=None,
            sync_before=True,
            sync_after=True,
            wait=False,
            **kwargs
    ):
        """
        Create and run a new experiment
        @param title: Name of the experiment
        @param templates: Templates to run the experiment on
        @param local: Boolean. Run the experiment locally
        @param command: The command to run. can be a function in case of a local experiment
        @param local_arguments: If local experiment and command is a function,
               local_arguments is a dictionary of the arguments to pass to the experiment's function
        @param datasets: list of datasets to use in the experiment.
        @param volume: A volume to attach to this experiment. (type: Volume object).
        @param args: optional arguments
        @param sync_before: Boolean. sync environment before running the experiment
        @param sync_after: Boolean. sync environment after the experiment finished
        @param wait: Wait for the experiment to finish
        @param kwargs: Dictionary. Rest of optional attributes for creation
            image: Image object to create experiment with
            git_branch: The branch to pull files from for the experiment, in case project is git project
            git_commit: The commit to pull files from for the experiment, in case project is git project
            queue: Name of the queue to run this job on
            output_dir: Sets the output folder for cnvrg to track experiment artifacts
            local_folder: Local folders to mount with the experiment
        @return: The experiment's object
        """
        m_kwargs = {
            "command": command,
            "local": local,
            **kwargs
        }

        if volume and not isinstance(volume, Volume):
            raise CnvrgArgumentsError(NOT_A_VOLUME_OBJECT)
        elif volume:
            m_kwargs["external_disk_slug"] = volume.slug

        if datasets and not validate_types_in_list(datasets, Dataset):
            raise CnvrgArgumentsError(NOT_A_DATASET_LIST_OBJECT)
        elif datasets:
            m_kwargs["job_datasets"] = [ds.as_request_params() for ds in datasets]

        if callable(command):
            if local:
                # if command is function, run it as a function and not as a os command. Update kwargs appropriately
                func_args = inspect.signature(command).parameters.keys()
                if "experiment" not in func_args:
                    raise CnvrgArgumentsError(MISSING_EXPERIMENT_ARGUMENT)
                m_kwargs["command"] = "func: {func_name}".format(func_name=command.__name__)
            else:
                raise CnvrgArgumentsError(EXPERIMENT_CANNOT_BE_A_FUNCTION)

        if sync_before and not self.project.git:
            self.project.sync()

        m_kwargs['job_parent_id'] = os.environ.get(ENV_KEYS['current_job_id'])

        experiment = super().create(title, templates, **m_kwargs)

        if local and not m_kwargs.get("clean_experiment", False):
            local_arguments = local_arguments or {}
            exit_status = self._prepare_local_experiment(
                experiment=experiment,
                executable=command,
                working_dir=m_kwargs.get("cwd", None),
                arguments={"experiment": experiment, **local_arguments},
            )

            if sync_after:
                self.project.sync()

            experiment.finish(exit_status)

        if wait:
            WorkflowUtils.wait_for_statuses(experiment, WorkflowStatuses.FINAL_STATES)

        return experiment

    def create_grid(
            self,
            title=None,
            templates=None,
            command=None,
            datasets=None,
            volume=None,
            sync_before=True,
            parameters=None,
            **kwargs
    ):
        """
        Create and run a new experiment
        @param title: Name of the experiment
        @param templates: Templates to run the experiment on
        @param command: The command to run. can be a function in case of a local experiment
        @param datasets: list of datasets to use in the experiment.
        @param volume: A volume to attach to this experiment. (type: Volume object).
        @param sync_before: Boolean. sync environment before running the experiment
        @param parameters: A dictionary of parameters to pass to the experiment
        @param kwargs: Dictionary. Rest of optional attributes for creation
            image: Image object to create experiment with
            git_branch: The branch to pull files from for the experiment, in case project is git project
            git_commit: The commit to pull files from for the experiment, in case project is git project
            queue: Name of the queue to run this job on
        @return: The grid slug
        """

        attributes = self._prepare_create_grid_attributes(title,
                                                          templates,
                                                          command,
                                                          datasets,
                                                          volume,
                                                          parameters,
                                                          **kwargs)
        if not command:
            raise CnvrgArgumentsError(EXPERIMENT_MISSING_COMMAND_ARGUMENT)

        if callable(command):
            raise CnvrgArgumentsError(EXPERIMENT_CANNOT_BE_A_FUNCTION)

        if sync_before and not self.project.git:
            self.project.sync()

        response = self._proxy.call_api(
            route=urljoin(self.project._route, routes.EXPERIMENT_HYPER_SUFFIX),
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

        return response.attributes["hyper_search_slug"]

    def _prepare_create_grid_attributes(self, title, templates, command, datasets, volume, parameters, **kwargs):

        if isinstance(kwargs.get("image"), Image):
            kwargs["image_slug"] = kwargs.get("image").slug
            del kwargs["image"]

        if kwargs.get("queue", False):
            kwargs["queue_name"] = kwargs.get("queue", False)
            del kwargs["queue"]

        if volume and not isinstance(volume, Volume):
            raise CnvrgArgumentsError(NOT_A_VOLUME_OBJECT)
        elif volume:
            kwargs["external_disk_slug"] = volume.slug

        if datasets and not validate_types_in_list(datasets, Dataset):
            raise CnvrgArgumentsError(NOT_A_DATASET_LIST_OBJECT)
        elif datasets:
            kwargs["job_datasets"] = [ds.as_request_params() for ds in datasets]

        attributes = {"title": title, "template_names": templates, "command": command, "params": parameters, **kwargs}

        # Todo: Support Optimizations
        attributes["algorithm"] = "GridSearch"

        # Validate parameters
        validate_hyper_parameters(attributes["params"])

        return attributes

    def _prepare_local_experiment(self, experiment, executable, working_dir, arguments: dict = None):

        """
        Prepares the local experiment before running and runs the experiment
        @param experiment: The experiment's object
        @param executable: The function to be run locally
        @param working_dir: The working dir
        @param arguments: In case user sent a function: Additional arguments to send to the user's function
        @return: execution's exit status
        """
        if callable(executable):
            with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
                return self._run_local_experiment(
                    experiment=experiment,
                    arguments=arguments,
                    stdout=stdout,
                    stderr=stderr,
                    exp_func=executable,
                )
        else:
            env = experiment.as_env()
            process = self._run_subprocess(cmd=executable, cwd=working_dir, env=env)
            stdout = process.stdout
            stderr = process.stderr
            return self._run_local_experiment(
                experiment=experiment,
                stdout=stdout,
                stderr=stderr,
                command_proc=process
            )

    @staticmethod
    def _run_subprocess(cmd, cwd=None, env=None):
        """
        Opens a subprocess that runs the user's command locally
        @param cmd: The command to run
        @param cwd: The working dir to work in
        @param env: Environment parameters
        @return: The subprocess running the command
        """
        env = dict({**os.environ, **(env or {}), **{'PYTHONUNBUFFERED': "1"}})
        cmd = re.sub(r"^(python3?)", r"{exe} -u".format(exe=sys.executable), cmd)
        cmd = shlex.split(cmd)

        params = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'close_fds': False,
            'bufsize': 1,
        }
        if cwd:
            params['cwd'] = r"{}".format(cwd)
        if env:
            params["env"] = env
        return subprocess.Popen(cmd, **params)

    @staticmethod
    def _run_local_experiment(experiment, stdout, stderr, arguments=None, exp_func=None, command_proc=None):
        """
        Runs local experiment and tracks logs written during the experiment
        @param experiment: The experiment's object
        @param stdout: The standard output logs are written to
        @param stderr: The standard errors output logs are written to
        @param arguments: In case user sent a function: Additional arguments to send to the user's function
        @param exp_func: The user's function to run, in case command was a function
        @param command_proc: The function to run the user's command, in case a command was sent
        @return: exit status of the experiment's execution
        """

        exit_status = None

        t_out = threading.Thread(target=log_buffer, kwargs={
            "buffer": stdout,
            "workflow": experiment,
            "log_type": LOGS_TYPE_OUTPUT
        })

        t_err = threading.Thread(target=log_buffer, kwargs={
            "buffer": stderr,
            "workflow": experiment,
            "log_type": LOGS_TYPE_ERROR
        })

        t_out.start()
        t_err.start()

        try:
            if exp_func:
                exit_status = exp_func(**arguments)
                result_log = exp_func.__name__ + " returned " + str(exit_status) + " as exit status."
                stdout.write(result_log)
                stdout.write('\0')
                stderr.write('\0')

        except Exception as e:
            exit_status = 1
            experiment.write_logs(str(e), LOGS_TYPE_ERROR)
        except KeyboardInterrupt:
            exit_status = -100
            experiment.write_logs("Keyboard Interrupt", LOGS_TYPE_ERROR)

        t_out.join()
        t_err.join()

        stdout.close()
        stderr.close()

        if command_proc:
            command_proc.wait()
            exit_status = command_proc.returncode

        # If user's function finished without failing and didn't return a status, we say it succeeded
        return exit_status or 0

    def delete(self, slugs, delete_artifacts=False):
        """
        Deleting multiple workflows
        @param delete_artifacts: will delete related artifacts from the storage
        @param slugs: List of workflow slugs to be deleted
        @return: None
        """
        delete_url = urljoin(self._route)

        attributes = {
            "workflow_slugs": slugs,
            "permanent": delete_artifacts
        }

        self._proxy.call_api(
            route=delete_url,
            http_method=HTTP.DELETE,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )
