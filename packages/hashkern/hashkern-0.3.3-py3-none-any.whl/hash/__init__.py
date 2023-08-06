import pluggy

store_hookimpl = pluggy.HookimplMarker("hash-store")
resource_hookimpl = pluggy.HookimplMarker("hash-resource")
target_hookimpl = pluggy.HookimplMarker("hash-target")
secrets_hookimpl = pluggy.HookimplMarker("hash-secrets")
execute_hookimpl = pluggy.HookimplMarker("hash-execute")
