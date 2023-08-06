import shlex
import os
import os.path
import stat
import subprocess
import json
import yaml
import requests
import platform
import shutil
import hashlib

import pluggy
from hash import resource_hookimpl as hookimpl

from hash import errors, utils, kern

from hash.kern.templates import Renderer

from .targets import Target, get_target

all_actions = ["build", "test", "publish", "deploy"]

hookspec = pluggy.HookspecMarker("hash-resource")


class ResourceSpec:
    @hookspec
    def init(self, file):
        pass

    @hookspec
    def action(self, name, state, env):
        pass

    @hookspec
    def re_action(self, action, state, env):
        pass

    @hookspec
    def depends_on_env(self):
        pass

    @hookspec
    def get_ignores(self):
        pass


class FileDownloadVerify(object):
    def __init__(self, url: str) -> None:
        utils.check_type(
            url, str, Exception, False, f"url must be string found {type(url)}"
        )
        self.__url = url
        self.__os_name = platform.system().lower()
        self.__cpu_arch = platform.processor().lower()

    def __verify_checksum(self, file: str, checksum: str):
        utils.check_type(
            checksum,
            str,
            Exception,
            False,
            f"checksum must be a string found {type(checksum)}",
        )
        utils.check_type(
            file, str, Exception, False, f"file must be a string found {type(file)}"
        )
        algo = hashlib.sha256()
        with open(file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                algo.update(byte_block)
            digest = algo.hexdigest()
            if digest != checksum:
                raise errors.ChecksumError(
                    f"calculated checksum {digest} for {file} does not match provided checksum {checksum}"
                )

    def download_file(self, version: str, checksum: str, path: str):
        utils.check_type(
            version,
            str,
            Exception,
            False,
            f"version must be a string found {type(version)}",
        )
        utils.check_type(
            checksum,
            str,
            Exception,
            False,
            f"checksum must be a string found {type(checksum)}",
        )
        utils.check_type(
            path, str, Exception, False, f"path must be a string found {type(path)}"
        )
        if os.path.isfile(path):
            try:
                self.__verify_checksum(path, checksum)
                return
            except errors.ChecksumError:
                pass
        response = requests.get(
            self.__url.format(
                version=version, os_name=self.__os_name, cpu_arch=self.__cpu_arch
            ),
            stream=True,
        )
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                f.write(chunk)
        self.__verify_checksum(path, checksum)

    def unpack_archive(self, file: str, output: str):
        utils.check_type(
            file,
            str,
            Exception,
            False,
            f"file must be a string found {type(file)}",
        )
        utils.check_type(
            output,
            str,
            Exception,
            False,
            f"output must be a string found {type(output)}",
        )
        shutil.unpack_archive(file, output)

    def make_exec(self, file):
        utils.check_type(
            file,
            str,
            Exception,
            False,
            f"file must be a string found {type(file)}",
        )
        st = os.stat(file)
        os.chmod(file, st.st_mode | stat.S_IEXEC)

    def prepare(self, version, checksum, path, output, is_archive: bool = False):
        utils.check_type(
            version,
            str,
            Exception,
            False,
            f"version must be a string found {type(version)}",
        )
        utils.check_type(
            checksum,
            str,
            Exception,
            False,
            f"checksum must be a string found {type(checksum)}",
        )
        utils.check_type(
            path, str, Exception, False, f"path must be a string found {type(path)}"
        )
        utils.check_type(
            output,
            str,
            Exception,
            False,
            f"output must be a string found {type(output)}",
        )
        self.download_file(version, checksum, path)
        if is_archive == True:
            self.unpack_archive(path, output)
        self.make_exec(output)


class Resource(object):
    def __init__(self, file) -> None:
        self.__path = file
        data = utils.parse_resource_file(file)
        self.__kind = data["kind"]
        self.__metadata = data["metadata"]
        self.__name = self.__metadata["name"]
        self.__spec = data.get("spec", {})
        self.__space = None

    def __str__(self) -> str:
        return f"{self.getKind()}:{self.getName()}"

    def setSpace(self, space):
        self.__space = space

    def getSpace(self):
        return self.__space

    def getPath(self):
        return os.path.join(os.path.dirname(self.__path), self.getSpec("path", "."))

    def getFile(self):
        return self.__path

    def getKind(self):
        return self.__kind

    def getName(self):
        return self.__name

    def getSpec(self, key, default=None):
        return self.__spec.get(key, default)

    def getMetadata(self, key, default=None):
        return self.__metadata.get(key, default)

    def getId(self):
        return f"{self.__kind}:{self.__name}"

    def forbidden_fields(self):  # skipcq: PYL-R0201
        """
        A list of forbidden fields that are not allowed
        to be mutated by Envs or Projects
        """
        return ["path"]

    def depends_on_env(self):
        return True

    def get_ignores(self):
        return []

    def raise_resource_error(self, name, e):
        if name == "build":
            raise errors.ResourceBuildError(e)
        elif name == "test":
            raise errors.ResourceTestError(e)
        elif name == "publish":
            raise errors.ResourcePublishError(e)
        elif name == "deploy":
            raise errors.ResourceDeployError(e)

    def create_artifact(
        self, id: str, action: str, env: str, hash: str, kind: str, data: str
    ):
        relative_path = ""
        if kind == "file":
            if data.startswith(self.getPath()):
                relative_path = data[len(self.getPath()) + 1 :]
            else:
                relative_path = data.split("/")[-1]
        return utils.Artifact(id, action, env, hash, kind, data, relative_path)

    def getSpecDict(self):
        """
        Return a dictionary that contains a key for every attribute with an imutable version of its value
        """
        ret = {}
        for k, v in self.__spec.items():
            if type(v) == list:
                item = tuple(v)
            elif type(v) == dict:
                item = utils.ImDict(v)
            else:
                item = v
            ret[k] = item
        return ret

    @classmethod
    def execute(
        cls, command: str, path: str, timeout=300
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            command,
            cwd=path,
            check=True,
            capture_output=True,
            shell=True,
            timeout=timeout,
        )

    def createArtifact(self, id, kind, data):
        relative_path = ""
        if kind == "file":
            if data.startswith(self.getPath()):
                relative_path = data[len(self.getPath()) + 1 :]
            else:
                relative_path = data.split("/")[-1]
        return utils.Artifact(id, "", "", "", kind, data, relative_path)

    def getParentId(self):
        parent_id = self.__metadata.get("parent")
        if parent_id is None:
            return
        utils.check_type(
            parent_id,
            str,
            errors.ResourceError,
            True,
            f"parent ID must be string: found {type(parent_id)}",
        )
        parent_parts = parent_id.split(":")
        if len(parent_parts) != 2 or parent_parts[1] == "" or parent_parts[0] == "":
            raise errors.ResourceError(f"Invalid parent ID: {parent_id}")
        return parent_id

    def mutate(self, mutate_spec: dict):
        """
        Mutate the specs of the resource based on mutation spec

        args:
            mutate_spec (dict): The specs used to mutate the resource
        """
        foribidden_fields = self.forbidden_fields() + ["path"]
        for field in foribidden_fields:
            if mutate_spec.get(field) != None:
                del mutate_spec[field]
        for k, v in self.__spec.items():
            if type(v) == list and mutate_spec.get(k) is not None:
                mutate_spec[k] = v + mutate_spec.get(k)
            elif type(v) == dict and mutate_spec.get(k) is not None:
                mutate_spec[k].update(v)
        self.__spec.update(mutate_spec)

    def __get_global(self, _globals, res_id, action, key, env):
        if env is None:
            env_name = "no_env"
        else:
            env_name = env
        if _globals.get(res_id) is None:
            raise errors.ResourceSpecError(f"No globals for resource with id {res_id}")
        if _globals[res_id].get(env_name) is None:
            raise errors.ResourceSpecError(
                f"No globals for resource with id {res_id} in env {env_name}"
            )
        if _globals[res_id][env_name].get(action) is None:
            raise errors.ResourceSpecError(
                f"No globals for resource with id {res_id} in env {env_name} for action {action}"
            )
        if _globals[res_id][env_name][action].get(key) is None:
            raise errors.ResourceSpecError(
                f"No globals for resource with id {res_id} in env {env_name}, action {action} called {key}"
            )
        return _globals[res_id][env_name][action][key]

    def __fill_specs(self, env: str, _globals: dict, rs, spec: dict):
        keys = {}
        delete_keys = {}
        for i, v in spec.items():
            if type(v) == str and v.startswith("secrets."):
                env_res = rs.find_resource_by_id(f"Env:{env}")
                if env_res is None:
                    raise errors.ResourceError(f"No env with name {env}")
                secrets_provider = env_res.getSecretProvider()
                parts = v.split(".")
                if len(parts) >= 2:
                    parts = parts[1:]
                    res_id = parts[0]
                    action = parts[1]
                    res = rs.find_resource_by_id(res_id)
                    if res is None:
                        raise errors.ResourceSpecError(
                            f"No resource with id : {res_id}"
                        )
                    if res.getMetadata("env"):
                        secret_key = f"{res_id}.{res.getMetadata('env')}.{action}"
                    else:
                        secret_key = f"{res_id}.{env}.{action}"
                try:
                    result = self.getSpace().get_secret_from_store(secret_key)
                except errors.SecretsProviderError as e:
                    raise errors.ResourceSpecError(
                        f"No secret with key {secret_key} : {e}"
                    )
                for p in parts[2:]:
                    if type(result) != dict and type(result) != utils.ImDict:
                        raise errors.ResourceSpecError(
                            f"No secret found with key {secret_key} and selectors {parts[2:]}"
                        )
                    result = result.get(p)
                    if result is None:
                        raise errors.ResourceSpecError(
                            f"No secret found with key {secret_key} and selectors {parts[2:]}"
                        )
                spec[i] = result
            elif type(v) == str and v.startswith("$"):
                parts = v.split(".")
                if len(parts) > 2:
                    res_id = parts[0][1:]
                    action = parts[1]
                    res = rs.find_resource_by_id(res_id)
                    if res is None:
                        raise errors.ResourceSpecError(
                            f"No resource with id : {res_id}"
                        )
                    if res.getMetadata("env"):
                        result = self.__get_global(
                            _globals, res_id, action, parts[2], res.getMetadata("env")
                        )
                    else:
                        result = self.__get_global(
                            _globals, res_id, action, parts[2], env
                        )
                    for p in parts[3:]:
                        try:
                            result = result[p]
                        except KeyError:
                            raise errors.ResourceSpecError(
                                f"Resource with id {res_id}, does not have an output called {p} from action {action} and env {env}"
                            )
                    spec[i] = result
            elif type(i) == str and i.startswith("secrets."):
                env_res = rs.find_resource_by_id(f"Env:{env}")
                if env_res is None:
                    raise errors.ResourceError(f"No env with name {env}")
                secrets_provider = env_res.getSecretProvider()
                parts = v.split(".")
                if len(parts) >= 2:
                    parts = parts[1:]
                    res_id = parts[0]
                    action = parts[1]
                    res = rs.find_resource_by_id(res_id)
                    if res is None:
                        raise errors.ResourceSpecError(
                            f"No resource with id : {res_id}"
                        )
                    if res.getMetadata("env"):
                        secret_key = f"{res_id}.{res.getMetadata('env')}.{action}"
                    else:
                        secret_key = f"{res_id}.{env}.{action}"
                try:
                    result = self.getSpace().get_secret_from_store(secret_key)
                except errors.SecretsProviderError as e:
                    raise errors.ResourceSpecError(f"No secret with key {secret_key}")
                for p in parts[2:]:
                    if type(result) != dict and type(result) != utils.ImDict:
                        raise errors.ResourceSpecError(
                            f"No secret found with key {secret_key} and selectors {parts[2:]}"
                        )
                    result = result.get(p)
                    if result is None:
                        raise errors.ResourceSpecError(
                            f"No secret found with key {secret_key} and selectors {parts[2:]}"
                        )
                keys[result] = v
                delete_keys[i] = 1
            elif type(i) == str and i.startswith("$"):
                parts = i.split(".")
                if len(parts) > 2:
                    res_id = parts[0][1:]
                    action = parts[1]
                    res = rs.find_resource_by_id(res_id)
                    if res is None:
                        raise errors.ResourceSpecError(f"No resource with id {res_id}")
                    if res.getMetadata("env"):
                        result = self.__get_global(
                            _globals, res_id, action, parts[2], res.getMetadata("env")
                        )
                        delete_keys[i] = 1
                    else:
                        result = self.__get_global(
                            _globals, res_id, action, parts[2], env
                        )
                        delete_keys[i] = 1
                    for p in parts[3:]:
                        try:
                            result = result[p]
                        except KeyError:
                            raise errors.ResourceSpecError(
                                f"Resource with id {res_id}, does not have an output called {p} from action {action} and env {env}"
                            )
                    keys[result] = v
                    delete_keys[i] = 1
            elif type(v) == dict:
                self.__fill_specs(env, _globals, rs, v)
            elif type(v) == list:
                for item in v:
                    if type(item) == dict:
                        self.__fill_specs(env, _globals, rs, item)
        if keys != {}:
            for i, v in keys.items():
                spec[i] = v
        if delete_keys != {}:
            for i, v in delete_keys.items():
                del spec[i]

    def fill_specs(self, env: str, _globals: dict, rs):
        """
        Fill the resources specs with data according to the env and globals, every spec
        key/value that starts with $ is filled according to current env and globals

        args:
            env (str): The env from which we must fill the specs
            _globals (dict): A dictionary for global values to use when sub-situting
                keys/values that start with $
            rs (ResourceSpace): The space in which to search for resources
        """
        self.__fill_specs(env, _globals, rs, self.__spec)

    def get_deps(self):
        """
        Return a list of explicit deps for this resource
        """
        deps = self.getMetadata("depends_on", [])
        utils.check_type(
            deps,
            list,
            errors.ResourceConfigError,
            False,
            f"depends_on should be a list: found {type(deps)}",
        )
        ret_deps = []
        ids = []
        for dep in deps:
            utils.check_type(
                dep,
                dict,
                errors.ResourceConfigError,
                False,
                f"Every dep should be a dictionary: found",
            )
            dep_id = dep.get("id")
            if dep_id in ids:
                continue
            ids.append(dep_id)
            utils.check_type(
                dep_id,
                str,
                errors.ResourceConfigError,
                False,
                f"Every dep needs to have an ID of type string: found {type(dep_id)}",
            )
            ret_deps.append(dep)
        return ret_deps

    def process_value(self, v, deps):
        if type(v) == str and v.startswith("$"):
            parts = v.split(".")
            if len(parts) > 2:
                res_id = parts[0][1:]
                action = parts[1]
                deps.append({"id": res_id, "action2": action})
        elif type(v) == str and v.startswith("secrets."):
            parts = v.split(".")
            parts = parts[1:]
            if len(parts) > 2:
                res_id = parts[0]
                action = parts[1]
                deps.append({"id": res_id, "action2": action})
        elif type(v) == dict:
            deps.extend(self.get_deps_spec(v))
        elif type(v) == list:
            for item in v:
                if type(item) == str and item.startswith("$"):
                    parts = item.split(".")
                    if len(parts) > 2:
                        res_id = parts[0][1:]
                        action = parts[1]
                        deps.append({"id": res_id, "action2": action})
                elif type(item) == str and item.startswith("secrets."):
                    parts = item.split(".")
                    parts = parts[1:]
                    if len(parts) > 2:
                        res_id = parts[0]
                        action = parts[1]
                        deps.append({"id": res_id, "action2": action})
                elif type(item) == dict:
                    deps.extend(self.get_deps_spec(item))

    def get_deps_spec(self, spec=None):
        if spec is None:
            spec = self.__spec
        deps = []
        for k, v in spec.items():
            self.process_value(k, deps)
            self.process_value(v, deps)
        return deps


class FakeResource(Resource):
    @hookimpl
    def init(self, file):
        pass

    @hookimpl
    def depends_on_env(self):
        return self.getSpec("depends_on_env", True)

    @hookimpl
    def action(self, name, state, env):
        if name not in all_actions:
            raise errors.ResourceError(
                f"Fake resource only supports these actions {all_actions}"
            )
        ret = {
            f"{name}_result": self.getSpec(f"{name}_result"),
            "globals": self.getSpec("globals"),
        }
        # process artifacts
        artifacts = self.getSpec("artifacts", [])
        afts = []
        env_name = None
        if env is not None:
            env_name = env.getName()
        for aft in artifacts:
            if aft.get("kind") == "file":
                content = aft.get("content")
                if content is not None:
                    with open(os.path.join(self.getPath(), aft.get("path")), "w") as f:
                        f.write(content)
                af = self.create_artifact(
                    aft.get("id", "id"),
                    name,
                    env_name,
                    state.get("hash"),
                    "file",
                    os.path.join(self.getPath(), aft.get("path")),
                )
                afts.append(af)
            else:
                af = self.create_artifact(
                    aft.get("id", "id"),
                    name,
                    env_name,
                    state.get("hash"),
                    aft.get("kind"),
                    aft.get("data"),
                )
                afts.append(af)
        ret["artifacts"] = afts
        if self.getSpec("ret"):
            return self.getSpec("ret")
        if self.getSpec("local") is not None:
            ret["local"] = self.getSpec("local")
        return ret

    def forbidden_fields(self):
        return ["dont"]

    @hookimpl
    def re_action(self, action, state, env):
        return self.getSpec(f"re_{action}", False)


class EnvResource(Resource):
    def action(self, name, state, env):
        pass

    def getTarget(self, kind: str):
        targets = self.getSpec("targets", [])
        for target in targets:
            if target["kind"] == kind:
                return get_target(kind, target, self.getSpace())
        parent_id = self.getParentId()
        if parent_id:
            parent = self.getSpace().find_resource_by_id(parent_id)
            if parent is None:
                raise errors.ResourceSpecError(
                    f"No resource with id {parent_id} in metadata of {self.getId()}"
                )
            targets = parent.getSpec("targets", [])
            for target in targets:
                if target["kind"] == kind:
                    return get_target(kind, target, self.getSpace())

    def getSecretProvider(self, name=None):
        secret_providers = self.getSpec("secrets", [])
        for secret_provider in secret_providers:
            if name is None:
                return kern.get_secrets(
                    secret_provider.get("kind"), secret_provider.get("spec", {})
                )
            if name == secret_provider.get("name"):
                return kern.get_secrets(
                    secret_provider.get("kind"), secret_provider.get("spec", {})
                )
        parent_id = self.getParentId()
        if parent_id:
            parent = self.getSpace().find_resource_by_id(parent_id)
            if parent is None:
                raise errors.ResourceSpecError(
                    f"No resource with id {parent_id} in metadata of {self.getId()}"
                )
            secret_providers = parent.getSpec("secrets", [])
            for secret_provider in secret_providers:
                if name is None:
                    return kern.get_secrets(
                        secret_provider.get("kind"), secret_provider.get("spec", {})
                    )
                if name == secret_provider.get("name"):
                    return kern.get_secrets(
                        secret_provider.get("kind"), secret_provider.get("spec", {})
                    )

    def __str__(self) -> str:
        return self.getName()


class ProjectResource(Resource):
    def action(self, name, state, env):
        pass

    def __str__(self) -> str:
        return self.getName()


class TerraformResource(Resource):
    def select_workspace(self, workspace):
        workspace_new_command = f"{self.__terraform} workspace new {workspace}"
        try:
            self.execute(workspace_new_command, self.getPath())
        except Exception:
            pass
        workspace_select_command = f"{self.__terraform} workspace select {workspace}"
        self.execute(workspace_select_command, self.getPath())

    def terraform_init(self, workspace):
        init_command = (
            f"{self.__terraform} init -no-color -upgrade -input=false -force-copy"
        )
        state_backend = self.getSpec("state_backend")
        if state_backend:
            kind = state_backend.get("kind", "gcs")
            if kind == "gcs":
                bucket_name = state_backend.get("bucket_name")
                if bucket_name is None:
                    raise errors.ResourceConfigError(
                        "GCS backend requires bucket_name option"
                    )
                prefix = state_backend.get("prefix")
                if prefix:
                    init_command += f" -backend-config='bucket={bucket_name}' -backend-config='prefix={prefix}'"
                else:
                    init_command += f" -backend-config='bucket={bucket_name}'"
                project = state_backend.get("project")
                if project:
                    p = self.execute(f"gsutil ls -p {project}", self.getPath())
                else:
                    p = self.execute(f"gsutil ls", self.getPath())
                if bucket_name not in p.stdout.decode("UTF-8"):
                    location = state_backend.get("location", "EU")
                    if project:
                        gcs_command = (
                            f"gsutil mb -l {location} -p {project} gs://{bucket_name}"
                        )
                    else:
                        gcs_command = f"gsutil mb -l {location} gs://{bucket_name}"
                    self.execute(gcs_command, self.getPath())
            else:
                raise errors.ResourceConfigError(f"Unknown state backend kind: {kind}")

        self.execute(init_command, self.getPath())
        self.select_workspace(workspace)

    @hookimpl
    def depends_on_env(self):
        return False

    def re_action(self, action, state, env):
        if action == "publish":
            return False
        self.check_terraform()
        if env is None or env == {}:
            self.raise_resource_error(
                "deploy", "Terraform resource requires an env with workspace argument"
            )
        if self.__get_version() != state.get("envs", {}).get(env.getName(), {}).get(
            action, {}
        ).get("version"):
            return True
        if action in ["build", "test", "publish"]:
            return False
        workspace = env.getSpec("workspace", env.getName())
        try:
            self.terraform_init(workspace)
        except subprocess.CalledProcessError as e:
            raise errors.ResourceDeployError(
                f"Cannot initialize terraform, {e.stderr.decode('UTF-8')}"
            )
        except subprocess.TimeoutExpired as e:
            raise errors.ResourceDeployError(
                f"Timeout initializing terraform, {e.stderr.decode('UTF-8')}"
            )
        build_command = (
            f"{self.__terraform} plan -detailed-exitcode -no-color -input=false"
        )
        variables = self.getSpec("variables")
        if variables:
            vars = ""
            for var_name, var_value in variables.items():
                if type(var_value) == list:
                    value = str(var_value).replace("'", '"')
                    vars += f" -var '{var_name}={value}'"
                else:
                    vars += f" -var {var_name}={var_value}"
            build_command += vars
        try:
            self.execute(
                build_command, self.getPath(), self.getSpec("plan_timeout", 300)
            )
        except FileNotFoundError as e:
            raise errors.ResourceBuildError("cannot find terraform in PATH")
        except subprocess.CalledProcessError as e:
            if e.returncode == 2:
                return True
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))
        return False

    @hookimpl
    def init(self, file: str):
        """
        Initialize the terraform resource.

        Args:
            content (dict): The dictionary that represents the YAML file resource, it must
            have a key called kind with the value of Terraform, a key called metadata with
            a dictionary value which at least has a name key, a key called spec with a
            dictionary value which at least hash a path key that must exist.
        """
        super().__init__(file)
        if self.getKind() != "Terraform":
            raise errors.ResourceConfigError("This is not a terraform resource")
        self.name = self.getMetadata("name")

    def get_outputs(self, path) -> dict:
        try:
            refresh_command = f"{self.__terraform} refresh"
            variables = self.getSpec("variables")
            if variables:
                vars = ""
                for var_name, var_value in variables.items():
                    if type(var_value) == list:
                        value = str(var_value).replace("'", '"')
                        vars += f" -var '{var_name}={value}'"
                    else:
                        vars += f" -var {var_name}={var_value}"
                refresh_command += vars
            self.execute(refresh_command, path)
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))
        try:
            proc = self.execute(f"{self.__terraform} output -json", path)
            outputs = json.loads(proc.stdout)
            normal_outputs = {}
            sensitive_outputs = {}
            for index, value in outputs.items():
                if value.get("sensitive"):
                    sensitive_outputs[index] = value
                else:
                    normal_outputs[index] = value
            return normal_outputs, sensitive_outputs
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))

    def __install_terraform(self, version):
        download_link = f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_linux_amd64.zip"
        terraform_check_sums = {
            "1.4.5": "ce10e941cd11554b15a189cd00191c05abc20dff865599d361bdb863c5f406a9",
            "1.4.4": "67541c1f6631befcc25b764028e5605e59234d4424e60a256518ee1e8dd50593",
            "1.4.3": "2252ee6ac8437b93db2b2ba341edc87951e2916afaeb50a88b858e80796e9111",
            "1.4.2": "9f3ca33d04f5335472829d1df7785115b60176d610ae6f1583343b0a2221a931",
            "1.4.1": "9e9f3e6752168dea8ecb3643ea9c18c65d5a52acc06c22453ebc4e3fc2d34421",
            "1.4.0": "5da60da508d6d1941ffa8b9216147456a16bbff6db7622ae9ad01d314cbdd188",
            "1.3.9": "53048fa573effdd8f2a59b726234c6f450491fe0ded6931e9f4c6e3df6eece56",
            "1.3.8": "9d9e7d6a9b41cef8b837af688441d4fbbd84b503d24061d078ad662441c70240",
            "1.3.7": "b8cf184dee15dfa89713fe56085313ab23db22e17284a9a27c0999c67ce3021e",
            "1.3.6": "bb44a4c2b0a832d49253b9034d8ccbd34f9feeb26eda71c665f6e7fa0861f49b",
            "1.3.5": "ac28037216c3bc41de2c22724e863d883320a770056969b8d211ca8af3d477cf",
            "1.3.4": "b24210f28191fa2a08efe69f54e3db2e87a63369ac4f5dcaf9f34dc9318eb1a8",
            "1.3.3": "fa5cbf4274c67f2937cabf1a6544529d35d0b8b729ce814b40d0611fd26193c1",
            "1.3.2": "6372e02a7f04bef9dac4a7a12f4580a0ad96a37b5997e80738e070be330cb11c",
            "1.3.1": "0847b14917536600ba743a759401c45196bf89937b51dd863152137f32791899",
            "1.3.0": "380ca822883176af928c80e5771d1c0ac9d69b13c6d746e6202482aedde7d457",
        }
        terraform_check_sum = self.getSpec("terraform_check_sum")
        if terraform_check_sum is None:
            terraform_check_sum = terraform_check_sums.get(version)
            if terraform_check_sum is None:
                raise errors.ResourceError(
                    f"Not stored checksum for version {version} and no checksum provided in spec `terraform_check_sum`"
                )
        try:
            download_command = f"wget -c {download_link}"
            hash_dir = self.getSpace().get_hash_dir()
            self.execute(download_command, hash_dir)
            sha256_sum = (
                self.execute(f"sha256sum terraform_{version}_linux_amd64.zip", hash_dir)
                .stdout.decode("UTF-8")
                .split(" ")[0]
            )
            if sha256_sum != terraform_check_sum:
                raise errors.ResourceError(
                    f"downloaded file checksum is {sha256_sum}, does not match {terraform_check_sum}"
                )
            self.execute(f"unzip -u terraform_{version}_linux_amd64.zip", hash_dir)
            self.execute(f"mv terraform terraform_{version}_linux_amd64", hash_dir)
            self.__terraform = os.path.join(
                hash_dir, f"terraform_{version}_linux_amd64"
            )
        except Exception as e:
            raise errors.ResourceError(
                f"Cannot download terraform binary, error is: {e}"
            )

    def check_terraform(self):
        version = self.getSpec("terraform_version")
        if version is None:
            self.__terraform = "terraform"
            return
        if type(version) != str:
            raise errors.ResourceError(
                f"terraform_version must be string, found: {type(version)}"
            )
        self.__terraform = "terraform"
        if version:
            try:
                current_version_output = self.execute(
                    "terraform version", self.getPath()
                )
                current_version = (
                    current_version_output.stdout.decode("UTF-8")
                    .split(" ")[1][1:]
                    .split("o")[0]
                    .strip()
                )
                if current_version == version:
                    return
            except FileNotFoundError as e:
                pass
            terraform_install = self.getSpec("terraform_install")
            if terraform_install is True:
                self.__install_terraform(version)
            else:
                raise errors.ResourceError(
                    "Terraform version is wrong or not installed and `terraform_install` is not set to true"
                )

    def __get_version(self):
        try:
            current_version_output = self.execute(
                f"{self.__terraform} version", self.getPath()
            )
            current_version = (
                current_version_output.stdout.decode("UTF-8")
                .split(" ")[1][1:]
                .split("o")[0]
                .strip()
            )
            return current_version
        except FileNotFoundError as e:
            raise errors.ResourceError(
                f"No terraform binary found at {self.__terraform}"
            )

    @hookimpl
    def action(self, name, state, env):
        self.check_terraform()
        if name == "build":
            return self.build(state, env)
        elif name == "test":
            return self.test(state, env)
        elif name == "deploy":
            return self.deploy(state, env)

    def build(self, state: dict, env: EnvResource):
        """
        Build the terraform resource based on its resource file

        Args:
            base_path (str): This path is joined with the path in the spec
            to get the full path to the terraform files directory.
        """
        if env is None or env == {}:
            self.raise_resource_error(
                "build", "Terraform resource requires an env with workspace argument"
            )
        workspace = env.getSpec("workspace", env.getName())
        try:
            self.terraform_init(workspace)
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(
                f"Cannot initialize terraform, {e.stderr.decode('UTF-8')}"
            )
        except subprocess.TimeoutExpired as e:
            raise errors.ResourceBuildError(
                f"Timeout initializing terraform, {e.stderr.decode('UTF-8')}"
            )
        build_command = f"{self.__terraform} plan -out=tfplan -no-color -input=false"
        variables = self.getSpec("variables")
        if variables:
            vars = ""
            for var_name, var_value in variables.items():
                if type(var_value) == list:
                    value = str(var_value).replace("'", '"')
                    vars += f" -var '{var_name}={value}'"
                else:
                    vars += f" -var {var_name}={var_value}"
            build_command += vars
        try:
            self.execute(
                build_command, self.getPath(), self.getSpec("plan_timeout", 300)
            )
        except FileNotFoundError as e:
            raise errors.ResourceBuildError("cannot find terraform in PATH")
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))
        artifacts = [
            self.create_artifact(
                "tfplan",
                "build",
                env.getName(),
                state.get("hash", ""),
                "file",
                os.path.join(self.getPath(), "tfplan"),
            )
        ]
        normal_outputs, sensitive_outputs = self.get_outputs(self.getPath())
        return {
            "status": "plan generated",
            "artifacts": artifacts,
            "globals": normal_outputs,
            "secrets": sensitive_outputs,
            "version": self.__get_version(),
        }

    def test(self, state: dict, env: EnvResource):
        fmt_check_command = f"{self.__terraform} fmt --check"
        try:
            self.execute(fmt_check_command, self.getPath())
        except subprocess.CalledProcessError as e:
            raise errors.ResourceTestError(
                f"Terraform is not formatted probably: please run command `terraform fmt`, {e.stderr.decode('UTF-8')}"
            )
        except subprocess.TimeoutExpired as e:
            raise errors.ResourceTestError(
                f"Timeout checking terraform format, {e.stderr.decode('UTF-8')}"
            )
        ifracost_spec = self.getSpec("infracost", {})
        ret_data = {
            "error": False,
            "message": "terraform is fomratted probably",
            "version": self.__get_version(),
        }
        if ifracost_spec.get("enabled"):
            maximum = ifracost_spec.get("maximum", 0)
            api_key = ifracost_spec.get("api_key")
            if type(api_key) != str:
                raise errors.ResourceTestError(
                    f"infracost API key should be a string value found {api_key}"
                )
            os.environ["INFRACOST_API_KEY"] = api_key
            try:
                p = self.execute(
                    "infracost breakdown --path . --format json", self.getPath()
                )
                actual_cost = float(
                    json.loads(p.stdout.decode("UTF-8")).get("totalMonthlyCost", 0)
                )
                if actual_cost > maximum:
                    raise errors.ResourceTestError(
                        f"Actual cost {actual_cost} is higher than maximum cost {maximum}"
                    )
                ret_data["infra_cost"] = {"actual_cost": actual_cost}
            except subprocess.CalledProcessError as e:
                raise errors.ResourceTestError(
                    f"Error checking for costs : {e.stderr.decode('UTF-8')}"
                )

        return ret_data

    def deploy(self, state: dict, env: EnvResource):
        """
        Build the terraform resource based on its resource file

        Args:
            base_path (str): This path is joined with the path in the spec
            to get the full path to the terraform files directory.
        """
        if env is None or env == {}:
            self.raise_resource_error(
                "deploy", "Terraform resource requires an env with workspace argument"
            )
        workspace = env.getSpec("workspace", env.getName())
        try:
            self.terraform_init(workspace)
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(
                f"Cannot initialize terraform, {e.stderr.decode('UTF-8')}"
            )
        except subprocess.TimeoutExpired as e:
            raise errors.ResourceBuildError(
                f"Timeout initializing terraform, {e.stderr.decode('UTF-8')}"
            )
        deploy_command = (
            f"{self.__terraform} apply -input=false -auto-approve -no-color"
        )
        variables = self.getSpec("variables")
        if variables:
            vars = ""
            for var_name, var_value in variables.items():
                if type(var_value) == list:
                    value = str(var_value).replace("'", '"')
                    vars += f" -var '{var_name}={value}'"
                else:
                    vars += f" -var {var_name}={var_value}"
            deploy_command += vars
        try:
            self.execute(
                deploy_command, self.getPath(), self.getSpec("apply_timeout", 300)
            )
            normal_outputs, sensitive_outputs = self.get_outputs(self.getPath())
            return {
                "status": "plan applied",
                "globals": normal_outputs,
                "secrets": sensitive_outputs,
                "version": self.__get_version(),
            }
        except FileNotFoundError as e:
            raise errors.ResourceBuildError("cannot find terraform in PATH")
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))


# Kustomize resource


class KustomizeResource(Resource):
    @hookimpl
    def init(self, file: str):
        """
        Initialize the kustomize resource.

        Args:
            content (dict): The dictionary that represents the YAML file resource, it must
            have a key called kind with the value of Kustomize, a key called metadata with
            a dictionary value which at least has a name key, a key called spec with a
            dictionary value which at least hash a path key that must exist.
        """
        super().__init__(file)
        if self.getKind() != "Kustomize":
            raise errors.ResourceConfigError("This is not a kustomize resource")
        self.name = self.getMetadata("name")

    def __install_kubectl(self, version):
        download_link = f"https://dl.k8s.io/release/v{version}/bin/linux/amd64/kubectl"
        kubectl_check_sums = {
            "1.22.0": "703e70d49b82271535bc66bc7bd469a58c11d47f188889bd37101c9772f14fa1",
            "1.22.1": "78178a8337fc6c76780f60541fca7199f0f1a2e9c41806bded280a4a5ef665c9",
            "1.22.2": "aeca0018958c1cae0bf2f36f566315e52f87bdab38b440df349cd091e9f13f36",
            "1.22.3": "0751808ca8d7daba56bf76b08848ef5df6b887e9d7e8a9030dd3711080e37b54",
            "1.22.4": "21f24aa723002353eba1cc2668d0be22651f9063f444fd01626dce2b6e1c568c",
            "1.22.5": "fcb54488199c5340ff1bc0e8641d0adacb27bb18d87d0899a45ddbcc45468611",
            "1.22.6": "1ab07643807a45e2917072f7ba5f11140b40f19675981b199b810552d6af5c53",
            "1.22.7": "4dd14c5b61f112b73a5c9c844011a7887c4ffd6b91167ca76b67197dee54d388",
            "1.22.8": "761bf1f648056eeef753f84c8365afe4305795c5f605cd9be6a715483fe7ca6b",
            "1.22.9": "ae6a9b585f9a366d24bb71f508bfb9e2bb90822136138109d3a91cd28e6563bb",
            "1.22.10": "225bc8d4ac86e3a9e36b85d2d9cb90cd4b4afade29ba0292f47834ecf570abf2",
            "1.22.11": "a61c697e3c9871da7b609511248e41d9c9fb6d9e50001425876676924761586b",
            "1.22.12": "8e36c8fa431e454e3368c6174ce3111b7f49c28feebdae6801ab3ca45f02d352",
            "1.22.13": "b96d2bc9137ec63546a29513c40c5d4f74e9f89aa11edc15e3c2f674d5fa3e02",
            "1.22.14": "a4408b32b9729e38c14b38a64ea6f00d67d2127f9c1314fbc2273a37a987a2d2",
            "1.22.15": "239a48f1e465ecfd99dd5e3d219066ffea7bbd4cdedb98524e82ff11fd72ba12",
            "1.22.16": "12da5128e2377f9c9eb97b854c95445e00839437de0543968bd3a54b5ae596d8",
            "1.22.17": "7506a0ae7a59b35089853e1da2b0b9ac0258c5309ea3d165c3412904a9051d48",
            "1.23.0": "2d0f5ba6faa787878b642c151ccb2c3390ce4c1e6c8e2b59568b3869ba407c4f",
            "1.23.1": "156fd5e7ebbedf3c482fd274089ad75a448b04cf42bc53f370e4e4ea628f705e",
            "1.23.2": "5b55b58205acbafa7f4e3fc69d9ce5a9257be63455db318e24db4ab5d651cbde",
            "1.23.3": "d7da739e4977657a3b3c84962df49493e36b09cc66381a5e36029206dd1e01d0",
            "1.23.4": "3f0398d4c8a5ff633e09abd0764ed3b9091fafbe3044970108794b02731c72d6",
            "1.23.5": "715da05c56aa4f8df09cb1f9d96a2aa2c33a1232f6fd195e3ffce6e98a50a879",
            "1.23.6": "703a06354bab9f45c80102abff89f1a62cbc2c6d80678fd3973a014acc7c500a",
            "1.23.7": "b4c27ad52812ebf3164db927af1a01e503be3fb9dc5ffa058c9281d67c76f66e",
            "1.23.8": "299803a347e2e50def7740c477f0dedc69fc9e18b26b2f10e9ff84a411edb894",
            "1.23.9": "053561f7c68c5a037a69c52234e3cf1f91798854527692acd67091d594b616ce",
            "1.23.10": "3ffa658e7f1595f622577b160bdcdc7a5a90d09d234757ffbe53dd50c0cb88f7",
            "1.23.11": "cf04ad2fa1cf118a951d690af0afbbe8f5fc4f02c721c848080d466e6159111e",
            "1.23.12": "b150c7c4830cc3be4bedd8998bf36a92975c95cd1967b4ef2d1edda080ffe5d9",
            "1.23.13": "fae6957e6a7047ad49cdd20976cd2ce9188b502c831fbf61f36618ea1188ba38",
            "1.23.14": "13ce4b18ba6e15d5d259249c530637dd7fb9722d121df022099f3ed5f2bd74cd",
            "1.23.15": "adab29cf67e04e48f566ce185e3904b5deb389ae1e4d57548fcf8947a49a26f5",
            "1.23.16": "5f914edc9dbfbe1b8b8dc0f5dbbac28720a8dffeb940e3339c371e3612c37e48",
            "1.23.17": "f09f7338b5a677f17a9443796c648d2b80feaec9d6a094ab79a77c8a01fde941",
            "1.24.0": "94d686bb6772f6fb59e3a32beff908ab406b79acdfb2427abdc4ac3ce1bb98d7",
            "1.24.1": "0ec3c2dbafc6dd27fc8ad25fa27fc527b5d7356d1830c0efbb8adcf975d9e84a",
            "1.24.2": "f15fb430afd79f79ef7cf94a4e402cd212f02d8ec5a5e6a7ba9c3d5a2f954542",
            "1.24.3": "8a45348bdaf81d46caf1706c8bf95b3f431150554f47d444ffde89e8cdd712c1",
            "1.24.4": "4a76c70217581ba327f0ad0a0a597c1a02c62222bb80fbfea4f2f5cb63f3e2d8",
            "1.24.5": "3037f2ec62956e7146fc86defb052d8d3b28e2daa199d7e3ff06d1e06a6286ed",
            "1.24.6": "3ba7e61aecb19eadfa5de1c648af1bc66f5980526645d9dfe682d77fc313b74c",
            "1.24.7": "2d88e56d668b1d7575b4783f22d512e94da432f42467c3aeac8a300b6345f12d",
            "1.24.8": "f93c18751ec715b4d4437e7ece18fe91948c71be1f24ab02a2dde150f5449855",
            "1.24.9": "7e13f33b7379b6c25c3ae055e4389eb3eef168e563f37b5c5f1be672e46b686e",
            "1.24.10": "d8e9cd9bb073ff09e2f2a74cf48e94a9b9d4f2fa2e2dd91b68b01f64e7061a3b",
            "1.24.11": "c8bdf1b12d5ac91d163c07e61b9527ef718bec6a00f4fd4cf071591218f59be5",
            "1.24.12": "25875551d4242339bcc8cef0c18f0a0f631ea621f6fab1190a5aaab466634e7c",
            "1.24.13": "52455fe485fa11c650ab07fea2e4856b5ea5a3e6ef8a1b3b6121e6361437fff9",
            "1.25.0": "e23cc7092218c95c22d8ee36fb9499194a36ac5b5349ca476886b7edc0203885",
            "1.25.1": "9cc2d6ce59740b6acf6d5d4a04d4a7d839b0a81373248ef0ce6c8d707143435b",
            "1.25.2": "8639f2b9c33d38910d706171ce3d25be9b19fc139d0e3d4627f38ce84f9040eb",
            "1.25.3": "f57e568495c377407485d3eadc27cda25310694ef4ffc480eeea81dea2b60624",
            "1.25.4": "e4e569249798a09f37e31b8b33571970fcfbdecdd99b1b81108adc93ca74b522",
            "1.25.5": "6a660cd44db3d4bfe1563f6689cbe2ffb28ee4baf3532e04fff2d7b909081c29",
            "1.25.6": "ba876aef0e9d7e2e8fedac036ec194de5ec9b6d2953e30ff82a2758c6ba32174",
            "1.25.7": "6cdbaf3fdd1032fc8e560ccc0a75b5bd6fa5b6cb45491e9677872f511131ad3d",
            "1.25.8": "80e70448455f3d19c3cb49bd6ff6fc913677f4f240d368fa2b9f0d400c8cd16e",
            "1.25.9": "aaa5ea3b3630730d2b8a8ef3cccb14b47754602c7207c7b0717158ae83c7cb10",
        }
        kubectl_check_sum = self.getSpec("kubectl_check_sum")
        if kubectl_check_sum is None:
            kubectl_check_sum = kubectl_check_sums.get(version)
            if kubectl_check_sum is None:
                raise errors.ResourceError(
                    f"Not stored checksum for version {version} and no checksum provided in spec `kubectl_check_sum`"
                )
        try:
            download_command = f"wget -c {download_link}"
            hash_dir = self.getSpace().get_hash_dir()
            self.execute(download_command, hash_dir)
            sha256_sum = (
                self.execute(f"sha256sum kubectl", hash_dir)
                .stdout.decode("UTF-8")
                .split(" ")[0]
            )
            if sha256_sum != kubectl_check_sum:
                raise errors.ResourceError(
                    f"downloaded file checksum is {sha256_sum}, does not match {kubectl_check_sum}"
                )
            self.execute(f"mv kubectl kubectl_{version}_linux_amd64", hash_dir)
            self.execute(f"chmod +x kubectl_{version}_linux_amd64", hash_dir)
            self.__kubectl = os.path.join(hash_dir, f"kubectl_{version}_linux_amd64")
        except Exception as e:
            raise errors.ResourceError(f"Cannot download kubectl binary, error is: {e}")

    def check_kubectl(self):
        version = self.getSpec("kubectl_version")
        if version is None:
            self.__kubectl = "kubectl"
            return
        if type(version) != str:
            raise errors.ResourceError(
                f"kubectl_version must be string, found: {type(version)}"
            )
        self.__kubectl = "kubectl"
        if version:
            try:
                current_version_output = self.execute(
                    "kubectl version --short --client", self.getPath()
                )
                current_version = (
                    current_version_output.stdout.decode("UTF-8")
                    .split("Client Version:")[1]
                    .split("\n")[0]
                    .strip()
                    .split("v")[1]
                )
                if current_version == version:
                    return
            except FileNotFoundError as e:
                pass
            kubectl_install = self.getSpec("kubectl_install")
            if kubectl_install is True:
                self.__install_kubectl(version)
            else:
                raise errors.ResourceError(
                    "kubectl version is wrong or not installed and `kubectl_install` is not set to true"
                )

    def __get_version(self):
        try:
            current_version_output = self.execute(
                f"{self.__kubectl} version --short --client", self.getPath()
            )
            current_version = (
                current_version_output.stdout.decode("UTF-8")
                .split("Client Version:")[1]
                .split("\n")[0]
                .strip()
                .split("v")[1]
            )
            return current_version
        except FileNotFoundError as e:
            raise errors.ResourceError(f"No kubectl binary found at {self.__kubectl}")

    @classmethod
    def generate(
        cls, path, file, env: EnvResource, overlay=None, missing_overlay="use_base"
    ):
        if overlay is None:
            path_overlay = os.path.join(path, "overlays", env.getName())
        else:
            path_overlay = os.path.join(path, "overlays", overlay)
        if not os.path.exists(path_overlay):
            if missing_overlay == "use_base":
                path_overlay = os.path.join(path, "base")
                if not os.path.exists(path_overlay):
                    raise errors.ResourceBuildError(
                        "overlay path and base path not found"
                    )
            elif missing_overlay == "ignore":
                with open(os.path.join(path, file), "w") as f:
                    f.write("")
                return
            elif missing_overlay == "throw_error":
                raise errors.ResourceBuildError("overlay path not found")
            else:
                raise errors.ResourceBuildError(
                    f"Unkown value for missing_overlay: {missing_overlay}"
                )
        build_command = "kustomize build"
        try:
            p = cls.execute(build_command, path_overlay)
        except FileNotFoundError as e:
            raise errors.ResourceBuildError("Cannot find kustomize in PATH")
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))
        path = os.path.join(path, file)
        with open(path, "w") as f:
            f.write(p.stdout.decode("UTF-8"))

    @hookimpl
    def action(self, name, state, env):
        self.check_kubectl()
        if name == "build":
            return self.build(state, env)
        elif name == "test":
            return self.test(state, env)
        elif name == "deploy":
            return self.deploy(state, env)

    def build(self, state: dict, env: EnvResource):
        """
        Build the kustomize resource based on its resource file

        Args:
            base_path (str): This path is joined with the path in the spec
            to get the full path to the kustomize files directory.
        """
        if env is None:
            raise errors.ResourceBuildError(
                "Building a kustomize resource requires an env"
            )
        path = os.path.join(self.getPath(), f"artifact-manifests-{self.name}.yaml")
        self.generate(
            self.getPath(),
            f"artifact-manifests-{self.name}.yaml",
            env,
            self.getSpec("overlay"),
            self.getSpec("missing_overlay", "use_base"),
        )
        namespace = self.getSpec("namespace", env.getName())
        force_namespace = self.getSpec("force_namespace", False)
        with open(path, "r") as f:
            manifests = yaml.safe_load_all(f)
            new_manifests = []
            for manifest in manifests:
                if manifest.get("kind") == "Namespace" or manifest.get(
                    "kind", ""
                ).startswith("Cluster"):
                    new_manifests.append(manifest)
                    continue
                if (
                    manifest.get("metadata", {}).get("namespace") is not None
                    and force_namespace
                ):
                    manifest["metadata"]["namespace"] = namespace
                elif manifest.get("metadata", {}).get("namespace") is None:
                    manifest["metadata"]["namespace"] = namespace
                new_manifests.append(manifest)
        with open(path, "w") as f:
            yaml.safe_dump_all(new_manifests, f)
        env_variables = self.getSpec("envs", {})
        for name, value in env_variables.items():
            os.environ[name] = value
        try:
            command = f"cat {path} | envsubst"
            p = self.execute(command, os.path.dirname(path))
            with open(path, "w") as f:
                f.write(p.stdout.decode("UTF-8"))
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(
                f"An error when filling env variables in manifests: {p.stderr.decode('UTF-8')}"
            )
        artifact = self.create_artifact(
            "manifests", "build", env.getName(), state.get("hash", ""), "file", path
        )
        return {"msg": "manifests generated", "artifacts": [artifact]}

    @classmethod
    def runTests(
        cls,
        target: Target,
        path: str,
        artifacts: list,
        env: EnvResource,
        kubectl: str,
        overlay=None,
        missing_overlay="use_base",
    ):
        if overlay is None:
            path_overlay = os.path.join(path, "overlays", env.getName())
        else:
            path_overlay = os.path.join(path, "overlays", overlay)
        if not os.path.exists(path_overlay):
            if missing_overlay == "use_base":
                path_overlay = os.path.join(path, "base")
                if not os.path.exists(path_overlay):
                    raise errors.ResourceBuildError(
                        "overlay path and base path not found"
                    )
            elif missing_overlay == "ignore":
                return
            elif missing_overlay == "throw_error":
                raise errors.ResourceBuildError("overlay path not found")
            else:
                raise errors.ResourceBuildError(
                    f"Unkown value for missing_overlay: {missing_overlay}"
                )
        test_command = "kustomize build -o=/dev/null"
        try:
            cls.execute(test_command, path_overlay)
        except FileNotFoundError as e:
            raise errors.ResourceTestError("Cannot find kustomize in PATH")
        except subprocess.CalledProcessError as e:
            raise errors.ResourceTestError(e.stderr.decode("UTF-8"))
        if target:
            for artifact in artifacts:
                config = {
                    "path": path,
                    "kubectl": kubectl,
                    "manifests_path": artifact.getData(),
                }
                try:
                    target.action("test", config)
                except errors.ResourceError as e:
                    raise errors.ResourceTestError(str(e))

    @classmethod
    def applyManifests(cls, env: EnvResource, path: str, artifacts: list, kubectl: str):
        if env is None:
            raise errors.ResourceDeployError("You need an env to apply k8s manifests")
        target = env.getTarget("K8STarget")
        if target is None:
            raise errors.ResourceDeployError(
                f"No K8S target found in env {env.getName()}"
            )
        for artifact in artifacts:
            config = {
                "path": path,
                "kubectl": kubectl,
                "manifests_path": artifact.getData(),
            }
            try:
                target.action("deploy", config)
            except errors.ResourceError as e:
                raise errors.ResourceDeployError(str(e))

    def test(self, state: dict, env: EnvResource):
        if env is None:
            raise errors.ResourceTestError(
                "Testing a kustomize resource requires an env"
            )
        else:
            artifacts = state["envs"][env.getName()]["build"].get("artifacts", [])
            target = env.getTarget("K8STarget")
            if target is None:
                raise errors.ResourceTestError(
                    f"No target of kind K8STarget in env {env}"
                )
        namespace = self.getSpec("namespace", env.getName())
        try:
            config = {"path": self.getPath(), "namespace": namespace}
            target.action("create_namespace", config)
        except subprocess.CalledProcessError:
            pass
        self.runTests(
            target,
            self.getPath(),
            artifacts,
            env,
            self.__kubectl,
            self.getSpec("overlay"),
            self.getSpec("missing_overlay", "use_base"),
        )
        return {"msg": "kustomize tested without errors"}

    def deploy(self, state: dict, env: EnvResource):
        if env is None:
            raise errors.ResourceTestError(
                "Deploying a kustomize resource requires an env"
            )
        else:
            artifacts = state["envs"][env.getName()]["build"].get("artifacts", [])
        self.applyManifests(env, self.getPath(), artifacts, self.__kubectl)
        return {"msg": "kustomize applied without errors"}


# Docker resource


class DockerImageResource(Resource):
    @classmethod
    def build_image_name(cls, res, state):
        image_name = res.getSpec("image_name", res.name)
        image_tag = res.getSpec("image_tag")
        if image_tag:
            image_name += ":" + image_tag + "-" + state["hash"][:6]
        else:
            image_name += ":" + state["hash"][:6]
        return image_name

    @hookimpl
    def init(self, file: str):
        """
        Initialize the Docker Image resource.

        Args:
            content (dict): The dictionary that represents the YAML file resource.
        """
        super().__init__(file)
        if self.getKind() != "DockerImage":
            raise errors.ResourceConfigError("This is not a DockerImage resource")
        self.name = self.getMetadata("name")

    @classmethod
    def DockerBuild(cls, path, image_name, docker_file="Dockerfile"):
        build_command = f"docker build -t {image_name} . -f {docker_file}"
        try:
            cls.execute(build_command, path)
            return {"error": False, "msg": "built docker image"}
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))

    @hookimpl
    def action(self, name, state, env):
        if name == "build":
            return self.build(state, env)
        elif name == "test":
            return self.test(state, env)
        elif name == "publish":
            return self.publish(state, env)
        elif name == "deploy":
            return self.deploy(state, env)

    def build(self, state: dict, env: EnvResource):
        image_name = self.build_image_name(self, state)
        ret = self.DockerBuild(
            self.getPath(), image_name, self.getSpec("docker_file", "Dockerfile")
        )
        save_command = f"docker save {image_name} -o docker.build"
        try:
            self.execute(save_command, self.getPath())
            if env:
                ret["artifacts"] = [
                    self.create_artifact(
                        "image_file",
                        "build",
                        env.getName(),
                        state["hash"],
                        "file",
                        os.path.join(self.getPath(), "docker.build"),
                    )
                ]
            else:
                ret["artifacts"] = [
                    self.create_artifact(
                        "image_file",
                        "build",
                        None,
                        state["hash"],
                        "file",
                        os.path.join(self.getPath(), "docker.build"),
                    )
                ]
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))
        return ret

    @classmethod
    def runTests(cls, image_name, path, accept_latest=False, docker_file="Dockerfile"):
        test_command = f"docker build -t {image_name} . -f {docker_file}"
        try:
            cls.execute(test_command, path)
        except subprocess.CalledProcessError as e:
            raise errors.ResourceTestError(e)
        if accept_latest:
            return
        with open(os.path.join(path, docker_file)) as f:
            line = f.readline()
            while line:
                parts = line.split(" ")
                if len(parts) > 1:
                    if parts[0] == "FROM":
                        second_part = parts[1].split(":")
                        if len(second_part) == 1:
                            raise errors.ResourceTestError(
                                Exception(
                                    f"no tag is specified for image {second_part[0]}"
                                )
                            )
                        else:
                            if second_part[1].strip() == "latest":
                                raise errors.ResourceTestError(
                                    Exception(
                                        f"latest tag is specified for image {second_part[0]}"
                                    )
                                )
                line = f.readline()

    def test(self, state: dict, env: EnvResource):
        image_name = self.build_image_name(self, state)
        self.runTests(
            image_name,
            self.getPath(),
            self.getSpec("accept_latest", False),
            self.getSpec("docker_file", "Dockerfile"),
        )
        return {"error": False, "msg": "tested docker image"}

    def publish(self, state: dict, env: EnvResource):
        if env is None:
            raise errors.ResourcePublishError(
                "Cannot publish Docker resource without an env"
            )
        artifacts = state["envs"][env.getName()]["build"].get("artifacts", [])
        image_name = self.build_image_name(self, state)
        config = {
            "path": self.getPath(),
            "image_name": image_name,
            "docker_file": self.getSpec("docker_file", "Dockerfile"),
            "image_file": os.path.join(self.getPath(), "docker.build"),
        }
        target = env.getTarget("DockerRegistryTarget")
        if target is None:
            raise errors.ResourceDeployError(
                f"No Docker Registry target found in env {env.getName()}"
            )
        image_url = target.action("publish", config)
        return {
            "artifacts": [
                self.create_artifact(
                    "image_url",
                    "publish",
                    env.getName(),
                    state.get("hash", ""),
                    "url",
                    image_url,
                )
            ]
        }

    def deploy(self, state: dict, env: EnvResource):
        if env is None:
            raise errors.ResourceDeployError(
                "Cannot deploy Docker resource without an env"
            )
        artifacts = state["envs"][env.getName()]["publish"].get("artifacts", [])
        image_url = artifacts[0].getData()
        config = {
            "path": self.getPath(),
            "kind": "DockerImage",
            "port": self.getSpec("expose_port"),
            "service_account": self.getSpec("service_account"),
            "pod_name": self.getSpec("pod_name", self.name),
            "image_url": image_url,
        }
        target = env.getTarget("K8STarget")
        if target is None:
            raise errors.ResourceDeployError(
                f"No K8S target found in env {env.getName()}"
            )
        target.action("deploy", config)


# Go Service resource


class GoServiceResource(Resource):
    @hookimpl
    def init(self, file: str):
        """
        Initialize the GoService resource.

        Args:
            content (dict): The dictionary that represents the YAML file resource.
        """
        super().__init__(file)
        if self.getKind() != "GoService":
            raise errors.ResourceConfigError("This is not a GoService resource")
        self.name = self.getMetadata("name")

    @classmethod
    def compile(cls, go_executable, executable_name, path, go_mod_path: str):
        go_version_command = f"{go_executable} version"
        ret = {}
        try:
            r = cls.execute(go_version_command, path)
            r = r.stdout.decode("utf-8")
            ret["version"] = r.split(" ")[2][2:]
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))
        go_mod_tidy_command = f"{go_executable} mod tidy"
        try:
            cls.execute(go_mod_tidy_command, go_mod_path)
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))
        compile_command = f"{go_executable} build -o {executable_name} ."
        try:
            os.environ["CGO_ENABLED"] = "0"
            cls.execute(compile_command, path)
            return ret
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.stderr.decode("UTF-8"))

    @classmethod
    def runTests(cls, go_executable, golangci_lint_executable, path):
        golangci_lint_version_command = f"{golangci_lint_executable} version"
        ret = {}
        try:
            r = cls.execute(golangci_lint_version_command, path)
            r = r.stdout.decode("utf-8")
            ret["version"] = r.split(" ")[3]
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e)
        lint_command = f"{golangci_lint_executable} run"
        test_command = f"{go_executable} test ./..."
        try:
            cls.execute(lint_command, path)
            cls.execute(test_command, path)
            return ret
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e.output.decode("utf-8"))

    @hookimpl
    def action(self, name, state, env):
        if name == "build":
            return self.build(state, env)
        elif name == "test":
            return self.test(state, env)

    def build(self, state: dict, env: EnvResource):
        executable_name = self.getSpec("exec_name", self.name)
        self.compile("go", executable_name, self.getPath(), self.getPath())
        artifact = self.create_artifact(
            "binary",
            "build",
            env.getName(),
            state["hash"],
            "file",
            os.path.join(self.getPath(), executable_name),
        )
        return {"status": "Go Service compiled without errors", "artifacts": [artifact]}

    def test(self, state: dict, env: EnvResource):
        self.runTests("go", "golangci-lint", self.getPath())
        return {"status": "Go service tested without errors"}

    @hookimpl
    def re_action(state: dict, action: str, env={}) -> bool:
        return False


class MicroService(object):
    @classmethod
    def build(cls, res, state, target, env: EnvResource):
        docker_path = os.path.join(res.getPath(), res.getSpec("docker_path", "."))
        image_name = DockerImageResource.build_image_name(res, state)
        config = {"image_name": image_name, "path": res.getPath()}
        image_url = target.action("publish", config)
        k8s_path = os.path.join(res.getPath(), res.getSpec("k8s_path", "k8s"))
        KustomizeResource.generate(k8s_path, "manifests.yaml", env)
        k8s_file = os.path.join(k8s_path, "manifests.yaml")
        try:
            with open(k8s_file, "r") as f:
                if f.read() == "" and not res.getSpec("allow_empty_manifests", True):
                    raise errors.ResourceBuildError(
                        "Empty manifests file and allow_empty_manifests is set to false"
                    )
        except FileNotFoundError:
            if not res.getSpec("allow_empty_manifests", True):
                raise errors.ResourceBuildError(
                    "Empty manifests file and allow_empty_manifests is set to false"
                )
            else:
                with open(k8s_file, "w") as f:
                    f.write("")
        os.environ["IMAGE_URL"] = image_url
        try:
            command = f"cat manifests.yaml | envsubst"
            p = subprocess.run(
                command,
                cwd=k8s_path,
                check=True,
                capture_output=True,
                shell=True,
                timeout=10,
            )
            with open(k8s_file, "w") as f:
                f.write(p.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            raise errors.ActionError(
                f"Cannot replace IMAGE URL in manifests file : error {p.stderr.decode('utf-8')}"
            )
        return image_url, k8s_file

    @classmethod
    def test(cls, res, target, artifacts, env: EnvResource):
        # Test docker image
        image_name = res.getSpec("image_name", res.name)
        DockerImageResource.runTests(image_name, res.getPath())

        # Test k8s manifests
        for artifact in artifacts:
            if artifact.getId() == "k8s":
                k8s_path = os.path.join(res.getPath(), res.getSpec("k8s_path", "k8s"))
                # TODO: install kubectl binary before this call.
                KustomizeResource.runTests(target, k8s_path, [artifact], env, "kubectl")
                break

    @classmethod
    def deploy(cls, res, target, artifacts):
        config = {"path": res.getPath()}
        for artifact in artifacts:
            if artifact.getId() == "k8s":
                config["manifests_path"] = artifact.getData()
                target.action("deploy", config)
                break


# Go Micro Service resource
class GoMicroServiceResource(Resource):
    @hookimpl
    def init(self, file: str):
        """
        Initialize the GoMicroService resource.

        Args:
            content (dict): The dictionary that represents the YAML file resource.
        """
        super().__init__(file)
        if self.getKind() != "GoMicroService":
            raise errors.ResourceConfigError("This is not a GoMicroService resource")
        self.name = self.getMetadata("name")
        self.__go_checksums = {
            "1.20.3": "979694c2c25c735755bf26f4f45e19e64e4811d661dd07b8c010f7a8e18adfca",
            "1.20.2": "4eaea32f59cde4dc635fbc42161031d13e1c780b87097f4b4234cfce671f1768",
            "1.20.1": "000a5b1fca4f75895f78befeb2eecf10bfff3c428597f3f1e69133b63b911b02",
            "1.20": "5a9ebcc65c1cce56e0d2dc616aff4c4cedcfbda8cc6f0288cc08cda3b18dcbf1",
            "1.19.8": "e1a0bf0ab18c8218805a1003fd702a41e2e807710b770e787e5979d1cf947aba",
            "1.19.7": "7a75720c9b066ae1750f6bcc7052aba70fa3813f4223199ee2a2315fd3eb533d",
            "1.19.6": "e3410c676ced327aec928303fef11385702a5562fd19d9a1750d5a2979763c3d",
            "1.19.5": "36519702ae2fd573c9869461990ae550c8c0d955cd28d2827a6b159fda81ff95",
            "1.19.4": "c9c08f783325c4cf840a94333159cc937f05f75d36a8b307951d5bd959cf2ab8",
            "1.19.3": "74b9640724fd4e6bb0ed2a1bc44ae813a03f1e72a4c76253e2d5c015494430ba",
            "1.19.2": "5e8c5a74fe6470dd7e055a461acda8bb4050ead8c2df70f227e3ff7d8eb7eeb6",
            "1.19.1": "acc512fbab4f716a8f97a8b3fbaa9ddd39606a28be6c2515ef7c6c6311acffde",
            "1.19": "464b6b66591f6cf055bc5df90a9750bf5fbc9d038722bb84a9d56a2bea974be6",
            "1.18": "e85278e98f57cdb150fe8409e6e5df5343ecb13cebf03a5d5ff12bd55a80264f",
            "1.18.1": "b3b815f47ababac13810fc6021eb73d65478e0b2db4b09d348eefad9581a2334",
            "1.18.2": "e54bec97a1a5d230fc2f9ad0880fcbabb5888f30ed9666eca4a91c5a32e86cbc",
            "1.18.3": "956f8507b302ab0bb747613695cdae10af99bbd39a90cae522b7c0302cc27245",
            "1.18.4": "c9b099b68d93f5c5c8a8844a89f8db07eaa58270e3a1e01804f17f4cf8df02f5",
            "1.18.5": "9e5de37f9c49942c601b191ac5fba404b868bfc21d446d6960acc12283d6e5f2",
            "1.18.6": "bb05f179a773fed60c6a454a24141aaa7e71edfd0f2d465ad610a3b8f1dc7fe8",
            "1.18.7": "6c967efc22152ce3124fc35cdf50fc686870120c5fd2107234d05d450a6105d8",
            "1.18.8": "4d854c7bad52d53470cf32f1b287a5c0c441dc6b98306dea27358e099698142a",
            "1.18.9": "015692d2a48e3496f1da3328cf33337c727c595011883f6fc74f9b5a9c86ffa8",
            "1.18.10": "5e05400e4c79ef5394424c0eff5b9141cb782da25f64f79d54c98af0a37f8d49",
        }
        self.__golangci_lint_checksums = {
            "1.52.2": "c9cf72d12058a131746edd409ed94ccd578fbd178899d1ed41ceae3ce5f54501",
            "1.52.1": "f31a6dc278aff92843acdc2671f17c753c6e2cb374d573c336479e92daed161f",
            "1.52.0": "01d258cd96a9df40e5d50b802bfeea115853d1409abb029b3cc5c7699e5091b7",
            "1.51.2": "4de479eb9d9bc29da51aec1834e7c255b333723d38dbd56781c68e5dddc6a90b",
            "1.51.1": "17aeb26c76820c22efa0e1838b0ab93e90cfedef43fbfc9a2f33f27eb9e5e070",
            "1.51.0": "38c25ae0ba5bfebd3ec42e9230547bd6461b179e47d7ba4d86950623bf28862a",
            "1.50.1": "4ba1dc9dbdf05b7bdc6f0e04bdfe6f63aa70576f51817be1b2540bbce017b69a",
            "1.50.0": "b4b329efcd913082c87d0e9606711ecb57415b5e6ddf233fde9e76c69d9b4e8b",
            "1.49.0": "5badc6e9fee2003621efa07e385910d9a88c89b38f6c35aded153193c5125178",
        }
        self.__go = "go"
        self.__golangci_lint = "golangci-lint"

    def check_go(self):
        go_version = self.getSpec("go_version")
        if type(go_version) != str:
            raise errors.ResourceError(
                f"go_version must be string found: {type(go_version)}"
            )
        if go_version:
            try:
                if os.path.isfile(
                    os.path.join(
                        self.getSpace().get_hash_dir(),
                        f"go{go_version}.linux-amd64",
                        "bin",
                        "go",
                    )
                ):
                    self.execute(f"{self.__go} version", self.getPath())
                    self.__go = os.path.join(
                        self.getSpace().get_hash_dir(),
                        f"go{go_version}.linux-amd64",
                        "bin",
                        "go",
                    )
            except subprocess.CalledProcessError as e:
                raise errors.ActionError(e.stderr.decode("UTF-8"))
        else:
            self.__go = "go"

    def check_golangci_lint(self):
        check_golangci_lint_version = self.getSpec("golangci_lint_version")
        if type(check_golangci_lint_version) != str:
            raise errors.ResourceError(
                f"golangci_lint_version must be string found: {type(check_golangci_lint_version)}"
            )
        if check_golangci_lint_version:
            try:
                if os.path.isfile(
                    os.path.join(
                        self.getSpace().get_hash_dir(),
                        f"golangci-lint-{check_golangci_lint_version}-linux-amd64",
                        "golangci-lint",
                    )
                ):
                    self.execute(f"{self.__golangci_lint} version", self.getPath())
                    self.__golangci_lint = os.path.join(
                        self.getSpace().get_hash_dir(),
                        f"golangci-lint-{check_golangci_lint_version}-linux-amd64",
                        "golangci-lint",
                    )
            except subprocess.CalledProcessError as e:
                raise errors.ActionError(e.stderr.decode("UTF-8"))
        else:
            self.__golangci_lint = "golangci-lint"

    def __install_go(self, version: str):
        self.check_go()
        if self.__go != "go":
            return
        try:
            file_name = f"go{version}.linux-amd64.tar.gz"
            hash_dir = self.getSpace().get_hash_dir()
            self.execute(f"wget -c https://go.dev/dl/{file_name}", hash_dir)
            with open(os.path.join(hash_dir, "checksums.txt"), "w") as f:
                checksum = self.__go_checksums.get(version, self.getSpec("go_checksum"))
                if checksum is None:
                    raise errors.ActionError(
                        f"version {version} doesn't have a checksum in specs or in the resource's class"
                    )
                f.write(f"{checksum} {file_name}")
            self.execute("sha256sum -c checksums.txt", hash_dir)
            self.execute(f"tar -zxf {file_name}", hash_dir)
            self.execute(f"mv go go{version}.linux-amd64", hash_dir)
            self.__go = os.path.join(hash_dir, f"go{version}.linux-amd64", "bin", "go")
        except subprocess.CalledProcessError as e:
            raise errors.ActionError(e.stderr.decode("UTF-8"))

    def __install_golangci_lint(self, version: str):
        self.check_golangci_lint()
        if self.__golangci_lint != "golangci-lint":
            return
        try:
            file_name = f"golangci-lint-{version}-linux-amd64.tar.gz"
            hash_dir = self.getSpace().get_hash_dir()
            self.execute(
                f"wget -c https://github.com/golangci/golangci-lint/releases/download/v{version}/{file_name}",
                hash_dir,
            )
            with open(os.path.join(hash_dir, "checksums.txt"), "w") as f:
                checksum = self.__golangci_lint_checksums.get(
                    version, self.getSpec("golangci_lint_checksum")
                )
                if checksum is None:
                    raise errors.ActionError(
                        f"version {version} doesn't have a checksum in specs or in the resource's class"
                    )
                f.write(f"{checksum} {file_name}")
            self.execute("sha256sum -c checksums.txt", hash_dir)
            self.execute(f"tar -zxf {file_name}", hash_dir)
            self.__golangci_lint = os.path.join(
                hash_dir, f"golangci-lint-{version}-linux-amd64", "golangci-lint"
            )
        except subprocess.CalledProcessError as e:
            raise errors.ActionError(e.stderr.decode("UTF-8"))

    def setup_tools(self):
        go_version = self.getSpec("go_version")
        if go_version:
            try:
                r = self.execute(f"{self.__go} version", self.getPath())
                r = r.stdout.decode("utf-8")
                version = r.split(" ")[2][2:]
                if version != go_version:
                    if not self.getSpec("go_install"):
                        raise errors.ActionError(
                            f"go version is {version}, required version {go_version} but go_install is not set to True"
                        )
                    self.__install_go(go_version)
            except subprocess.CalledProcessError as e:
                raise errors.ActionError(e.stderr.decode("UTF-8"))
        golangci_lint_version = self.getSpec("golangci_lint_version")
        if golangci_lint_version:
            try:
                r = self.execute(f"{self.__golangci_lint} version", self.getPath())
                r = r.stdout.decode("utf-8")
                version = r.split(" ")[3]
                if version != golangci_lint_version:
                    if not self.getSpec("golangci_lint_install"):
                        raise errors.ActionError(
                            f"golangci-lint version is {version}, required version {golangci_lint_version} but golangci_lint_install is not set to True"
                        )
                    self.__install_golangci_lint(golangci_lint_version)
            except subprocess.CalledProcessError as e:
                raise errors.ActionError(e.stderr.decode("UTF-8"))

    @hookimpl
    def get_ignores(self):
        return [".deployed"]

    @hookimpl
    def action(self, name, state, env):
        self.setup_tools()
        if name == "build":
            return self.build(state, env)
        elif name == "test":
            return self.test(state, env)
        elif name == "deploy":
            return self.deploy(state, env)

    def build(self, state: dict, env: EnvResource):
        if env is None:
            raise errors.ResourceBuildError(
                f"Building micro service {self} requires an env"
            )
        deploy_target = self.getSpec("deploy_target", "kubernetes")
        if deploy_target == "kubernetes":
            target = env.getTarget("DockerRegistryTarget")
            if target is None:
                raise errors.ResourceBuildError(
                    f"No target of kind DockerRegistry in env {env}"
                )
        elif deploy_target == "DOFunction":
            target = env.getTarget("DOFunctionTarget")
            if target is None:
                raise errors.ResourceBuildError(
                    f"No target of kind DOFunction in env {env}"
                )
        else:
            raise errors.ResourceBuildError(
                f"Invalid value for 'deploy_target': {deploy_target}, valid values are: 'kubernetes' and 'DOFunction'"
            )
        # Build go service
        executable_name = self.getSpec("exec_name", self.name)
        go_mod_path = self.getSpec("go_mod_path")
        if go_mod_path is None:
            go_mod_path = self.getSpace().get_base()
        else:
            go_mod_path = os.path.join(self.getPath(), go_mod_path)
        h = kern.Hash()
        go_mod_hash = h.hash(go_mod_path, ["go.mod", "go.sum"])
        go_env_data = GoServiceResource.compile(
            self.__go, executable_name, self.getPath(), go_mod_path
        )
        executable_path = os.path.join(self.getPath(), executable_name)

        binary_artifact = self.create_artifact(
            "binary", "build", env.getName(), state["hash"], "file", executable_path
        )
        if deploy_target == "DOFunction":
            return {
                "artifacts": [binary_artifact],
                "_go": go_env_data,
                "_go_mod_hash": go_mod_hash,
            }
        image_url, k8s_file = MicroService.build(self, state, target, env)
        k8s_artifact = self.create_artifact(
            "k8s", "build", env.getName(), state["hash"], "file", k8s_file
        )
        image_url_artifact = self.create_artifact(
            "image_url", "build", env.getName(), state["hash"], "url", image_url
        )
        return {
            "artifacts": [binary_artifact, k8s_artifact, image_url_artifact],
            "_go": go_env_data,
            "_go_mod_hash": go_mod_hash,
        }

    def test(self, state: dict, env: EnvResource):
        if env is None:
            raise errors.ResourceTestError(
                f"Testing micro service {self} requires an env"
            )
        deploy_target = self.getSpec("deploy_target", "kubernetes")
        if deploy_target == "kubernetes":
            target = env.getTarget("K8STarget")
            if target is None:
                raise errors.ResourceTestError(
                    f"No target of kind K8STarget in env {env}"
                )
        elif deploy_target == "DOFunction":
            target = env.getTarget("DOFunctionTarget")
            if target is None:
                raise errors.ResourceTestError(
                    f"No target of kind DOFunction in env {env}"
                )
        else:
            raise errors.ResourceTestError(
                f"Invalid value for 'deploy_target': {deploy_target}, valid values are: 'kubernetes' and 'DOFunction'"
            )
        artifacts = state["envs"][env.getName()]["build"].get("artifacts", [])
        # Test go code
        golang_ci_lint_env_data = GoServiceResource.runTests(
            self.__go, self.__golangci_lint, self.getPath()
        )
        if deploy_target == "kubernetes":
            namespace = self.getSpec("namespace", env.getName())
            try:
                config = {"path": self.getPath(), "namespace": namespace}
                target.action("create_namespace", config)
            except subprocess.CalledProcessError:
                pass
            MicroService.test(self, target, artifacts, env)
        return {"_golangci_lint": golang_ci_lint_env_data}

    def deploy(self, state: dict, env):
        # deploy k8s manifests only
        if env is None:
            raise errors.ResourceDeployError(
                f"Deploying micro service {self} requires an env"
            )
        deploy_target = self.getSpec("deploy_target", "kubernetes")
        if deploy_target == "kubernetes":
            target = env.getTarget("K8STarget")
            if target is None:
                raise errors.ResourceTestError(
                    f"No target of kind K8STarget in env {env}"
                )
        elif deploy_target == "DOFunction":
            target = env.getTarget("DOFunctionTarget")
            if target is None:
                raise errors.ResourceTestError(
                    f"No target of kind DOFunction in env {env}"
                )
        else:
            raise errors.ResourceTestError(
                f"Invalid value for 'deploy_target': {deploy_target}, valid values are: 'kubernetes' and 'DOFunction'"
            )
        artifacts = state["envs"][env.getName()]["build"].get("artifacts", [])
        if deploy_target == "kubernetes":
            MicroService.deploy(self, target, artifacts)
        else:
            url = target.action(
                "deploy",
                {
                    "project_dir": self.getPath(),
                    "package_name": self.getSpec("do_function", {}).get(
                        "package_name", self.getName()
                    ),
                    "function_name": self.getSpec("do_function", {}).get(
                        "function_name", self.getName()
                    ),
                },
            )
            return {"globals": {"do_function_url": url}}

    @hookimpl
    def re_action(self, action, state, env: EnvResource):
        if env is None:
            result = state.get("no_env")
        else:
            result = state.get("envs", {}).get(env.getName())
        go_mod_path = self.getSpec("go_mod_path")
        if go_mod_path is None:
            go_mod_path = self.getSpace().get_base()
        else:
            go_mod_path = os.path.join(self.getPath(), go_mod_path)
        h = kern.Hash().hash(go_mod_path, ["go.mod", "go.sum"])
        go_mod_hash = result.get("build", {}).get("_go_mod_hash")
        if go_mod_hash != h:
            return True
        if action == "deploy" and env is not None:
            target = env.getTarget("K8STarget")
            if target:
                artifacts = (
                    state.get("envs", {})
                    .get(env.getName(), {})
                    .get("build", {})
                    .get("artifacts", [])
                )
                for artifact in artifacts:
                    if artifact.getId() != "k8s":
                        continue
                    config = {
                        "path": self.getPath(),
                        "manifests_path": artifact.getData(),
                        "diff": True,
                    }
                    try:
                        return target.action("test", config)
                    except errors.ResourceError as e:
                        raise errors.ResourceTestError(str(e))

        self.check_go()
        go_version = result.get("build", {}).get("_go", {}).get("version")
        go_version_command = f"{self.__go} version"
        try:
            r = self.execute(go_version_command, self.getPath())
            r = r.stdout.decode("utf-8")
            version = r.split(" ")[2][2:]
            if version != go_version:
                return True
        except subprocess.CalledProcessError as e:
            raise errors.ResourceBuildError(e)
        return False


def get_plugin_manager():
    pm = pluggy.PluginManager("hash-resource")
    pm.add_hookspecs(ResourceSpec)
    pm.load_setuptools_entrypoints("hash-resource")
    pm.register(FakeResource, "FakeResource")
    pm.register(EnvResource, "EnvResource")
    pm.register(ProjectResource, "ProjectResource")
    pm.register(TerraformResource, "TerraformResource")
    pm.register(KustomizeResource, "KustomizeResource")
    pm.register(DockerImageResource, "DockerImageResource")
    pm.register(GoServiceResource, "GoServiceResource")
    pm.register(GoMicroServiceResource, "GoMicroServiceResource")
    return pm


def get_resource(file: str):
    """
    Retrun the specific resource object of the resource file
    passed as an argument

    args:
        file (str): The path to the resource's file
    """
    data = utils.parse_resource_file(file)
    kind = data["kind"] + "Resource"
    pm = get_plugin_manager()
    plugins = pm.list_name_plugin()
    for plugin in plugins:
        if kind == plugin[0]:
            hash_resource = plugin[1](file)
            if callable(getattr(hash_resource, "init", None)):
                hash_resource.init(file)
            return hash_resource


class ResourceSpace(object):
    def __init__(self, base: str, store=None) -> None:
        self.__base = base
        self.__store = store
        hash_dir = os.path.join(base, ".hash")
        if not os.path.isdir(hash_dir):
            os.mkdir(hash_dir)

    def read(self, file: str):
        path = os.path.join(self.__base, file)
        return get_resource(path)

    def find_resource_by_id(self, res_id):
        utils.check_type(
            res_id,
            str,
            errors.ResourceError,
            False,
            f"resource id must be str: found {type(res_id)}",
        )
        res_id_parts = res_id.split(":")
        if len(res_id_parts) != 2:
            raise errors.ResourceError(f"Invalid resource ID: {res_id}")
        return self.find_resource(res_id_parts[1], res_id_parts[0])

    def get_base(self):
        return str(self.__base)

    def get_hash_dir(self):
        return os.path.join(self.__base, ".hash")

    def get_secret_from_store(self, key: str):
        return self.__store.read_secret(key)

    def find_resource(self, name: str, kind: str):
        """
        Search the workspace for a resource based on its namd and kind

        args:
            name (str): The name of the resource to find.
            kind (str): The kind of the resource to find
        """
        find_command = "find . -name *.yaml"
        find_command = shlex.split(find_command)
        find = subprocess.run(find_command, cwd=self.__base, stdout=subprocess.PIPE)
        resource_files = find.stdout.decode().split("\n")[:-1]
        for file in resource_files:
            f = file.split("/")[-1]
            if f.startswith("resource"):
                rs = self.read(file)
                if rs and rs.getKind() == kind and rs.getName() == name:
                    return rs

    def cal_spec(self, resource, env: str, _globals: dict):
        """
        This function updates the values of the resource's specs, based
        on the env and globals object

        args:
            resource (Resource): This is the resource which we want to update its spec
            env (str): The env in which the specs will be updated
            _globals (dict): A dictionary of the globals which are used to fill the
                values for specs which have $ in their names, values
        """
        env_id = f"Env:{env}"
        env_res = self.find_resource_by_id(env_id)
        if env_res is not None:
            mutate_spec_kind = env_res.getSpec(resource.getKind())
            if mutate_spec_kind:
                resource.mutate(mutate_spec_kind)
            resource_id = resource.getId().replace(":", "-")
            mutate_spec_id = env_res.getSpec(resource_id)
            if mutate_spec_id:
                resource.mutate(mutate_spec_id)
            parent_id = env_res.getParentId()
            if parent_id:
                parent_res = self.find_resource_by_id(parent_id)
                if parent_res is None:
                    raise errors.ResourceSpecError(
                        f"No resource with id {parent_id} in metatdata of {env_id}"
                    )
                mutate_spec_kind = parent_res.getSpec(resource.getKind())
                if mutate_spec_kind:
                    resource.mutate(mutate_spec_kind)
                resource_id = resource.getId().replace(":", "-")
                mutate_spec_id = parent_res.getSpec(resource_id)
                if mutate_spec_id:
                    resource.mutate(mutate_spec_id)

        resource.fill_specs(env, _globals, self)

    def calculate_hash(self, resource, alg="sha256"):
        ignore = []
        if self.__store is not None:
            artifact_paths = self.__store.get_artifact_paths(resource.getId())
            artifacts_paths = []
            for path in artifact_paths:
                new_path = path.replace(resource.getPath(), "")
                artifacts_paths.append(new_path.lstrip("./"))
            ignore = artifacts_paths
        r = Renderer(resource, self, [], {})
        templates = r.get_hash_templates()
        for template in templates:
            ignore.append(template.lstrip("./").rstrip(".hash"))
        if resource.getKind() == "Env":
            match = [resource.getFile().split("/")[-1]]
            match.extend(resource.getSpec("match", []))
            return kern.Hash(alg).hash(
                os.path.join(self.__base, resource.getPath()), match
            )
        match = resource.getSpec("match")
        if match:
            match.append(resource.getFile().split("/")[-1])
            match.append("*.hash")
        build_script = resource.getSpec("build_script")
        if build_script and match:
            match.append(build_script)
        if resource.getKind() == "Env":
            match = [resource.getFile().split("/")[-1]]
            match.extend(resource.getSpec("match", []))
        ignore.extend(resource.get_ignores())
        return kern.Hash(alg).hash(
            os.path.join(self.__base, resource.getPath()), match, ignore
        )
