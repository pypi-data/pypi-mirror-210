"""Types to inherit from"""

import asyncio
from abc import ABCMeta
from pathlib import Path
from typing import Generic

import pytest
from cppython_core.plugin_schema.generator import GeneratorT
from cppython_core.plugin_schema.provider import ProviderT
from cppython_core.plugin_schema.scm import SCMT
from cppython_core.resolution import resolve_group, resolve_name

from pytest_cppython.shared import (
    DataPluginIntegrationTests,
    DataPluginUnitTests,
    GeneratorTests,
    PluginIntegrationTests,
    PluginUnitTests,
    ProviderTests,
    SCMTests,
)


class ProviderIntegrationTests(
    DataPluginIntegrationTests[ProviderT], ProviderTests[ProviderT], Generic[ProviderT], metaclass=ABCMeta
):
    """Base class for all provider integration tests that test plugin agnostic behavior"""

    @pytest.fixture(autouse=True, scope="session")
    def _fixture_install_dependency(self, data_plugin: ProviderT, install_path: Path) -> None:
        """Forces the download to only happen once per test session"""

        path = install_path / resolve_name(type(data_plugin))
        path.mkdir(parents=True, exist_ok=True)

        asyncio.run(data_plugin.download_tooling(path))

    def test_install(self, data_plugin: ProviderT) -> None:
        """Ensure that the vanilla install command functions

        Args:
            data_plugin: A newly constructed provider
        """
        data_plugin.install()

    def test_update(self, data_plugin: ProviderT) -> None:
        """Ensure that the vanilla update command functions

        Args:
            data_plugin: A newly constructed provider
        """
        data_plugin.update()

    def test_group_name(self, plugin_type: type[ProviderT]) -> None:
        """Verifies that the group name is the same as the plugin type

        Args:
            plugin_type: The type to register
        """
        assert resolve_group(plugin_type) == "provider"


class ProviderUnitTests(
    DataPluginUnitTests[ProviderT], ProviderTests[ProviderT], Generic[ProviderT], metaclass=ABCMeta
):
    """Custom implementations of the Provider class should inherit from this class for its tests.
    Base class for all provider unit tests that test plugin agnostic behavior
    """


class GeneratorIntegrationTests(
    DataPluginIntegrationTests[GeneratorT], GeneratorTests[GeneratorT], Generic[GeneratorT], metaclass=ABCMeta
):
    """Base class for all scm integration tests that test plugin agnostic behavior"""

    def test_group_name(self, plugin_type: type[GeneratorT]) -> None:
        """Verifies that the group name is the same as the plugin type

        Args:
            plugin_type: The type to register
        """
        assert resolve_group(plugin_type) == "generator"


class GeneratorUnitTests(
    DataPluginUnitTests[GeneratorT], GeneratorTests[GeneratorT], Generic[GeneratorT], metaclass=ABCMeta
):
    """Custom implementations of the Generator class should inherit from this class for its tests.
    Base class for all Generator unit tests that test plugin agnostic behavior"""


class SCMIntegrationTests(PluginIntegrationTests[SCMT], SCMTests[SCMT], Generic[SCMT], metaclass=ABCMeta):
    """Base class for all generator integration tests that test plugin agnostic behavior"""

    def test_group_name(self, plugin_type: type[SCMT]) -> None:
        """Verifies that the group name is the same as the plugin type

        Args:
            plugin_type: The type to register
        """
        assert resolve_group(plugin_type) == "scm"


class SCMUnitTests(PluginUnitTests[SCMT], SCMTests[SCMT], Generic[SCMT], metaclass=ABCMeta):
    """Custom implementations of the Generator class should inherit from this class for its tests.
    Base class for all Generator unit tests that test plugin agnostic behavior
    """
