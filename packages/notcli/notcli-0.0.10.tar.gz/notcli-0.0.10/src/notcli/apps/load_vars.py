import os
import subprocess
from typing import Union, Optional

from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import DirectoryTree, Footer, Header, Static
from rich.traceback import Traceback

from src.notcli.conf.settings import TTY_ECHO_PATH, STATIC_DIR
from src.notcli.screens.error import ErrorScreen


class LoadVars(App):
    CSS_PATH = f"{STATIC_DIR}/demo.css"
    TITLE = "Textual Demo"
    BINDINGS = [
        ("f1", "app.toggle_class('TextLog', '-hidden')", "Notes"),
        Binding("ctrl+c,ctrl+q", "app.quit", "Quit", show=True),
    ]
    file_path: reactive[str] = reactive("")
    variables: reactive[dict] = reactive({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code_view = Static(expand=True)

    def add_note(self, renderable: RenderableType) -> None:
        pass
        # self.query_one(TextLog).write(renderable)

    def on_mount(self) -> None:
        self.add_note("Textual Demo app is running")
        self.query_one(DirectoryTree).focus()

    def compose(self) -> ComposeResult:
        yield Container(
            Header(show_clock=False),
            # TextLog(classes="-hidden", wrap=False, highlight=True, markup=True),
            DirectoryTree("./", id="tree-view"),
            self.code_view,
        )
        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        event.stop()
        code_view = self.code_view
        try:
            self.sub_title = reactive(str(event.path))
        except Exception as e:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = reactive(str(e))
        else:
            self.query_one("#tree-view").scroll_home(animate=False)
            self.sub_title = reactive(str(event.path))

        self.validate_and_read_file(str(event.path))

    def validate_and_read_file(self, path: str) -> Union[None, str]:
        # self.add_note(f"Validating {path}")
        validated_path = os.path.abspath(path)
        if not os.path.exists(validated_path):
            return self.action_error(
                line_no=None, line=None, message=f"{validated_path} does not exist"
            )
        if not os.path.isfile(validated_path):
            return self.action_error(line_no=None, line=None, message="Not a file")
        if not os.access(validated_path, os.R_OK):
            return self.action_error(
                line_no=None, line=None, message="File is not readable"
            )

        # Check if file matches format VARS=VALUE
        with open(validated_path, "r") as f:
            # Check file format is correct and read variables
            self.add_note(f"Reading {validated_path}")
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                if "=" not in line:
                    return self.action_error(line_no, line, "Invalid format")
                var, value = line.split("=", 1)
                # Check that variable name is valid and value doesn't have leading/trailing spaces
                if not var.isidentifier() or value.strip() != value:
                    return self.action_error(line_no, line, "Invalid variable or value")
                self.variables[var] = value
                self.add_note(f"Found variable {var} with value {value}")
        self.export_variables()

    def action_error(
        self, line_no: Optional[int], line: Optional[str], message: str
    ) -> None:
        """Action to display the error dialog."""
        self.push_screen(ErrorScreen(line_no, line, message))

    @staticmethod
    def get_tty():
        try:
            result = subprocess.run(
                ["tty"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            result.check_returncode()
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to get current terminal: {e.stderr.decode().strip()}"
            )

    @staticmethod
    def build_command(commands):
        if not commands:
            raise ValueError("No commands to run")
        return ";".join(commands)

    def export_variables(self) -> None:
        self.add_note("Exporting variables to environment")
        commands_to_run = [
            f"export {var}={value}" for var, value in self.variables.items()
        ]
        if commands_to_run:
            self.add_note("Running commands")
            try:
                tty = self.get_tty()
                command_str = self.build_command(commands_to_run) + "; clear"
                sleep_and_run = (
                    f"sleep 0.3 && {TTY_ECHO_PATH}/ttyecho -n {tty} '{command_str}'"
                )
                subprocess.Popen(sleep_and_run, shell=True)
            except Exception as e:
                self.add_note(f"Failed to export variables: {str(e)}")
            else:
                self.app.exit()
        else:
            subprocess.Popen("clear", shell=True)
