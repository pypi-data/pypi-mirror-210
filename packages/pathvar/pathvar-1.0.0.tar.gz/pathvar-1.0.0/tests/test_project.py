from src.pathvar.project import *


inp = "/home/hussein/.cache/activestate/bin:/home/hussein/.local/ActiveState/StateTool/release/bin:/home/hussein/.cache/activestate/bin:/home/hussein/.local/ActiveState/StateTool/release/bin:/usr/bin/nodejs/node-v16.16.0-linux-x64/bin:/usr/bin/nodejs/node-v16.16.0-linux-x64/bin:/home/hussein/.local/bin:/usr/bin/nodejs/node-v16.16.0-linux-x64/bin:/usr/bin/nodejs/node-v16.16.0-linux-x64/bin:/home/hussein/.local/bin:/usr/bin/nodejs/node-v16.16.0-linux-x64/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/usr/lib/jvm/java-17-oracle/bin:/usr/lib/jvm/java-17-oracle/db/bin:/usr/share/rvm/bin:/usr/lib/jvm/java-17-oracle/bin:/usr/lib/jvm/java-17-oracle/db/bin:/usr/lib/jvm/java-17-oracle/bin:/usr/lib/jvm/java-17-oracle/db/bin"
out = "/home/hussein/.cache/activestate/bin:/home/hussein/.local/ActiveState/StateTool/release/bin:/usr/bin/nodejs/node-v16.16.0-linux-x64/bin:/home/hussein/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/usr/lib/jvm/java-17-oracle/bin:/usr/lib/jvm/java-17-oracle/db/bin:/usr/share/rvm/bin"


def test_str_duplicates_elimination():
    assert path_duplicates_eliminator(
        "x:x:y:y:z:z:xy:xz:yz:xyz:X:Y:Z:XY:XZ:YZ:XYZ:X:Y:Z"
    ) == "x:y:z:xy:xz:yz:xyz:X:Y:Z:XY:XZ:YZ:XYZ"
    assert path_duplicates_eliminator(inp) == out
    assert path_duplicates_eliminator(out) == out
    assert path_duplicates_eliminator('') == ''


def test_path_remover():
    assert path_remover(
        "foo/foo:bar/bar:baz/baz",
        "bar/bar"
    ) == "foo/foo:baz/baz"
    assert path_remover("foo/foo", "foo/foo") == ""
    assert path_remover("foo/foo", "bar/bar") == "foo/foo"
    assert path_remover(
        "foo/foo:bar/bar:baz/baz",
        "baz/baz"
    ) == "foo/foo:bar/bar"


def test_is_there_path():
    assert is_there_path(
        "foo/foo:/bar/bar:baz/baz",
        "baz/baz"
    ) == True
    assert is_there_path(
        "foo/foo:/bar/bar:baz/baz",
        "foo/foo"
    ) == True
    assert is_there_path(
        "foo/foo:/bar/bar:baz/baz",
        "baz/baz:foo/foo"
    ) == False
    assert is_there_path(
        "foo/foo:/bar/bar:baz/baz",
        "foo/baz"
    ) == False
