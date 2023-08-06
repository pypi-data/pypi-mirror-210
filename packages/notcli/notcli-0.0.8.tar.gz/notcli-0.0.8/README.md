# NotCLI - An Interactive TUI Application

`notcli` is a Textual User Interface (TUI) application designed to streamline your command line tasks with easy-to-use shortcuts. The application leverages the power of Python's `argparse` and `rich` libraries to provide an intuitive interface, and the `textual` library for an interactive user experience.

## Features

- **Interactive Textual-based User Interface**: Enjoy the power of command-line interfaces with the usability and aesthetics of a GUI.
- **Load Variables from a File**: Manage your environment variables with ease. Load variables from a file and export them to the environment.
- **Error Handling and Display**: When something goes wrong, `notcli` provides meaningful error messages through customizable error screens.
- **Shortcut Bindings**: Make your tasks quicker with shortcut bindings, enabling fast access to your favorite commands.
- **Extendable**: The design of `notcli` is such that more features and shortcuts can be added in the future to cater to a wide range of use-cases.

## Installation

You can install `notcli` using pip:

```shell
pip install notcli
```

## Usage

`notcli` is designed to bring simplicity and efficiency to your command line tasks. To use `notcli`, simply call it from the command line followed by the appropriate command:

```shell
notcli loadvars
```

This command will launch the Textual interface, providing you with an interactive session where you can select the file that contains your environment variables. Once the file is selected, `notcli` will load these variables into your environment.

If `notcli` encounters an error, such as an issue reading the file or loading the variables, it will bring up an error screen with the details of the error. This allows you to quickly understand what went wrong and how to fix it.

The `loadvars` command is just one of the features `notcli` provides. As the application grows, more commands and shortcuts will be added. For a list of currently available commands, simply run `notcli` without any command:

```shell
notcli
```

This will display a list of commands along with a brief description of what each command does.

| Command    | Description                                                     |
|------------|-----------------------------------------------------------------|
| `loadvars` | Loads variables from a file and exports them to the environment |
| `help`     | Displays a list of available commands and their descriptions    |
| `version`  | Displays the version of `notcli`                                |


## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.