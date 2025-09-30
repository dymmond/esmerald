import os
import shutil
import sys

import pytest


@pytest.fixture(scope="function", autouse=True)
def create_folders():
    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    try:
        os.remove("app.db")
    except OSError:
        pass
    try:
        shutil.rmtree("myproject")

    except OSError:
        pass
    try:
        shutil.rmtree("temp_folder")
    except OSError:
        pass

    yield

    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    try:
        os.remove("app.db")
    except OSError:
        pass
    try:
        shutil.rmtree("myproject")

    except OSError:
        pass
    try:
        shutil.rmtree("temp_folder")
    except OSError:
        pass


@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python 3.11 or higher")
def test_send_mail_directive(client, create_folders):
    # Create the project
    os.environ["ESMERALD_DEFAULT_APP"] = "tests.cli.main:app"
    result = client.invoke(["createproject", "myproject"])

    assert result.exit_code == 0

    # Change directory to the project
    os.chdir("myproject")

    # Run the sendtest mail directive
    result = client.invoke(
        [
            "mail",
            "sendtest",
            "--to",
            "user@example.com",
            "--subject",
            "Hello",
            "--text",
            "Plain message",
        ]
    )

    assert result.exit_code == 0
    assert "Test email sent to 'user@example.com' using console backend." in result.output


@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python 3.11 or higher")
def test_send_mail_directive_to_multiple(client, create_folders):
    # Create the project
    os.environ["ESMERALD_DEFAULT_APP"] = "tests.cli.main:app"
    result = client.invoke(["createproject", "myproject"])

    assert result.exit_code == 0

    # Change directory to the project
    os.chdir("myproject")

    # Run the sendtest mail directive
    result = client.invoke(
        [
            "mail",
            "sendtest",
            "--to",
            "user@example.com",
            "--to",
            "user2@example.com",
            "--subject",
            "Hello",
            "--text",
            "Plain message",
        ]
    )

    assert result.exit_code == 0


@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python 3.11 or higher")
def test_send_mail_directive_html(client, create_folders):
    # Create the project
    os.environ["ESMERALD_DEFAULT_APP"] = "tests.cli.main:app"
    result = client.invoke(["createproject", "myproject"])

    assert result.exit_code == 0

    # Change directory to the project
    os.chdir("./myproject")

    # Run the sendtest mail directive
    result = client.invoke(
        [
            "mail",
            "sendtest",
            "--to",
            "user@example.com",
            "--subject",
            "Hello",
            "--html",
            "<h1>HTML message</h1>",
        ]
    )

    assert result.exit_code == 0
    assert "<h1>HTML message</h1>" in result.output
