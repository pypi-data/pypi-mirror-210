# pathvar

### Video Demo:  https://youtu.be/THzJUZlqiI0x
### Description:

My final project for **CS50P**: "*CS50 Introduction to Programming with Python*".

![Screenshot of the utility's help option output.](./assets/images/pathvar_screen.png)

This tool meant to facilitate the interaction with the system's PATH environment variable (Linux BASH shell only).

- To get the work done correctly do the following: 
    * Read the 'help' instruction well 
    * Be careful about the paths you input (with some options) 
    * Separate between multiple paths with a single colon ':'

NOTE: This program saves the new modified PATH's value in '~/.bash_profile' file,
and if this file not exists creates a new one, 
and eventually source the '~/.bashrc' and '~/.profile' if any of them exists.

---

### Usage:

    project.py [-h] [-s] [-e] [-a] [-p] [-d] [-q] [--remove-all-paths] [-v]

### Options:

- **_-h, --help_**
    * show this help message and exit
- **_-s, --show_**
    * shows the current value of the 'PATH' (default)
- **_-e, --eliminate-duplicates_**
    * eliminates any duplicates in the value of the 'PATH' (Included with any modifications)
- **_-a , --append_**
    * appends any number of paths to the current value of the 'PATH' (which are must be given as a
                        single string separated with ':' between every two paths and without any spaces)
- **_-p , --push_**
    * pushes any number of paths at the beginning of the current value of 'PATH' (which are must be
                        given as a single string separated with ':' between every two paths and without any spaces)
- **_-d , --delete_**
    * deletes from 'PATH' any number of paths (which are must be given as a single string separated
                        with ':' between every two paths and without any spaces)
- **_-q , --query_**
    * checks whether the given path is in the current 'PATH'
- **_--remove-all-paths_**
    * removes all paths in the current 'PATH' (NOT RECOMMENDED)
- **_-v, --version_**
    * show program's version number and exit

---

### Code design:
*The entire program is designed using the Functional Programming Paradigm and all application's logic included in one file: 'project.py'.*

### Code documentation:

#### Contents:

* [pathvar.project module](#pathvarproject-module)


    * [`add_args()`](#pathvarprojectadd_argsparser_obj-argumentparser)


    * [`get_path()`](#pathvarprojectget_path)


    * [`is_there_path()`](#pathvarprojectis_there_pathcurrent_path-str-given_path-str)


    * [`main()`](#pathvarprojectmain)


    * [`parse_args_and_modify_path_str()`](#pathvarprojectparse_args_and_modify_path_strparser_obj-argumentparser-current_path-str)


    * [`path_duplicates_eliminator()`](#pathvarprojectpath_duplicates_eliminators-str)


    * [`path_remover()`](#pathvarprojectpath_removercurrent_path-str-given_paths-str)


    * [`print_msg()`](#pathvarprojectprint_msgtitle-str-msg-str)


    * [`run_command_verbosely()`](#pathvarprojectrun_command_verboselycmd-str)


    * [`update_path()`](#pathvarprojectupdate_pathnew_path_value-str)

### pathvar.project module

#### pathvar.project.add_args(parser_obj: ArgumentParser)
*Adding CL arguments to and ArgumentParser object*

*Manipulate the inputted ArgumentParser object 
by adding the needed command line arguments to it
with all the specifications for each of the arguments
(i.e. argument name, action, help, …).*


* **Parameters**

    **parser_obj** (*argparse.ArgumentParser*) – parser object for parsing the command line arguments


* **Returns**

    None


* **Return type**

    None


#### pathvar.project.get_path()
*A simple function to get the current PATH*

*Get the current PATH environment variable
using the command meant for that 
depending on the kind of the operating system that pathvar running on.*

* **Returns**

    The value of the PATH variable


* **Return type**

    str


#### pathvar.project.is_there_path(current_path: str, given_path: str)
*Check whether the ‘given_path’ is in ‘current_path’*

*Return True if the ‘given_path’ is in ‘current_path’
Otherwise, return false.*


* **Parameters**

    
    * **current_path** (*str*) – The value inside the PATH environment variable


    * **given_paths** (*str*) – The paths that the user want it to be deleted



* **Returns**

    True/False, based on whether the ‘given_path’ is in ‘current_path’



* **Return type**

    bool


#### pathvar.project.main()
*pathvar main function*

*The Logic of the entire ‘pathvar’ program.*


* **Returns**

    Nothing, just execute the logic of the entire program.



* **Return type**

    None


#### pathvar.project.parse_args_and_modify_path_str(parser_obj: ArgumentParser, current_path: str)
*Parsing the command line arguments*

*Using ‘argparse’ library this function will consume an ‘ArgumentParser’ object
in order to parse the arguments and handle the chosen option/s.*


* **Parameters**

    **parser_obj** (*argparse.ArgumentParser*) – parser object for parsing the command line arguments



* **Returns**

    None



* **Return type**

    None



#### pathvar.project.path_duplicates_eliminator(s: str)
*Remove any duplicates in a PATH variable*

*This function removes any duplicated paths from a PATH variable.
It looks for duplicated paths.*


* **Parameters**

    **s** (*str*) – The value of the PATH environment variable



* **Returns**

    The same input of the PATH value without any duplicates



* **Return type**

    str


#### pathvar.project.path_remover(current_path: str, given_paths: str)
*Delete the given path/s from the current PATH*

*return copy of the ‘current_path’ 
without and value included in the ‘given_paths’*


* **Parameters**

    
    * **current_path** (*str*) – The value inside the PATH environment variable


    * **given_paths** (*str*) – The paths that the user want it to be deleted



* **Returns**

    A copy from the current path without any given path



* **Return type**

    str


#### pathvar.project.print_msg(title: str, msg: str)
*Print message to the user*

*This function will print a message to the user
in form of message title and message body*


* **Parameters**

    
    * **title** (*str*) – The title of the message


    * **msg** (*str*) – The body of the message



* **Returns**

    Nothing, just the print side effect



* **Return type**

    None


#### pathvar.project.run_command_verbosely(cmd: str)
*Run a given command in subprocess*

*Run the given command in subprocess 
and print and ‘stdout’ or ‘stderr’*


* **Parameters**

    **cmd** (*str*) – Command to run


#### pathvar.project.update_path(new_path_value: str)
*Run a command to update the PATH variable*

*Run the needed commands for updating the PATH environment variable
based on the current operating system and print any ‘stdout’ or ‘stderr’*


* **Parameters**

    **new_path_value** (*str*) – The new value in order to set the PATH variable to it

---

### License:
<h6 align="center">Copyright (c) 2023 Hussein Mahmoud Kandil - MIT<h6>
