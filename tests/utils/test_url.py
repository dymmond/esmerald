from lilya._internal._path import clean_path, join_paths


def test_clean_path():
    path = clean_path("test")

    assert path == "/test"


def test_clean_path_underscores():
    path = clean_path("////test")

    assert path == "/test"


def test_join_paths():
    paths = ["base", "test"]

    joined_paths = join_paths(paths)

    assert joined_paths == "/base/test"


def test_join_paths_complex():
    paths = ["base", "test", "//child", "////under"]

    joined_paths = join_paths(paths)

    assert joined_paths == "/base/test/child/under"
