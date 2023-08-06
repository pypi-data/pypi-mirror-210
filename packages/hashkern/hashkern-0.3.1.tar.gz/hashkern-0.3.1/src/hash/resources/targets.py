import os
import json
import yaml
from subprocess import CalledProcessError
import tempfile
import pluggy

from hash import target_hookimpl as hookimpl

from hash import errors, resources

hookspec = pluggy.HookspecMarker("hash-targets")


class TargetSpec:
    @hookspec
    def action(name: str, config: dict):
        pass

    @hookspec
    def _init(config: dict):
        pass


class Target(object):
    def _init(self, config: dict) -> None:
        self.name = config.get("name")
        if self.name is None:
            raise errors.TargetConfigError("No name specified for the target")
        self.kind = config.get("kind")
        if self.kind is None:
            raise errors.TargetConfigError("No kind specified for the target")
        self.spec = config.get("spec", {})


class FakeTarget(Target):
    @hookimpl
    def init(self, config: dict, space) -> None:
        self._init(config)
        if self.kind != "FakeTarget":
            raise errors.TargetConfigError(
                f"This target is not of kind Fake, it is of kind {self.kind}"
            )
        self.__space = space

    @hookimpl
    def action(name: str, config: dict, artifacts):
        pass


class K8STarget(Target):
    @hookimpl
    def init(self, config: dict, space) -> None:
        self._init(config)
        if self.kind != "K8STarget":
            raise errors.TargetConfigError(
                f"This target is not of kind K8S, it is of kind {self.kind}"
            )
        self.__space = space

    @hookimpl
    def action(self, name: str, config: dict):
        if name != "deploy" and name != "test" and name != "create_namespace":
            raise errors.TargetActionError(
                f"Cannot run action {name} with target of type K8S"
            )
        kubectl_binary = config.get("kubectl", "kubectl")
        context = self.spec.get("context")
        k8s_certificate_ca = self.spec.get("k8s_certificate_ca")
        if k8s_certificate_ca:
            try:
                open(k8s_certificate_ca, "r")
            except FileNotFoundError:
                t = k8s_certificate_ca
                k8s_certificate_ca = tempfile.mkstemp(text=True)
                with open(k8s_certificate_ca[1], "w") as f:
                    f.write(t)
                k8s_certificate_ca = k8s_certificate_ca[1]
            except OSError as e:
                if e.errno == 36:  # File name too long
                    t = k8s_certificate_ca
                    k8s_certificate_ca = tempfile.mkstemp(text=True)
                    with open(k8s_certificate_ca[1], "w") as f:
                        f.write(t)
                    k8s_certificate_ca = k8s_certificate_ca[1]
                else:
                    pass  # TODO: raise error
        k8s_certificate = self.spec.get("k8s_certificate")
        if k8s_certificate:
            try:
                open(k8s_certificate, "r")
            except FileNotFoundError:
                t = k8s_certificate
                k8s_certificate = tempfile.mkstemp(text=True)
                with open(k8s_certificate[1], "w") as f:
                    f.write(t)
                k8s_certificate = k8s_certificate[1]
            except OSError as e:
                if e.errno == 36:
                    t = k8s_certificate
                    k8s_certificate = tempfile.mkstemp(text=True)
                    with open(k8s_certificate[1], "w") as f:
                        f.write(t)
                    k8s_certificate = k8s_certificate[1]
                else:
                    pass
        k8s_client_key = self.spec.get("k8s_client_key")
        if k8s_client_key:
            try:
                open(k8s_client_key, "r")
            except FileNotFoundError:
                t = k8s_client_key
                k8s_client_key = tempfile.mkstemp(text=True)
                with open(k8s_client_key[1], "w") as f:
                    f.write(t)
                k8s_client_key = k8s_client_key[1]
            except OSError as e:
                if e.errno == 36:
                    t = k8s_client_key
                    k8s_client_key = tempfile.mkstemp(text=True)
                    with open(k8s_client_key[1], "w") as f:
                        f.write(t)
                    k8s_client_key = k8s_client_key[1]
                else:
                    pass
        k8s_kube_config = self.spec.get("k8s_kube_config")
        if k8s_kube_config:
            try:
                open(k8s_kube_config, "r")
            except FileNotFoundError:
                t = k8s_kube_config
                k8s_kube_config = tempfile.mkstemp(text=True)
                with open(k8s_kube_config[1], "w") as f:
                    f.write(t)
                k8s_kube_config = k8s_kube_config[1]
            except OSError as e:
                if e.errno == 36:
                    t = k8s_kube_config
                    k8s_kube_config = tempfile.mkstemp(text=True)
                    with open(k8s_kube_config[1], "w") as f:
                        f.write(t)
                    k8s_kube_config = k8s_kube_config[1]
                else:
                    pass
        server = self.spec.get("server")
        token = self.spec.get("token")
        config_kind = config.get("kind", "Kustomize")
        kubectl_args = ""
        path = config.get("path")
        if path is None:
            raise errors.ResourcePublishError(
                "You need to specify path for command execution"
            )
        use_gcloud = False
        if self.spec.get("use_gcloud") == True:
            use_gcloud = True
            cluster_name = self.spec.get("cluster_name")
            if cluster_name is None:
                raise errors.ActionError(
                    "use_gcloud is set to True but cluster_name is not set"
                )
            project_name = self.spec.get("project_name")
            if project_name is None:
                raise errors.ActionError(
                    "use_gcloud is set to True but project_name is not set"
                )
            cluster_region = self.spec.get("cluster_region")
            if cluster_region is None:
                cluster_zone = self.spec.get("cluster_zone")
                if cluster_zone is None:
                    raise errors.ActionError(
                        "neither cluster_region nor cluster_zone is set"
                    )
                try:
                    gcloud_command = f"gcloud container clusters get-credentials {cluster_name} --zone {cluster_zone} --project {project_name}"
                    os.environ["KUBECONFIG"] = os.path.join(
                        self.__space.get_hash_dir(),
                        f"{cluster_name}-{project_name}-config",
                    )
                    resources.Resource.execute(gcloud_command, path)
                except CalledProcessError as e:
                    raise errors.ActionError(e)
            else:
                try:
                    gcloud_command = f"gcloud container clusters get-credentials {cluster_name} --region {cluster_region} --project {project_name}"
                    os.environ["KUBECONFIG"] = os.path.join(
                        self.__space.get_hash_dir(),
                        f"{cluster_name}-{project_name}-config",
                    )
                    resources.Resource.execute(gcloud_command, path)
                except CalledProcessError as e:
                    raise errors.ActionError(e)
        use_az = False
        if self.spec.get("use_az") == True:
            use_az = True
            cluster_name = self.spec.get("cluster_name")
            if cluster_name is None:
                raise errors.ActionError(
                    "use_az is set to True but cluster_name is not set"
                )
            subscription_id = self.spec.get("subscription_id")
            if subscription_id is None:
                raise errors.ActionError(
                    "use_az is set to True but subscription_id is not set"
                )
            resource_group = self.spec.get("resource_group")
            if resource_group is None:
                raise errors.ActionError(
                    "use_az is set to True but resource_group is not set"
                )
            try:
                az_command = f"az aks get-credentials --name {cluster_name} --resource-group {resource_group} --subscription {subscription_id} --overwrite-existing"
                os.environ["KUBECONFIG"] = os.path.join(
                    self.__space.get_hash_dir(),
                    f"{cluster_name}-{resource_group}-{subscription_id}-config",
                )
                resources.Resource.execute(az_command, path)
            except CalledProcessError as e:
                raise errors.ActionError(e)
        if not use_gcloud and not use_az:
            if context:
                kubectl_args = f" --context={context} "
            else:
                if k8s_certificate_ca and k8s_certificate and k8s_client_key:
                    kubectl_args = f" --certificate-authority={k8s_certificate_ca} --client-certificate={k8s_certificate} --client-key={k8s_client_key} "
                if server:
                    kubectl_args += f" --server={server} "
                if token:
                    kubectl_args += f" --token={token} "
                if k8s_kube_config:
                    kubectl_args += f" --kubeconfig={k8s_kube_config} "
        if config_kind not in ["Kustomize", "DockerImage"]:
            raise errors.ResourceDeployError(
                "Config kind must be either 'Kustomize' or 'DockerImage'"
            )
        port = config.get("port")
        if port:
            kubectl_args += f"--port={port}"
        service_account = config.get("service_account")
        if service_account:
            kubectl_args += f"--serviceaccount={service_account}"
        if config_kind == "Kustomize" and name != "create_namespace":
            manifests_path = config.get("manifests_path")
            if manifests_path is None:
                raise errors.ResourceError(f"No manifests path supplied for K8S target")
            if name == "deploy":
                kubectl_command = (
                    f"{kubectl_binary} apply {kubectl_args} -f {manifests_path}"
                )
            elif name == "test" and config.get("diff") is not True:
                kubectl_command = f"{kubectl_binary} apply {kubectl_args} --dry-run=server -f {manifests_path}"
            elif name == "test" and config.get("diff") is True:
                kubectl_command = (
                    f"{kubectl_binary} diff {kubectl_args} -f {manifests_path}"
                )
        elif config_kind == "DockerImage":
            image_url = config.get("image_url")
            if image_url is None:
                raise errors.ResourceError("No image URL supplied for K8S target")
            pod_name = config.get("pod_name", name)
            kubectl_command = (
                f"{kubectl_binary} run {kubectl_args} --image={image_url} {pod_name}"
            )
        if name == "create_namespace":
            namespace = config.get("namespace")
            if namespace is None:
                raise errors.ResourceError(
                    "k8s target: create_namespace is reqested but no namespace name is provided"
                )
            kubectl_command = (
                f"{kubectl_binary} create namespace {kubectl_args} {namespace}"
            )
        try:
            resources.Resource.execute(kubectl_command, path)
        except CalledProcessError as e:
            if config.get("diff") is True and e.returncode == 1:
                return True
            if name == "create_namespace":
                raise e
            raise errors.ResourceError(e.stderr.decode("UTF-8"))
        finally:
            if k8s_certificate_ca:
                try:
                    os.remove(k8s_certificate_ca)
                except Exception:
                    pass
            if k8s_certificate:
                try:
                    os.remove(k8s_certificate)
                except Exception:
                    pass
            if k8s_client_key:
                try:
                    os.remove(k8s_client_key)
                except Exception:
                    pass
            if k8s_kube_config:
                try:
                    os.remove(k8s_kube_config)
                except Exception:
                    pass


class DockerRegistryTarget(Target):
    @hookimpl
    def init(self, config: dict, space) -> None:
        self._init(config)
        if self.kind != "DockerRegistryTarget":
            raise errors.TargetConfigError(
                f"This target is not of kind DockerRegistry, it is of kind {self.kind}"
            )
        self.__space = space

    @hookimpl
    def action(self, name: str, config: dict):
        if name != "publish":
            raise errors.TargetActionError(
                f"Cannot run action {name} with target of type Docker Registry"
            )
        registry_url = self.spec.get("registry_url")
        if registry_url is None:
            raise errors.ResourcePublishError("No registry_url in target")
        docker_config_dir = None
        credHelpers = self.spec.get("credHelpers")
        if credHelpers:
            docker_config_dir = tempfile.mkdtemp()
            with open(os.path.join(docker_config_dir, "config.json"), "w") as f:
                out = {"credHelpers": credHelpers}
                json.dump(out, f)
        docker_config = self.spec.get("docker_config")
        if docker_config:
            docker_config_dir = tempfile.mkdtemp()
            with open(os.path.join(docker_config_dir, "config.json"), "w") as f:
                f.write(docker_config)
        config_kind = config.get("kind", "DockerFile")
        if config_kind not in ["DockerFile", "DockerImage"]:
            raise errors.ResourcePublishError(
                "target connfig kind must be either 'DockerFile' or 'DockerImage'"
            )
        service_account = self.spec.get("service_account")
        login_command = None
        if service_account:
            registry_host = registry_url.split("/")[0]
            login_command = f"gcloud auth print-access-token --impersonate-service-account {service_account} | docker login -u oauth2accesstoken --password-stdin https://{registry_host}"
        use_az = self.spec.get("use_az")
        if use_az == True:
            registry_name = self.spec.get("registry_name")
            if registry_name is None:
                raise errors.ActionError("use_az is True but registry_name is not set")
            subscription_id = self.spec.get("subscription_id")
            if subscription_id is None:
                raise errors.ActionError(
                    "use_az is True but subscription_id is not set"
                )
            login_command = (
                f"az acr login --subscription {subscription_id} --name {registry_name}"
            )
        if config_kind == "DockerFile":
            image_name = config.get("image_name")
            if image_name is None:
                raise errors.ResourcePublishError("You need to specify image name")
            image_file = config.get("image_file")
            docker_file = config.get("docker_file", "Dockerfile")
            docker_file_path = config.get("docker_file_path", ".")
            image_url = f"{registry_url}/{image_name}"
            tag_command = None
            if docker_config_dir:
                if image_file:
                    build_command = f"docker image load -i {image_file}"
                    tag_command = f"docker tag {image_name} {image_url}"
                else:
                    build_command = f"docker --config={docker_config_dir} build -t {image_url} {docker_file_path} -f {docker_file}"
                publish_command = (
                    f"docker --config={docker_config_dir} push {image_url}"
                )
            else:
                if image_file:
                    build_command = f"docker image load -i {image_file}"
                    tag_command = f"docker tag {image_name} {image_url}"
                else:
                    build_command = f"docker build -t {image_url} {docker_file_path} -f {docker_file}"
                publish_command = f"docker push {image_url}"
            path = config.get("path")
            if path is None:
                raise errors.ResourcePublishError(
                    "You need to specify path for command execution"
                )
            try:
                if login_command:
                    resources.Resource.execute(login_command, path)
                resources.Resource.execute(build_command, path)
                if tag_command:
                    resources.Resource.execute(tag_command, path)
                resources.Resource.execute(publish_command, path)
                return image_url
            except CalledProcessError as e:
                raise errors.ResourcePublishError(e.stderr.decode("UTF-8"))


class DOFunctionTarget(Target):
    def __verify_function(
        self, package_name: str, function_name: str, config: dict
    ) -> bool:
        packages = config.get("packages", [])
        for package in packages:
            if package.get("name") == package_name:
                functions = package.get("functions", [])
                for function in functions:
                    if function.get("name") == function_name:
                        return True
        return False

    @hookimpl
    def init(self, config: dict, space) -> None:
        self._init(config)
        if self.kind != "DOFunctionTarget":
            raise errors.TargetConfigError(
                f"This target is not of kind DOFunction, it is of kind {self.kind}"
            )
        self.__space = space

    @hookimpl
    def action(self, name: str, config: dict):
        if name != "deploy":
            raise errors.ResourceError(
                f"DOFunction target can only run deploy actions not {name}"
            )
        region = self.spec.get("region")
        if region is None:
            raise errors.ResourceError("No region found in DOFunction target specs")
        project_dir = config.get("project_dir")
        if project_dir is None:
            raise errors.ResourceError(
                "No project_dir provided in config for DOFunction target"
            )
        if not os.path.exists(os.path.join(project_dir, "project.yml")):
            raise errors.ResourceError(f"No project.yml file found in {project_dir}")
        package_name = config.get("package_name")
        if package_name is None:
            raise errors.ResourceError(
                "No package_name is provided for DOFunction target"
            )
        function_name = config.get("function_name")
        if function_name is None:
            raise errors.ResourceError(
                "No function_name is provided for DOFunction target"
            )
        with open(os.path.join(project_dir, "project.yml"), "r") as f:
            project_yaml = yaml.safe_load(f)
        if not self.__verify_function(package_name, function_name, project_yaml):
            raise errors.ResourceError(
                f"No package with name {package_name} and fuction with {function_name} found in {os.path.join(project_dir, 'project.yml')}"
            )
        function_index = f"{package_name}/{function_name}"
        label = self.spec.get("label")
        if label is None:
            raise errors.ResourceError("No label found in DOFunction target specs")
        namespaces_list_command = "doctl serverless namespaces list -ojson"
        namespace_id = None
        try:
            p = resources.Resource.execute(namespaces_list_command, project_dir)
            namespaces = p.stdout.decode("UTF-8")
            namespaces_list = json.loads(namespaces)
            for namespace in namespaces_list:
                if namespace.get("label") == label:
                    namespace_id = namespace.get("namespace")
        except CalledProcessError as e:
            raise errors.ResourceError(e.stdout.decode("UTF-8"))
        if namespace_id is None:
            create_namespace_command = (
                f"doctl serverless namespaces create --label {label} --region {region}"
            )
            try:
                p = resources.Resource.execute(create_namespace_command, project_dir)
                namespace_id = p.stdout.decode("UTF-8").split(" ")[4]
            except CalledProcessError as e:
                raise errors.ResourceError(
                    f"Error creating namespace in DO: {e.stderr.decode('UTF-8')}"
                )
        try:
            resources.Resource.execute(
                f"doctl serverless connect {namespace_id}", project_dir
            )
        except CalledProcessError as e:
            raise errors.ResourceError(
                f"Error connecting to namespace: {e.stderr.decode('UTF-8')}"
            )
        deploy_command = f"doctl serverless deploy . -ojson"
        try:
            resources.Resource.execute(deploy_command, config.get("project_dir"))
        except CalledProcessError as e:
            raise errors.ResourceError(e.stdout.decode("UTF-8"))
        try:
            p = resources.Resource.execute(
                f"doctl sls fn get {function_index} --url", project_dir
            )
            return p.stdout.decode("UTF-8")
        except CalledProcessError as e:
            raise errors.ResourceError(
                f"Error when getting function URL: {function_index}, {e.stderr.decode('UTF-8')}"
            )


def get_plugin_manager():
    """
    Return the plugin manager for hash-targets plugins.
    """
    pm = pluggy.PluginManager("hash-targets")
    pm.add_hookspecs(TargetSpec)
    pm.load_setuptools_entrypoints("hash-targets")
    pm.register(FakeTarget(), "FakeTarget")
    pm.register(K8STarget(), "K8STarget")
    pm.register(DockerRegistryTarget(), "DockerRegistryTarget")
    pm.register(DOFunctionTarget(), "DOFunctionTarget")
    return pm


def get_target(target, args, space):
    """
    Docs Return a target by its name

    Args:
        target (str): The name of the target to return.
        args (dict): A dictionary which contains the config for this target

    Return:
        object: The target object, which can be used to run actions
    """
    pm = get_plugin_manager()
    plugins = pm.list_name_plugin()
    for plugin in plugins:
        if target == plugin[0]:
            hash_target = plugin[1]
            hash_target.init(args, space)
            return hash_target
