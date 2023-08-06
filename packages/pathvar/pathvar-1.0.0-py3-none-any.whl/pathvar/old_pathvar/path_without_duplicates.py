import os

# TODO: Delete the following constants if there is no need to them
HOME_PATH: str = os.path.normpath(os.path.expanduser('~'))
TEMP_PATH: str = os.path.join(HOME_PATH, "__TEMP_current_path_var__.txt")


def main():
    # # Stroe the value of the PATH variable in a temp file
    # print_state("Getting the value of $PATH...")
    # run("echo $PATH >> " + TEMP_PATH, shell=True)
    # print_state("Store temp...")
    # Place holder for the current path
    current_path = os.environ["PATH"]
    # # In case of .txt file
    # # if sys.argv[1].endswith(".txt"):
    # # Read the gotten PATH value and store it in a 'current_path'
    # with open(TEMP_PATH) as f:
    #     lines = f.readlines()
    #     if len(lines) == 0:
    #         run("rm -f " + TEMP_PATH, shell=True)
    #         sys.exit("can't read the $PATH")
    #     for line in lines:
    #         current_path += line.strip()
    # # Delete the temp file
    # run("rm -f " + TEMP_PATH, shell=True)
    # print_state("Delete temp...")
    # # Trim any white spaces
    # current_path = current_path.strip()
    # Print the current state
    print_state("echo Eliminating duplicates...")
    # Filter the path variable
    new_path = str_duplicates_elimination(current_path)
    # Print the current state
    print(f"\nOld: {current_path}\n\
          \nNew: {new_path}\n\
          \nIsAnyDuplicateElimination: {current_path != new_path}\n")


def str_duplicates_elimination(s: str) -> str:
    # Split on ':'
    ss = s.split(':')
    if len(ss) < 2:
        return s
    # Store only the unique paths
    temp_ss = []
    for p in ss:
        if p not in temp_ss:
            temp_ss.append(p)
    # Concatenate the string result
    result = ""
    for part in temp_ss:
        result += part + ':' if part != temp_ss[-1] else part
    # Return the final result string without duplicates
    return result


def print_state(s):
    # TODO: make this function returns a str.
    print()
    print(s)
    print()


if __name__ == "__main__":
    main()
