import argparse
import sys
from rich.console import Console
from rich.table import Table
from src.notcli.main import LoadVars


def main():
    parser = argparse.ArgumentParser(prog="notcli")
    parser.add_argument(
        "command",
        nargs="?",
        help="The command to execute",
    )
    try:
        args = parser.parse_args()
    except SystemExit:
        show_commands()
        sys.exit(1)
    except argparse.ArgumentError as exc:
        console = Console()
        console.print(f"[bold red]{exc.message}[/bold red]")
        sys.exit(1)
    else:
        if not args.command:
            show_commands()
            sys.exit(1)

    if args.command == "loadvars":
        # Call your generate function here
        LoadVars().run()
    elif args.command == "version":
        print_version()
    else:
        show_commands()


def show_commands():
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command", style="dim", width=12)
    table.add_column("Description")

    table.add_row(
        "loadvars", "Loads variables from a file and exports them to the environment"
    )
    table.add_row("help", "Shows this help message")
    table.add_row("version", "Shows the version of this program")

    console.print(table)


def print_version():
    from src.notcli import __version__

    console = Console()
    console.print(f"notcli version: [bold blue]{__version__}[/bold blue]")


if __name__ == "__main__":
    main()
