from sys import exit
import os
from subprocess import run, PIPE
from argparse import ArgumentParser, Namespace

HOME_PATH: str = os.path.normpath(os.path.expanduser('~'))
USER_BASH_PROFILE_PATH: str = os.path.join(HOME_PATH, ".bash_profile")
PATH_SEP = os.pathsep
FOUND_MSG = "The given path is FOUND in PATH environment variable."
NOT_FOUND_MSG = "The given path is NOT FOUND in PATH environment variable."
BOLD_STYLE = "\033[1m"
UNDERLINE_STYLE = "\033[4m"
RED_STYLE = "\033[91m"
GREEN_STYLE = "\033[92m"
END_STYLE = "\033[0m"


def main() -> None:
    """pathvar main function

    The Logic of the entire 'pathvar' program.

    :return: Nothing, just execute the logic of the entire program.
    :rtype: None
    """

    # Get PATH
    old_path_value: str = get_path()
    if old_path_value == "__%NO_PATH%__":
        exit("Failure: Couldn't get PATH variable")

    # Create argument parser
    parser: ArgumentParser = ArgumentParser(
        description=f"This tool meant to facilitate the interaction \
                with the system's PATH environment variable (Linux BASH shell only). \
                    To get the work done correctly do the following: \
                        Read the 'help' instruction well, \n\
                        Be careful about the paths you input (with some options), \n\
                        and Separate between multiple paths with a single '{PATH_SEP}'. \
                        Copyright (c) 2023 Hussein Mahmoud Kandil - MIT."
    )
    # Add arguments to the ArgumentParser object
    add_args(parser)

    # Parse the arguments and modify the current path
    new_path: str = parse_args_and_modify_path_str(parser, old_path_value)

    # PATH modifications flag
    is_path_modified = False

    # Print information to the user
    if new_path == FOUND_MSG:
        print('\n' + BOLD_STYLE + GREEN_STYLE + new_path + END_STYLE)
        new_path = old_path_value
    elif new_path == NOT_FOUND_MSG:
        print('\n' + BOLD_STYLE + RED_STYLE + new_path + END_STYLE)
        new_path = old_path_value
    elif new_path != old_path_value:
        # Update the old PATH
        new_path = path_duplicates_eliminator(new_path)
        update_path(new_path)
        is_path_modified = True
        print_msg("Old 'PATH'", old_path_value)

    # Print the current PATH value
    print_msg("Current 'PATH'", new_path)

    # Suggest source command if the PATH IS modified and not on windows
    if is_path_modified and PATH_SEP != ';':
        print_msg("Needed Command",
                  "Run 'source ~/.bash_profile' to apply the changes to the current session.")


def get_path() -> str:
    """A simple function to get the current PATH

    Get the current PATH environment variable
    using the command meant for that 
    depending on the kind of the operating system that pathvar running on.

    :return: The value of the PATH variable
    :rtype: str
    """

    path = "__%NO_PATH%__"

    # UNIX
    if PATH_SEP == ':':
        process = run("echo $PATH", shell=True,
                      stdout=PIPE, stderr=PIPE, text=True)
        if process.stderr:
            print_msg(RED_STYLE + "STDERR", process.stderr)
            return path
        path = process.stdout.strip()

    return path


def run_command_verbosely(cmd: str) -> None:
    """Run a given command in subprocess

    Run the given command in subprocess 
    and print and 'stdout' or 'stderr'

    :param cmd: Command to run
    :type cmd: str
    """

    # Run the commands and print any stdout or stderr
    process = run(
        cmd,
        shell=True, stdout=PIPE, stderr=PIPE, text=True
    )
    if process.stdout:
        print_msg(GREEN_STYLE + "STDOUT", process.stdout)
    if process.stderr:
        print_msg(RED_STYLE + "STDERR", process.stderr)

    return None


def update_path(new_path_value: str) -> None:
    """Run a command to update the PATH variable

    Run the needed commands for updating the PATH environment variable
    based on the current operating system and print any 'stdout' or 'stderr'

    :param new_path_value: The new value in order to set the PATH variable to it
    :type new_path_value: str
    """

    # UNIX
    if PATH_SEP == ':':
        # Make sure that there is ~/.bash_profile file
        if not os.path.exists(USER_BASH_PROFILE_PATH):
            run_command_verbosely("touch " + USER_BASH_PROFILE_PATH)

        # Move the current .bash_profile into temp state
        run_command_verbosely("mv " +
                              USER_BASH_PROFILE_PATH + ' ' +
                              USER_BASH_PROFILE_PATH + "__~")

        # Program signature to use it as a boundary for our result lines
        prog_sig_start: str = "# PATHVAR *** RESULT *** START\n"
        prog_sig_end: str = "# PATHVAR *** RESULT *** END\n"

        # Add new ~/.bash_profile file and copy everything except old result
        with open(USER_BASH_PROFILE_PATH + "__~") as tmp_f:
            with open(USER_BASH_PROFILE_PATH, 'w') as f:
                # Sourcing the .bashrc & .profile if exist
                f.write(prog_sig_start)
                f.write("if [ -f ~/.bashrc ]; then\n    . ~/.bashrc\nfi\n")
                f.write('\n')
                f.write("if [ -f ~/.profile ]; then\n    . ~/.profile\nfi\n")
                f.write(prog_sig_end)
                # Flags to avoid copying our result lines again
                is_prog_seg_start: bool = False
                is_prog_seg_end: bool = False
                # copy each line except for our old result lines
                for line in tmp_f:
                    if line == prog_sig_start:
                        is_prog_seg_start = True
                        is_prog_seg_end = False
                    elif line == prog_sig_end:
                        is_prog_seg_start = False
                        is_prog_seg_end = True
                        continue
                    if not is_prog_seg_start or is_prog_seg_end:
                        f.write(line)
                # Adding the new PATH result lines
                f.write(prog_sig_start)
                f.write('export PATH="' + new_path_value + '"\n')
                f.write(prog_sig_end)

        # Delete the temp state of the ~/.bash_profile
        run_command_verbosely("rm -f " + USER_BASH_PROFILE_PATH + "__~")

    return None


def add_args(parser_obj: ArgumentParser) -> None:
    """Adding CL arguments to and ArgumentParser object

    Manipulate the inputted ArgumentParser object 
    by adding the needed command line arguments to it
    with all the specifications for each of the arguments
    (i.e. argument name, action, help, ...).

    :param parser_obj: parser object for parsing the command line arguments
    :type parser_obj: argparse.ArgumentParser
    :return: None
    :rtype: None
    """

    # Adding all needed arguments
    parser_obj.add_argument(
        "-s", "--show",
        action="store_true",
        help="shows the current value of the 'PATH' (default)"
    )
    parser_obj.add_argument(
        "-e", "--eliminate-duplicates",
        action="store_true",
        help="eliminates any duplicates in the value of the 'PATH' \
            (Included with any modifications)"
    )
    parser_obj.add_argument(
        "-a", "--append",
        metavar='',
        help=f"appends any number of paths \
            to the current value of the 'PATH' \
                (which are must be given as a single string separated with '{PATH_SEP}' \
                    between every two paths and without any spaces)"
    )
    parser_obj.add_argument(
        "-p", "--push",
        metavar='',
        help=f"pushes any number of paths at the beginning \
            of the current value of 'PATH' \
                (which are must be given as a single string separated with '{PATH_SEP}' \
                    between every two paths and without any spaces)"
    )
    parser_obj.add_argument(
        "-d", "--delete",
        metavar='',
        help=f"deletes from 'PATH' any number of paths \
            (which are must be given as a single string separated with '{PATH_SEP}' \
                between every two paths and without any spaces)"
    )
    parser_obj.add_argument(
        "-q", "--query",
        metavar='',
        help="checks whether the given path is in the current 'PATH'"
    )
    parser_obj.add_argument(
        "--remove-all-paths",
        action="store_true",
        help="removes all paths in the current 'PATH' (NOT RECOMMENDED)"
    )
    parser_obj.add_argument(
        "-v", "--version",
        action="version",
        version="pathvar 1.0.0"
    )


def parse_args_and_modify_path_str(
    parser_obj: ArgumentParser,
    current_path: str
) -> str:
    """Parsing the command line arguments

    Using 'argparse' library this function will consume an 'ArgumentParser' object
    in order to parse the arguments and handle the chosen option/s.

    :param parser_obj: parser object for parsing the command line arguments
    :type parser_obj: argparse.ArgumentParser
    :return: None
    :rtype: None
    """

    # Handle all used arguments
    args: Namespace = parser_obj.parse_args()

    if args.eliminate_duplicates:
        # Change the current path after eliminating any duplicates
        current_path = path_duplicates_eliminator(current_path)

    if args.append:
        # Append the given paths to the current path
        current_path += PATH_SEP + args.append.strip().strip(PATH_SEP).rstrip('/')

    if args.push:
        # Push the given paths at the beginning of the current path
        current_path = \
            args.push.strip().strip(PATH_SEP).rstrip('/') + PATH_SEP + current_path

    if args.delete:
        new_path = path_remover(
            current_path,
            args.delete.strip().strip(PATH_SEP).rstrip('/')
        )
        if current_path == new_path:
            return NOT_FOUND_MSG
        else:
            current_path = new_path

    if args.query:
        # Return a message to inform the user about whether the given path is in PATH.
        if is_there_path(
            current_path,
            args.query.strip().strip(PATH_SEP).rstrip('/')
        ):
            return FOUND_MSG
        return NOT_FOUND_MSG

    if args.remove_all_paths:
        print("All paths stored in the PATH environment variable WILL BE DELETED!")
        while True:
            ans: str = input(
                "Are you sure you want to continue [y|n]? "
            )
            if ans.strip().lower() in ('y', 'yes'):
                return ''
            elif ans.strip().lower() in ('n', 'no'):
                break

    # return the current_path with or without any modifications
    return current_path


def path_duplicates_eliminator(s: str) -> str:
    """Remove any duplicates in a PATH variable

    This function removes any duplicated paths from a PATH variable.
    It looks for duplicated paths.

    :param s: The value of the PATH environment variable
    :type s: str
    :return: The same input of the PATH value without any duplicates
    :rtype: str
    """

    # Split on PATH_SEP
    ss: list[str] = s.split(PATH_SEP)
    # Store only the unique paths
    temp_ss: list[str] = []

    for p in ss:
        if p not in temp_ss:
            temp_ss.append(p)

    # Return concatenated string on PATH_SEP from the final list
    return PATH_SEP.join(temp_ss)


def path_remover(current_path: str, given_paths: str) -> str:
    """Delete the given path/s from the current PATH

    return copy of the 'current_path' 
    without and value included in the 'given_paths'

    :param current_path: The value inside the PATH environment variable
    :type current_path: str
    :param given_paths: The paths that the user want it to be deleted
    :type given_paths: str
    :return: A copy from the current path without any given path
    :rtype: str
    """

    paths_to_remove: list[str] = given_paths.strip().strip(
        PATH_SEP).split(PATH_SEP)
    paths: list[str] = current_path.split(PATH_SEP)

    for path in paths_to_remove:
        try:
            paths.remove(path)
        except ValueError:
            continue

    return PATH_SEP.join(paths)


def is_there_path(current_path: str, given_path: str) -> bool:
    """Check whether the 'given_path' is in 'current_path'

    Return True if the 'given_path' is in 'current_path'
    Otherwise, return false.

    :param current_path: The value inside the PATH environment variable
    :type current_path: str
    :param given_paths: The paths that the user want it to be deleted
    :type given_paths: str
    :return: True/False, based on whether the 'given_path' is in 'current_path'
    :rtype: bool
    """

    for path in current_path.split(PATH_SEP):
        if given_path == path:
            return True
    return False


def print_msg(title: str, msg: str) -> None:
    """Print message to the user

    This function will print a message to the user
    in form of message title and message body

    :param title: The title of the message
    :type title: str
    :param msg: The body of the message
    :type msg: str
    :return: Nothing, just the print side effect
    :rtype: None
    """
    print()
    print(BOLD_STYLE + GREEN_STYLE + "Welcome to PATHVAR" + END_STYLE)
    print()
    print(BOLD_STYLE + title + ': ' + END_STYLE)
    print('_' * 28 + '\n')
    print(msg)
    print()


if __name__ == "__main__":
    main()
