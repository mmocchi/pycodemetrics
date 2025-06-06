"""Tests for config_manager module."""

import tempfile
from pathlib import Path

import pytest
import toml

from pycodemetrics.config.config_manager import (
    EXCLUDE_PATTERN_DEFAULT,
    TESTCODE_PATTERN_DEFAULT,
    USER_GROUPS_DEFAULT,
    ConfigManager,
    UserGroupConfig,
)


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def test_get_testcode_type_patterns_with_valid_config(self):
        """Test get_testcode_type_patterns with valid config file."""
        config_data = {
            "tool": {
                "pycodemetrics": {
                    "groups": {"testcode": {"pattern": ["custom/tests/*", "spec/*"]}}
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            patterns = ConfigManager.get_testcode_type_patterns(config_path)
            assert patterns == ["custom/tests/*", "spec/*"]
        finally:
            config_path.unlink()

    def test_get_testcode_type_patterns_with_nonexistent_config(self):
        """Test get_testcode_type_patterns with non-existent config file."""
        non_existent_path = Path("/tmp/non_existent_config.toml")
        patterns = ConfigManager.get_testcode_type_patterns(non_existent_path)
        assert patterns == TESTCODE_PATTERN_DEFAULT

    def test_get_testcode_type_patterns_with_missing_key(self):
        """Test get_testcode_type_patterns with config missing the testcode key."""
        config_data = {"tool": {"pycodemetrics": {"groups": {}}}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            patterns = ConfigManager.get_testcode_type_patterns(config_path)
            assert patterns == TESTCODE_PATTERN_DEFAULT
        finally:
            config_path.unlink()

    def test_get_user_groups_with_valid_config(self):
        """Test get_user_groups with valid config file."""
        config_data = {
            "tool": {
                "pycodemetrics": {
                    "groups": {
                        "user": {
                            "frontend": ["src/frontend/*", "web/*"],
                            "backend": ["src/backend/*", "api/*"],
                        }
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            user_groups = ConfigManager.get_user_groups(config_path)
            assert len(user_groups) == 2

            frontend_group = next(g for g in user_groups if g.name == "frontend")
            assert frontend_group.patterns == ["src/frontend/*", "web/*"]

            backend_group = next(g for g in user_groups if g.name == "backend")
            assert backend_group.patterns == ["src/backend/*", "api/*"]
        finally:
            config_path.unlink()

    def test_get_user_groups_with_nonexistent_config(self):
        """Test get_user_groups with non-existent config file."""
        non_existent_path = Path("/tmp/non_existent_config.toml")
        user_groups = ConfigManager.get_user_groups(non_existent_path)
        assert user_groups == USER_GROUPS_DEFAULT

    def test_get_user_groups_with_missing_key(self):
        """Test get_user_groups with config missing the user groups key."""
        config_data = {"tool": {"pycodemetrics": {"groups": {}}}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            user_groups = ConfigManager.get_user_groups(config_path)
            assert user_groups == USER_GROUPS_DEFAULT
        finally:
            config_path.unlink()

    def test_get_exclude_patterns_with_valid_config(self):
        """Test get_exclude_patterns with valid config file."""
        config_data = {
            "tool": {
                "pycodemetrics": {
                    "exclude": {"pattern": ["custom_exclude/*", "temp/*", ".custom"]}
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            patterns = ConfigManager.get_exclude_patterns(config_path)
            assert patterns == ["custom_exclude/*", "temp/*", ".custom"]
        finally:
            config_path.unlink()

    def test_get_exclude_patterns_with_nonexistent_config(self):
        """Test get_exclude_patterns with non-existent config file."""
        non_existent_path = Path("/tmp/non_existent_config.toml")
        patterns = ConfigManager.get_exclude_patterns(non_existent_path)
        assert patterns == EXCLUDE_PATTERN_DEFAULT

    def test_get_exclude_patterns_with_missing_key(self):
        """Test get_exclude_patterns with config missing the exclude key."""
        config_data = {"tool": {"pycodemetrics": {}}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            patterns = ConfigManager.get_exclude_patterns(config_path)
            assert patterns == EXCLUDE_PATTERN_DEFAULT
        finally:
            config_path.unlink()

    def test_get_exclude_patterns_default_values(self):
        """Test that EXCLUDE_PATTERN_DEFAULT contains expected patterns."""
        assert "__pycache__" in EXCLUDE_PATTERN_DEFAULT
        assert ".git" in EXCLUDE_PATTERN_DEFAULT
        assert ".venv" in EXCLUDE_PATTERN_DEFAULT
        assert "venv" in EXCLUDE_PATTERN_DEFAULT
        assert "env" in EXCLUDE_PATTERN_DEFAULT
        assert "ENV" in EXCLUDE_PATTERN_DEFAULT
        assert ".env" in EXCLUDE_PATTERN_DEFAULT
        assert "node_modules" in EXCLUDE_PATTERN_DEFAULT
        assert ".pytest_cache" in EXCLUDE_PATTERN_DEFAULT
        assert "site-packages" in EXCLUDE_PATTERN_DEFAULT
        assert "dist" in EXCLUDE_PATTERN_DEFAULT
        assert "build" in EXCLUDE_PATTERN_DEFAULT
        assert ".tox" in EXCLUDE_PATTERN_DEFAULT


class TestUserGroupConfig:
    """Test cases for UserGroupConfig class."""

    def test_user_group_config_creation(self):
        """Test UserGroupConfig creation with valid data."""
        config = UserGroupConfig(name="test_group", patterns=["src/test/*", "tests/*"])
        assert config.name == "test_group"
        assert config.patterns == ["src/test/*", "tests/*"]

    def test_user_group_config_forbid_extra_fields(self):
        """Test that UserGroupConfig forbids extra fields."""
        with pytest.raises(ValueError):
            UserGroupConfig(
                name="test_group", patterns=["src/test/*"], extra_field="not_allowed"
            )
