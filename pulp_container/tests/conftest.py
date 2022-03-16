import pytest

from urllib.parse import urlparse
from pulp_smash.cli import RegistryClient
from pulpcore.client.pulp_container import (
    ApiClient,
    PulpContainerNamespacesApi,
    RemotesContainerApi,
    RepositoriesContainerApi,
    RepositoriesContainerPushApi,
    RepositoriesContainerVersionsApi,
    RepositoriesContainerPushVersionsApi,
    DistributionsContainerApi,
    ContentTagsApi,
    ContentManifestsApi,
    ContentBlobsApi,
)


@pytest.fixture(scope="session")
def registry_client(pulp_cfg):
    """Fixture for a container registry client."""
    registry = RegistryClient(pulp_cfg)
    try:
        registry.raise_if_unsupported(ValueError, "Tests require podman/docker")
    except ValueError:
        pytest.Skip("Tests require podman/docker")

    return registry


@pytest.fixture()
def local_registry(request, _local_registry):
    """Local registry with authentication."""

    # This check only works, if the fixture is scoped to the test
    if request.node.get_closest_marker("parallel") is not None:
        raise pytest.UsageError("This test is not suitable to be marked parallel.")

    return _local_registry


@pytest.fixture(scope="session")
def _local_registry(pulp_cfg, bindings_cfg, registry_client):
    """Local registry with authentication. Session scoped."""

    registry_name = urlparse(pulp_cfg.get_base_url()).netloc

    class _LocalRegistry:
        @staticmethod
        def _dispatch_command(*args):
            if bindings_cfg.username is not None:
                registry_client.login(
                    "-u", bindings_cfg.username, "-p", bindings_cfg.password, registry_name
                )
            else:
                registry_client.logout(registry_name)
            try:
                registry_client._dispatch_command(*args)
            finally:
                registry_client.logout(registry_name)

        @staticmethod
        def pull(image_path):
            if bindings_cfg.username is not None:
                registry_client.login(
                    "-u", bindings_cfg.username, "-p", bindings_cfg.password, registry_name
                )
            else:
                registry_client.logout(registry_name)
            try:
                registry_client.pull("/".join([registry_name, image_path]))
            finally:
                registry_client.logout(registry_name)

        @staticmethod
        def tag_and_push(image_path, local_url):
            local_image_path = "/".join([registry_name, local_url])
            registry_client.tag(image_path, local_image_path)
            if bindings_cfg.username is not None:
                registry_client.login(
                    "-u", bindings_cfg.username, "-p", bindings_cfg.password, registry_name
                )
            else:
                registry_client.logout(registry_name)
            try:
                registry_client.push(local_image_path)
            finally:
                # Untag local copy
                registry_client.rmi(local_image_path)
                registry_client.logout(registry_name)

    return _LocalRegistry()


@pytest.fixture(scope="session")
def container_client(bindings_cfg):
    """Fixture for container_client."""
    return ApiClient(bindings_cfg)


@pytest.fixture(scope="session")
def container_namespace_api(container_client):
    """Container namespace API fixture."""
    return PulpContainerNamespacesApi(container_client)


@pytest.fixture(scope="session")
def container_remote_api(container_client):
    """Container remote API fixture."""
    return RemotesContainerApi(container_client)


@pytest.fixture(scope="session")
def container_repository_api(container_client):
    """Container repository API fixture."""
    return RepositoriesContainerApi(container_client)


@pytest.fixture(scope="session")
def container_repository_version_api(container_client):
    """Container repository version API fixture."""
    return RepositoriesContainerVersionsApi(container_client)


@pytest.fixture(scope="session")
def container_push_repository_api(container_client):
    """Container push repository API fixture."""
    return RepositoriesContainerPushApi(container_client)


@pytest.fixture(scope="session")
def container_push_repository_version_api(container_client):
    """Container repository version API fixture."""
    return RepositoriesContainerPushVersionsApi(container_client)


@pytest.fixture(scope="session")
def container_distribution_api(container_client):
    """Container distribution API fixture."""
    return DistributionsContainerApi(container_client)


@pytest.fixture(scope="session")
def container_tag_api(container_client):
    """Container tag API fixture."""
    return ContentTagsApi(container_client)


@pytest.fixture(scope="session")
def container_manifest_api(container_client):
    """Container manifest API fixture."""
    return ContentManifestsApi(container_client)


@pytest.fixture(scope="session")
def container_blob_api(container_client):
    """Container blob API fixture."""
    return ContentBlobsApi(container_client)
