# Contributing

Thank you for showing interest in contributing to Esmerald. There are many ways you can help and contribute to the
project.

* Try Esmerald and [report bugs and issues](https://github.com/dymmond/esmerald/issues/new) you find.
* [Implement new features](https://github.com/dymmond/esmerald/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
* Help others by [reviewing pull requests](https://github.com/dymmond/esmerald/pulls)
* Help writing documentation
* Use the discussions and actively participate on them.
* Become an contributor by helping Esmerald growing and spread the words across small, medium, large or any company
size.

## Reporting possible bugs and issues

It is natural that you might find something that Esmerald should support or even experience some sorte of unexpected
behaviour that needs addressing.

The way we love doing things is very simple, contributions should start out with a
[discussion](https://github.com/dymmond/esmerald/discussions). The potential bugs shall be raised as "Potential Issue"
in the discussions, the feature requests may be raised as "Ideas".

We can then decide if the discussion needs to be escalated into an "Issue" or not.

When reporting something you should always try to:

* Be as more descriptive as possible
* Provide as much evidence as you can, something like:
    * OS platform
    * Python version
    * Installed dependencies
    * Code snippets
    * Tracebacks

Avoid putting examples extremely complex to understand and read. Simplify the examples as much as possible to make
it clear to understand and get the required help.

## Development

To develop for Esmerald, create a fork of the [Esmerald repository](https://github.com/dymmond/esmerald) on GitHub.

After, clone your fork with the follow command replacing `YOUR-USERNAME` with your GitHub username:

```shell
$ git clone https://github.com/YOUR-USERNAME/esmerald
```

Esmerald also uses [hatch](https://hatch.pypa.io/latest/) for its development, testing and release cycles.

Please make sure you run:

```shell
$ pip install hatch
```

### Install the project dependencies

Not necessary because the dependencies are automatically installed by hatch.
But if environments should be pre-initialized it can be done with `hatch env`

```shell
$ cd esmerald
$ hatch env create
$ hatch env create test
$ hatch env create docs
```

!!! Tip
    This is the recommended way but if you still feel you want your own virtual environment and
    all the packages installed there, you can always run `scripts/install`.

### Enable pre-commit

The project comes with a pre-commit hook configuration. To enable it, just run inside the clone:

```shell
$ pre-commit install
```

### Run the tests

To run the tests, use:


```shell
$ hatch run test:test
```

Because Esmerald uses pytest, any additional arguments will be passed. More info within the
[pytest documentation](https://docs.pytest.org/en/latest/how-to/usage.html)

For example, to run a single test_script:

```shell
$ hatch run test:test tests/test_apiviews.py
```

To run the linting, use:


```shell
$ hatch run lint
```

## Documentation

Improving the documentation is quite easy and it is placed inside the `esmerald/docs` folder.

To build all the documentation:

```shell
$ hatch run docs:build
```

### Docs live (serving the docs)

During local development, there is a script that builds the site and checks for any changes, live-reloading:

```shell
$ hatch run docs:serve
```

It will serve the documentation on `http://localhost:8000`.

If you wish to serve on a different port:

```shell
$ hatch run docs:serve -p <PORT-NUMBER>
```

That way, you can edit the documentation/source files and see the changes live.

!!! tip
    Alternatively, you can perform the same steps that scripts does manually.

    Go into the language directory, for the main docs in English it's at `docs/en/`:

    ```console
    $ cd docs/en/
    ```

    Then run `mkdocs` in that directory:

    ```console
    $ mkdocs serve --dev-addr 8000
    ```

### Docs Structure

The documentation uses <a href="https://www.mkdocs.org/" class="external-link" target="_blank">MkDocs</a>.

And there are extra tools/scripts in place to handle translations in `./scripts/docs.py`.

!!! tip
    You don't need to see the code in `./scripts/docs.py`, you just use it in the command line.

All the documentation is in Markdown format in the directory `./docs/en/`.

Many of the tutorials have blocks of code.

In most of the cases, these blocks of code are actual complete applications that can be run as is.

In fact, those blocks of code are not written inside the Markdown, they are Python files in the `./docs_src/` directory.

And those Python files are included/injected in the documentation when generating the site.

### Translations

Help with translations is VERY MUCH appreciated! And it can't be done without the help from the community.

Here are the steps to help with translations.

#### Tips and guidelines

* Check the currently <a href="https://github.com/dymmond/esmerald/pulls" class="external-link" target="_blank">existing pull requests</a> for your language. You can filter the pull requests by the ones with the label for your language. For example, for Spanish, the label is <a href="https://github.com/dymmond/esmerald/pulls?q=is%3Aopen+sort%3Aupdated-desc+label%3Alang-es+label%3Aawaiting-review" class="external-link" target="_blank">`lang-es`</a>.

* Review those pull requests, requesting changes or approving them. For the languages I don't speak, I'll wait for several others to review the translation before merging.

!!! tip
    You can <a href="https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/commenting-on-a-pull-request" class="external-link" target="_blank">add comments with change suggestions</a> to existing pull requests.

    Check the docs about <a href="https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-request-reviews" class="external-link" target="_blank">adding a pull request review</a> to approve it or request changes.

* Check if there's a <a href="https://github.com/dymmond/esmerald/discussions/categories/translations" class="external-link" target="_blank">GitHub Discussion</a> to coordinate translations for your language. You can subscribe to it, and when there's a new pull request to review, an automatic comment will be added to the discussion.

* If you translate pages, add a single pull request per page translated. That will make it much easier for others to review it.

* To check the 2-letter code for the language you want to translate, you can use the table <a href="https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes" class="external-link" target="_blank">List of ISO 639-1 codes</a>.

#### Existing language

Let's say you want to translate a page for a language that already has translations for some pages, like Spanish.

In the case of Spanish, the 2-letter code is `es`. So, the directory for Spanish translations is located at `docs/es/`.

!!! tip
    The main ("official") language is English, located at `docs/en/`.

Now run the live server for the docs in Spanish:

<div class="termy">

```shell
// Use the command "live" and pass the language code as a CLI argument
$ hatch run docs:serve_lang es
```

</div>

!!! tip
    Alternatively, you can perform the same steps that scripts does manually.

    Go into the language directory, for the Spanish translations it's at `docs/es/`:

    ```console
    $ cd docs/es/
    ```

    Then run `mkdocs` in that directory:

    ```console
    $ mkdocs serve --dev-addr 8000
    ```

Now you can go to <a href="http://127.0.0.1:8000" class="external-link" target="_blank">http://127.0.0.1:8000</a> and see your changes live.

You will see that every language has all the pages. But some pages are not translated and have an info box at the top, about the missing translation.

Now let's say that you want to add a translation for the section [Router](routing/router.md){.internal-link target=_blank}.

* Copy the file at:

```
docs/en/docs/routing/router.md
```

* Paste it in exactly the same location but for the language you want to translate, e.g.:

```
docs/es/docs/routing/router.md
```

!!! tip
    Notice that the only change in the path and file name is the language code, from `en` to `es`.

If you go to your browser you will see that now the docs show your new section (the info box at the top is gone). 🎉

Now you can translate it all and see how it looks as you save the file.

#### New Language

Let's say that you want to add translations for a language that is not yet translated, not even some pages.

Let's say you want to add translations for Creole, and it's not yet there in the docs.

Checking the link from above, the code for "Creole" is `ht`.

The next step is to run the script to generate a new translation directory:

```shell
// Use the command new-lang, pass the language code as a CLI argument
$ hatch run docs:new_lang ht

Successfully initialized: docs/ht
```

Now you can check in your code editor the newly created directory `docs/ht/`.

That command created a file `docs/ht/mkdocs.yml` with a simple config that inherits everything from the `en` version:

```yaml
INHERIT: ../en/mkdocs.yml
site_dir: '../../site_lang/ht'
```

!!! tip
    You could also simply create that file with those contents manually.

That command also created a dummy file `docs/ht/index.md` for the main page, you can start by translating that one.

You can continue with the previous instructions for an "Existing Language" for that process.

You can make the first pull request with those two files, `docs/ht/mkdocs.yml` and `docs/ht/index.md`. 🎉

#### Preview the result

As already mentioned above, you can use the `./scripts/docs.py` with the `live` command to preview the results (or `mkdocs serve`).

Once you are done, you can also test it all as it would look online, including all the other languages.

To do that, first build all the docs:


```shell
// Use the command "build-all", this will take a bit
$ hatch run docs:build
```

You can also collect documentation for one language

```shell
// Use the command "build-lang", this will take a bit
$ hatch run docs:build_lang your_lang
```

This builds all those independent MkDocs sites for each language, combines them, and generates the final output at `./site/`.

Then you can serve that with the command `serve`:

```shell
// Use the command "serve" after running "build-all" or "build-lang -l your_lang"
$ hatch run docs:dev

Warning: this is a very simple server. For development, use mkdocs serve instead.
This is here only to preview a site with translations already built.
Make sure you run the build-all command first.
Serving at: http://127.0.0.1:8008
```


## Building Esmerald

To build a package locally, run:


```shell
$ hatch build
```


Alternatively running:


```shell
$ hatch shell
```

It will install the requirements and create a local build in your virtual environment.

## Releasing

*This section is for the maintainers of `Esmerald`*.

### Building the Esmerald for release

Before releasing a new package into production some considerations need to be taken into account.

* **Changelog**
    * Like many projects, we follow the format from [keepchangelog](https://keepachangelog.com/en/1.0.0/).
    * [Compare](https://github.com/dymmond/esmerald/compare/) `main` with the release tag and list of the entries
that are of interest to the users of the framework.
        * What **must** go in the changelog? added, changed, removed or deprecated features and the bug fixes.
        * What is **should not go** in the changelog? Documentation changes, tests or anything not specified in the
point above.
        * Make sure the order of the entries are sorted by importance.
        * Keep it simple.

* *Version bump*
    * The version should be in `__init__.py` of the main package.

#### Releasing

Once the `release` PR is merged, create a new [release](https://github.com/dymmond/esmerald/releases/new)
that includes:

Example:

There will be a release of the version `0.2.3`, this is what it should include.

* Release title: `Version 0.2.3`.
* Tag: `0.2.3`.
* The description should be copied from the changelog.

Once the release is created, it should automatically upload the new version to PyPI. If something
does not work with PyPI the release can be done by running `scripts/release`.
