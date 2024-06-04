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

### Documentation

Improving the documentation is quite easy and it is placed inside the `esmerald/docs` folder.

To start the docs, run:


```shell
$ hatch run docs:serve
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
