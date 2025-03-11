import sys, shutil, subprocess, os
import readline

def tokenize(cmd):
    # split into tokens
    tokens = []
    token = []
    i = 0
    in_quotes = None  # none=outside, '"'=in double quotes, "'"=in single quotes
    
    while i < len(cmd):
        char = cmd[i]
        
        # backslash
        if char == '\\':
            if i + 1 < len(cmd): 
                # in quotes, only escape quotes and backslashes
                if in_quotes and cmd[i + 1] not in [in_quotes, '\\']:
                    token.append(char)  
                    token.append(cmd[i + 1])  
                else:
                    token.append(cmd[i + 1]) 
                i += 2
                continue
            else:  # backslash at end of string
                token.append(char)
                i += 1
                continue
            
        # quotes
        if char in '"\'':
            if in_quotes == char:  # closing
                in_quotes = None
            elif not in_quotes:  # opening
                in_quotes = char
            else:
                token.append(char)
            i += 1
            continue
            
        # spaces
        if char.isspace() and not in_quotes:
            if token:  # end current token
                tokens.append(''.join(token))
                token = []
            i += 1
            continue
            
        # character
        token.append(char)
        i += 1
    
    # add final token if exists
    if token:
        tokens.append(''.join(token))
        
    return tokens


def main():
    # shell built ins 
    def _exit(args): sys.exit(int(args[0]) if args else 0)
    def _echo(args): sys.stdout.write(' '.join(args) + '\n')
    def _pwd(*_): sys.stdout.write(os.getcwd() + '\n')
    
    def _cd(args):
        try:
            os.chdir(os.path.expanduser(args[0]) if args else os.path.expanduser("~"))
        except:
            sys.stderr.write(f"cd: {args[0] if args else '~'}: No such file or directory\n")
            
    def _type(args):
        if not args:
            sys.stderr.write("type: missing argument\n")
            return
        cmd = args[0]
        if cmd in builtins:
            sys.stdout.write(f"{cmd} is a shell builtin\n")
        elif path := shutil.which(cmd):
            sys.stdout.write(f"{cmd} is {path}\n")
        else:
            sys.stderr.write(f"{cmd}: not found\n")
    
    def _ls(args):
        # list files and directories in specified directory
        try:
            # if no args, use current directory, otherwise use the specified path
            path = os.path.expanduser(args[0]) if args else '.'
            
            # get all entries in the directory
            entries = os.listdir(path)
            entries.sort()
            
            # print each entry on a new line
            for entry in entries:
                sys.stdout.write(f"{entry}\n")
                
        except FileNotFoundError:
            sys.stderr.write(f"ls: {args[0] if args else '.'}: No such file or directory\n")
        except PermissionError:
            sys.stderr.write(f"ls: {args[0] if args else '.'}: Permission denied\n")
        except Exception as e:
            sys.stderr.write(f"ls: {e}\n")
    
    def _touch(args):
        # create an empty file or update the access and modification times of an existing file
        if not args:
            sys.stderr.write("touch: missing file operand\n")
            return
        
        for filename in args:
            try:
                # expand user directory if needed (e.g., ~/)
                expanded_filename = os.path.expanduser(filename)
                
                # create directory if it doesn't exist
                directory = os.path.dirname(expanded_filename)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                
                # open the file in append mode 
                with open(expanded_filename, 'a'):
                    # update the file's access and modification times to current time
                    os.utime(expanded_filename, None)
                    
            except PermissionError:
                sys.stderr.write(f"touch: cannot touch '{filename}': Permission denied\n")
            except Exception as e:
                sys.stderr.write(f"touch: {filename}: {e}\n")
    
    def _mv(args):
        # move/rename files
        if len(args) < 2:
            sys.stderr.write("mv: missing file operand\n")
            return
        
        source = os.path.expanduser(args[0])
        destination = os.path.expanduser(args[1])
        
        try:
            # move file or dir
            directory = os.path.dirname(destination)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            shutil.move(source, destination)
        except FileNotFoundError:
            sys.stderr.write(f"mv: cannot stat '{source}': No such file or directory\n")
        except PermissionError:
            sys.stderr.write(f"mv: cannot move '{source}': Permission denied\n")
        except Exception as e:
            sys.stderr.write(f"mv: {e}\n")
    
    def _help(args):
        # help function
        if not args:
            # list all commands
            sys.stdout.write("Available commands:\n")
            for cmd in sorted(builtins.keys()):
                sys.stdout.write(f"  {cmd}\n")
        else:
            # show help for specific command
            cmd = args[0]
            if cmd in help_text:
                sys.stdout.write(help_text[cmd])
            elif cmd in builtins:
                sys.stdout.write(f"Help for '{cmd}' not available.\n")
            else:
                sys.stderr.write(f"help: '{cmd}' is not a shell command\n")
    
    # help text for commands
    help_text = {
        "exit": "exit [n] - Exit the shell with optional status n\n",
        "echo": "echo [string...] - Display a line of text\n",
        "type": "type [name] - Display information about command type\n",
        "pwd": "pwd - Print current working directory\n",
        "cd": "cd [dir] - Change the current directory to dir\n",
        "ls": "ls [dir] - List directory contents\n",
        "touch": "touch [file...] - Create empty file(s) or update timestamps\n",
        "mv": "mv source dest - Move/rename source to destination\n",
        "help": "help [command] - Display help for commands\n"
    }
    
    # cmd to func mapping
    builtins = {
        "exit": _exit,
        "echo": _echo,
        "type": _type,
        "pwd": _pwd,
        "cd": _cd,
        "ls": _ls,
        "touch": _touch,
        "mv": _mv,
        "help": _help
    }

    # tab completion variables
    completion_matches = []
    last_text = None
    tab_count = 0

    def get_executables(prefix):
        # all matching executables from PATH
        matches = []
        paths = os.environ.get('PATH', '').split(os.pathsep)
        for path in paths:
            if not os.path.isdir(path):
                continue
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if (entry.startswith(prefix) and 
                    os.path.isfile(full_path) and 
                    os.access(full_path, os.X_OK)):
                    matches.append(entry)
        return matches
    
    def find_longest_common_prefix(strings):
        # longest common prefix 
        if not strings:
            return ""
        
        prefix = strings[0]
        for s in strings[1:]:
            i = 0
            while i < len(prefix) and i < len(s) and prefix[i] == s[i]:
                i += 1
            prefix = prefix[:i]
            if not prefix:
                break
        
        return prefix

    def completer(text, state):
        # completion handler for readline
        nonlocal completion_matches, last_text, tab_count
        
        # update if text changes
        if text != last_text:
            last_text = text
            tab_count = 0
            
            # all matches
            builtin_matches = [cmd for cmd in builtins if cmd.startswith(text)]
            executable_matches = get_executables(text)
            completion_matches = sorted(set(builtin_matches + executable_matches))
        
        # no matches = ring bell
        if not completion_matches:
            if state == 0:
                sys.stdout.write('\a')  # bell character
                sys.stdout.flush()
            return None
        
        # single match = complete 
        if len(completion_matches) == 1:
            return completion_matches[0] + ' ' if state == 0 else None
        
        # find the longest common prefix for multiple matches
        if state == 0:
            common_prefix = find_longest_common_prefix(completion_matches)
            
            # if common prefix is longer than the current text, return 
            if len(common_prefix) > len(text):
                return common_prefix
            
            # first tab press = ring bell
            if tab_count == 0:
                tab_count += 1
                sys.stdout.write('\a')  
                sys.stdout.flush()
                return None
            
            # second tab press = display matches
            elif tab_count == 1:
                tab_count = 0
                sys.stdout.write('\n')
                sys.stdout.write('  '.join(completion_matches))
                sys.stdout.write('\n$ ' + text)
                sys.stdout.flush()
                return None
        
        # return the match at the specified state index
        if state < len(completion_matches):
            return completion_matches[state] + ' '
        else:
            return None

    def ensure_directory_exists(file_path):
        # ensure directory exists, create if necessary
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                sys.stderr.write(f"cannot create directory '{directory}': {e}\n")
                return False
        return True

    def process_command_with_redirection(tokens):
        # process command with possible redirection
        stdout_redirect_index = -1
        stderr_redirect_index = -1
        
        # find redirection operators
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # check for append redirection (>>)
            if token == '>>' or token == '1>>':
                stdout_redirect_index = i
                append_mode = True
            # check for standard redirection (>)
            elif token == '>' or token == '1>':
                stdout_redirect_index = i
                append_mode = False
            # check for error redirection
            elif token == '2>':
                stderr_redirect_index = i
            # check for error append redirection (2>>)
            elif token == '2>>':
                stderr_redirect_index = i
                append_mode = True
                
            i += 1
        
        # extract command and initial args 
        first_redirect = min(x for x in [stdout_redirect_index, stderr_redirect_index] if x >= 0) if \
                        (stdout_redirect_index >= 0 or stderr_redirect_index >= 0) else len(tokens)
        
        command, args = tokens[0], tokens[1:first_redirect]
        
        # setup redirection files
        stdout_file = None
        stderr_file = None
        
        # check for stdout redirection
        if stdout_redirect_index >= 0:
            if stdout_redirect_index == len(tokens) - 1:
                sys.stderr.write("syntax error: no file specified for output redirection\n")
                return
            stdout_path = tokens[stdout_redirect_index + 1]
            if not ensure_directory_exists(stdout_path):
                return
            
            # open in append mode if >> was used
            stdout_mode = 'a' if tokens[stdout_redirect_index] in ['>>', '1>>'] else 'w'
            try:
                stdout_file = open(stdout_path, stdout_mode)
            except IOError as e:
                sys.stderr.write(f"error opening '{stdout_path}' for writing: {e}\n")
                return
        
        # check for stderr redirection
        if stderr_redirect_index >= 0:
            if stderr_redirect_index == len(tokens) - 1:
                sys.stderr.write("syntax error: no file specified for error redirection\n")
                if stdout_file:
                    stdout_file.close()
                return
            stderr_path = tokens[stderr_redirect_index + 1]
            if not ensure_directory_exists(stderr_path):
                if stdout_file:
                    stdout_file.close()
                return
            
            # open in append mode if 2>> was used
            stderr_mode = 'a' if tokens[stderr_redirect_index] == '2>>' else 'w'
            try:
                stderr_file = open(stderr_path, stderr_mode)
            except IOError as e:
                sys.stderr.write(f"error opening '{stderr_path}' for writing: {e}\n")
                if stdout_file:
                    stdout_file.close()
                return
        
        # execute command with redirections
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            if stdout_file:
                sys.stdout = stdout_file
            if stderr_file:
                sys.stderr = stderr_file
                
            execute_command(command, args)
            
        finally:
            # restore original streams
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
            # close file handles
            if stdout_file:
                stdout_file.close()
            if stderr_file:
                stderr_file.close()

    def execute_command(command, args):
        # execute command with arguments
        if command in builtins:
            builtins[command](args)
        elif shutil.which(command):
            # run with stdin connected to terminal for interactive programs
            try:
                proc = subprocess.Popen([command] + args,
                                    stdin=sys.stdin,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
                
                stdout, stderr = proc.communicate()
                
                if stdout:
                    sys.stdout.write(stdout)
                if stderr:
                    sys.stderr.write(stderr)
                    
                sys.stdout.flush()
                sys.stderr.flush()
            except Exception as e:
                sys.stderr.write(f"error running {command}: {e}\n")
        else:
            sys.stderr.write(f"{command}: command not found\n")

    # setup custom readline behavior
    class Completer:
        def __init__(self):
            self.matches = []
            self.last_text = None
            self.tab_count = 0
            
        def complete(self, text, state):
            # wrapper for completer to handle state management
            return completer(text, state)
    
    # set up readline
    readline.set_completer(Completer().complete)
    readline.parse_and_bind('tab: complete')
    
    # prevent backspace from erasing prompt
    readline.set_pre_input_hook(lambda: None)  # ensure hook is initialized

    # main shell repl
    while True:
        prompt = "$ "
        sys.stdout.write(prompt)
        sys.stdout.flush()
        
        try:
            # configure readline to respect prompt boundary
            readline.set_startup_hook(lambda: readline.insert_text(""))
            
            # read input using input() which respects readline settings
            cmd = input()
            
            # clear the startup hook
            readline.set_startup_hook(None)
            
            tokens = tokenize(cmd)
            if not tokens: continue
            
            # handle command with possible redirection
            process_command_with_redirection(tokens)
                
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        except Exception as e:
            sys.stderr.write(f"error: {e}\n")

if __name__ == "__main__":
    main()
