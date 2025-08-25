# SimpleShell

A lightweight, pure Python implementation of a Unix-like shell with essential built-in commands and features.
This was built following the CodeCrafters [Build your own Shell](https://app.codecrafters.io/courses/shell/overview) Course.

![image](https://github.com/user-attachments/assets/6b2eabbb-2940-4a4a-97dd-ebc772765835)

## Features

- Core shell functionality with command execution
- Built-in commands: `cd`, `pwd`, `echo`, `exit`, `ls`, `touch`, `mv`, `type`, `help`
- Tab completion for commands
- Command history navigation
- I/O redirection (`>`, `>>`, `2>`, `2>>`)
- Support for interactive programs that request user input
- Proper handling of quotes and escape characters

## Installation

Simply download the script and run it with Python 3:

```bash
git clone https://github.com/Pixelrick420/Shell.git
cd Shell
pip install pyreadline3 #this becomes readline on linux/macOs
python3 shell.py
```

## Usage

Once running, you'll see a prompt:

```
$
```

You can now enter commands like you would in a regular shell:

```
$ ls
$ pwd
$ cd ~/Documents
$ touch test.txt
$ echo "Hello World" > test.txt
$ mv test.txt newname.txt
$ help
```

### Built-in Commands

- `cd [dir]` - Change directory
- `pwd` - Print working directory
- `echo [text]` - Display text
- `exit [code]` - Exit the shell with optional status code
- `ls [dir]` - List directory contents
- `touch [file]` - Create empty file or update timestamp
- `mv source dest` - Move/rename files
- `type [command]` - Show command type information
- `help [command]` - Display help for all commands or specific command

## Tab Completion

Press Tab to complete commands. If there are multiple possibilities:
- First Tab press: Bell sound
- Second Tab press: Display all possibilities

## I/O Redirection

The shell supports standard output and error redirection:

```
$ ls > files.txt       # Redirect stdout to files.txt
$ ls >> files.txt      # Append stdout to files.txt
$ ls 2> errors.txt     # Redirect stderr to errors.txt
$ ls 2>> errors.txt    # Append stderr to errors.txt
```

## Limitations

- No support for pipes (`|`)
- No environment variable expansion
- Limited shell scripting capabilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
