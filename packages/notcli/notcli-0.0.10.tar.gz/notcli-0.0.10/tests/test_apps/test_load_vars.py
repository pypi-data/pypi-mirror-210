import io
import subprocess

import pytest
from unittest.mock import patch, MagicMock

from src.notcli.conf.settings import TTY_ECHO_PATH
from src.notcli.main import LoadVars


# Test fixture for LoadVars instance
@pytest.fixture
def load_vars():
    return LoadVars()


# Test for validate_and_read_file when file does not exist
def test_validate_and_read_file_non_existent(load_vars):
    with patch("os.path.exists", return_value=False):
        with patch.object(load_vars, "action_error") as mock_action_error:
            load_vars.validate_and_read_file("non_existent_file")
            mock_action_error.assert_called_once()


# Test for validate_and_read_file when path is not a file
def test_validate_and_read_file_not_a_file(load_vars):
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=False):
            with patch.object(load_vars, "action_error") as mock_action_error:
                load_vars.validate_and_read_file("not_a_file")
                mock_action_error.assert_called_once()


# Test for validate_and_read_file when file is not readable
def test_validate_and_read_file_unreadable_file(load_vars):
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=True):
            with patch("os.access", return_value=False):
                with patch.object(load_vars, "action_error") as mock_action_error:
                    load_vars.validate_and_read_file("unreadable_file")
                    mock_action_error.assert_called_once()


# Test for build_command with valid commands
def test_build_command_valid_commands(load_vars):
    commands = ["command1", "command2", "command3"]
    expected_result = "command1;command2;command3"
    assert load_vars.build_command(commands) == expected_result


# Test for build_command with no commands
def test_build_command_no_commands(load_vars):
    with pytest.raises(ValueError):
        load_vars.build_command([])  # empty commands list should raise ValueError


# Test for export_variables with no variables
def test_export_variables_no_variables(load_vars):
    with patch.object(subprocess, "Popen") as mock_popen:
        load_vars.variables = {}
        load_vars.export_variables()
        mock_popen.assert_called_once_with("clear", shell=True)


# Test for validate_and_read_file with a non-existing file
def test_validate_and_read_file_nonexistent(load_vars):
    with patch("os.path.exists", return_value=False):
        result = load_vars.validate_and_read_file("nonexistent_file")
        assert result is None


# Test for validate_and_read_file with a directory
def test_validate_and_read_file_directory(load_vars):
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=False):
            result = load_vars.validate_and_read_file("directory")
            assert result is None


# Test for validate_and_read_file with an unreadable file
def test_validate_and_read_file_unreadable(load_vars):
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=True):
            with patch("os.access", return_value=False):
                result = load_vars.validate_and_read_file("unreadable_file")
                assert result is None


# Test for validate_and_read_file with a file with invalid format
def test_validate_and_read_file_invalid_format(load_vars):
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=True):
            with patch("os.access", return_value=True):
                with patch("builtins.open", return_value=io.StringIO("invalid format")):
                    result = load_vars.validate_and_read_file("invalid_format_file")
                    assert result is None


# Test for validate_and_read_file with a file with invalid variable name
def test_validate_and_read_file_invalid_variable(load_vars):
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=True):
            with patch("os.access", return_value=True):
                with patch("builtins.open", return_value=io.StringIO("123=valid")):
                    result = load_vars.validate_and_read_file("invalid_variable_file")
                    assert result is None


# Test for validate_and_read_file with a file with value having leading/trailing spaces
def test_validate_and_read_file_value_spaces(load_vars):
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=True):
            with patch("os.access", return_value=True):
                with patch("builtins.open", return_value=io.StringIO("valid= value ")):
                    result = load_vars.validate_and_read_file("value_spaces_file")
                    assert result is None


# Test for validate_and_read_file with a valid file
def test_validate_and_read_file_valid(load_vars):
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=True):
            with patch("os.access", return_value=True):
                with patch("builtins.open", return_value=io.StringIO("valid=value")):
                    with patch.object(
                        load_vars, "export_variables"
                    ) as mock_export_variables:
                        load_vars.validate_and_read_file("valid_file")
                        mock_export_variables.assert_called_once()


# Test for get_tty when tty command is successful
def test_get_tty_success(load_vars):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.check_returncode = MagicMock()
        mock_run.return_value.stdout = b"/dev/tty1"
        tty = load_vars.get_tty()
        assert tty == "/dev/tty1"


# Test for get_tty when tty command fails
def test_get_tty_failure(load_vars):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.check_returncode.side_effect = (
            subprocess.CalledProcessError(1, "tty", stderr=b"error message")
        )
        with pytest.raises(RuntimeError):
            load_vars.get_tty()


# Test for export_variables when there are variables to export and everything is successful
def test_export_variables_success(load_vars):
    with patch.object(load_vars, "get_tty", return_value="/dev/tty1"):
        with patch.object(load_vars, "build_command", return_value="export VAR=VALUE"):
            with patch("subprocess.Popen") as mock_popen:
                load_vars.variables = {"VAR": "VALUE"}
                load_vars.export_variables()
                mock_popen.assert_called_once_with(
                    f"sleep 0.3 && {TTY_ECHO_PATH}/ttyecho -n /dev/tty1 'export VAR=VALUE; clear'",
                    shell=True,
                )


# Test for export_variables when there are variables to export but an error occurs
def test_export_variables_error(load_vars):
    with patch.object(load_vars, "get_tty", return_value="/dev/tty1"):
        with patch.object(load_vars, "build_command", return_value="export VAR=VALUE"):
            with patch("subprocess.Popen", side_effect=Exception("error message")):
                with patch.object(load_vars, "add_note") as mock_add_note:
                    load_vars.variables = {"VAR": "VALUE"}
                    load_vars.export_variables()
                    mock_add_note.assert_called_with(
                        "Failed to export variables: error message"
                    )
