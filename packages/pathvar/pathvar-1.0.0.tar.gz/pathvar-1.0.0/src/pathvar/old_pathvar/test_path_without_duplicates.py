from path_without_duplicates import str_duplicates_elimination

# Read input & output form files
def read_file(file_path: str) -> str:
    s = ""
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            s += line.strip()
    return s

inp = read_file("test_path_without_duplicates_input.txt")
out = read_file("test_path_without_duplicates_output.txt")

def test_str_duplicates_elimination():
    assert str_duplicates_elimination(
        "x:x:y:y:z:z:xy:xz:yz:xyz:X:Y:Z:XY:XZ:YZ:XYZ:X:Y:Z"
    ) == "x:y:z:xy:xz:yz:xyz:X:Y:Z:XY:XZ:YZ:XYZ"
    assert str_duplicates_elimination(inp) == out
    assert str_duplicates_elimination(out) == out
    assert str_duplicates_elimination('') == ''
