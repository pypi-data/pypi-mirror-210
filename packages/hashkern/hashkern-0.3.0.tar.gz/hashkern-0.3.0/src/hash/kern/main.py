"""
The main kern module, it has the main_action method which runs an action x on resource y in environment z
"""

from hash import errors
import os
import graphviz
from hash import kern
from hash.kern.execute import Execute
from hash.kern.planner import Planner
from hash.resources.base import get_resource, ResourceSpace


def main_action(
    resource_file: str,
    action_name: str,
    env_name: str,
    base_path: str,
    store,
    plan_file=None,
):
    if os.path.isdir(resource_file):
        resource_file = os.path.join(resource_file, "resource.yaml")
    if not os.path.exists(resource_file):
        raise errors.ResourceError(f"File not found {resource_file}")
    resource = get_resource(resource_file)
    if resource is None:
        raise errors.ResourceError(f"Resource at {resource_file} is not recognized")
    rs = ResourceSpace(base_path, store)
    if env_name is None:
        env = None
    else:
        env = rs.find_resource_by_id(f"Env:{env_name}")
        if env is None:
            raise errors.ResourceError(f"No env with name {env_name}")
    h = rs.calculate_hash(resource)
    st = store.get(resource.getId(), h)
    pl = Planner(store, base_path)
    pl.plan(action_name, resource, env, st.get_imdict())
    if plan_file is not None:
        edges = pl.getGraph().getEdges()
        dot = graphviz.Digraph(
            f"Plan to run {action_name} on {resource.getId()} in {env_name}"
        )
        for edge in edges:
            node1_key = " ".join(edge.node1.getKey().split(":")[0:4])
            node2_key = " ".join(edge.node2.getKey().split(":")[0:4])
            dot.edge(node1_key, node2_key)
        with open(plan_file, "w") as f:
            f.write(dot.source)
        print(f"Plan saved to {plan_file}")
        return
    deps = pl.get__deps()
    ex = Execute(rs, store, "SerialExecutor", pl.get_states())
    try:
        ex.execute(pl.getGraph(), deps)
    except Exception as e:
        raise e
    finally:
        store.persist_states()
        for ac in kern.all_actions:
            artifacts = st.get_artifacts(ac, env_name).get(ac, [])
            for artifact in artifacts:
                if artifact.getKind() == "file":
                    try:
                        os.remove(artifact.getData())
                    except Exception:
                        pass
        for _, state in pl.get_states().items():
            for ac in kern.all_actions:
                res = rs.find_resource_by_id(state.get_resource_id())
                if res:
                    env_name_res = res.getMetadata("env")
                    if env_name_res:
                        artifacts = state.get_artifacts(ac, env_name_res).get(ac, [])
                    else:
                        artifacts = state.get_artifacts(ac, env_name).get(ac, [])
                else:
                    artifacts = state.get_artifacts(ac, env_name).get(ac, [])
                for artifact in artifacts:
                    if artifact.getKind() == "file":
                        try:
                            os.remove(artifact.getData())
                        except Exception:
                            pass

    return ex.get_steps()
