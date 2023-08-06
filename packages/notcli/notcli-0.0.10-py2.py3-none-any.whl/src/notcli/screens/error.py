from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Label, Button


class ErrorScreen(ModalScreen[None]):
    """Screen with an error message."""

    BINDINGS = [
        Binding("escape,q", "error_dismiss", "Dismiss", show=False),
    ]

    def __init__(
        self, line_no: Optional[int], line: Optional[str], message: str, **kwargs
    ):
        super().__init__(**kwargs)
        self.line_no = line_no
        self.line = line
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            if not self.line_no or not self.line:
                yield Label(self.message, id="error_message")
            else:
                yield Label(self.message, id="error_message")
                yield Label(f"Line {self.line_no}: {self.line}", id="error_line")
            with Horizontal(id="buttons"):
                yield Button("OK", variant="error", id="ok")

    def action_error_dismiss(self) -> None:
        self.dismiss()
