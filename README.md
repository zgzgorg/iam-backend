# IAM Backend

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/40c7e61928a844ff857374bce18dee5d)](https://www.codacy.com/gh/zgzgorg/iam-backend/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=zgzgorg/iam-backend&amp;utm_campaign=Badge_Grade)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/zgzgorg/iam-backend.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/zgzgorg/iam-backend/context:python)
[![Maintainability](https://api.codeclimate.com/v1/badges/30c4351f9da4107634cf/maintainability)](https://codeclimate.com/github/zgzgorg/iam-backend/maintainability)
[![Actions Status](https://github.com/zgzgorg/iam-backend/workflows/CI/badge.svg)](https://github.com/zgzgorg/iam-backend/actions)
[![Actions Status](https://github.com/zgzgorg/iam-backend/workflows/CodeQL/badge.svg)](https://github.com/zgzgorg/iam-backend/actions)
[![codecov](https://codecov.io/gh/zgzgorg/iam-backend/branch/master/graph/badge.svg?token=IJHGG265W1)](https://codecov.io/gh/zgzgorg/iam-backend)

An [Identity Access Management](https://www.onelogin.com/learn/iam) (IAM) system using [Google Workspace](https://workspace.google.com/) accounts.

**Intended Users.** This system is intended for use at [Community Builder Toolbox, Inc.](https://www.cb-t.org/), a California-based [501(c)(3)](https://www.irs.gov/charities-non-profits/charitable-organizations/exemption-requirements-501c3-organizations) non-profit organization. It is currently incubated under *[ZaiGeZaiGu](https://www.zgzg.io)*, a volunteer platform for Chinese in the SF Bay Area.

## Installation

### Set up the environment

Assuming you have [GitHub CLI](https://github.com/cli/cli) installed (possibly via `brew install gh`) and uses [Conda](https://docs.conda.io/en/latest/) as your environment manager, execute the following commands:

```shell
git clone zgzgorg/iam-backend # Clone the repo.
cd iam-backend
conda create -n zgiam python=3.8
conda activate zgiam
make develop
```

### Bootstrap the database

You can skip this section if you're provided with a `zgiam.sql` file.

1. Run `make update-schema`. This will **create an empty SQLite** file at `zgiam/zgiam.sql`.
2. **Open this file with a SQLite editor** of your choice. We recommend [DBeaver](https://dbeaver.io/), which you can install via `brew install --cask dbeaver-community` (assuming you have [Homebrew](https://brew.sh/) installed).
3. Insert a row to the table `account`. Provide the following required fields:

   1. `email` -- You must be able to receive emails via this email address.
   2. `first_name`
   3. `last_name`
   4. `phone_number`
4. Save and exit.

### Run the server

Someone should've sent you an `iam_sqlite.cfg`. Place it under the repo's directory. Run:

```shell
IAM_CONFIG_PATH=$PWD/iam_sqlite.cfg python zgiam/app.py
```

Now, go to <http://127.0.0.1:5000/api/v1/>. You should see a page similar to [this screenshot](https://snippyly.com/img/?q=ppVYktiQC1cBnQtYex8i&EDIT=hnB7q6BAchTXPcMy9BQJ).

## Configuration

**Using a file.** By default, `iam-backend` reads `/etc/zgiam/zgiam.cfg` for configs. The file supports [a dialect of the INI file structure](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure) defined by the Python 3 standard library `configparser`. A sample `zgiam.cfg` file can be found at `zgiam/conf/default_iam.cfg`. You can override the default path via the environment variable `IAM_CONFIG_PATH`.

**Using environment variables.** All variables in this file are also overridable via environment variables. The overriding environment variable should follow the format of `IAM_{section}_{option}`. For example:

- IAM_CORE_DEBUG
- IAM_DATABASE_TYPE
- IAM_DATABASE_FILE_PATH
- IAM_DATABASE_HOST
- IAM_DATABASE_PORT
- IAM_DATABASE_USER
- IAM_DATABASE_PASSWORD
- IAM_DATABASE_DBNAME
- IAM_DATABASE_SQLALCHEMY_TRACK_MODIFICATIONS
- IAM_LOGGING_CONFIG_PATH

## Styles, Conventions, and Standards

This repo adheres to the following practices:

- [Semantic Versioning 2.0.0](https://semver.org/).
- [Conversational Commits](https://www.conventionalcommits.org/en/v1.0.0/): A specification for adding human and machine readable meaning to **commit messages**. Configured with `.commitlintrc.yml`.
- [Black](https://black.readthedocs.io/en/stable/): The uncompromising code formatter for Python. Takes priority over _PEP 8_.
- [PEP 8](https://www.python.org/dev/peps/pep-0008/): **Style Guide** for Python Code.
  - This repo uses both [`pycodestyle`](https://pycodestyle.pycqa.org/en/latest/) and [`flake8`](https://flake8.pycqa.org/en/latest/) to enforce PEP 8. They have each other's back.
- Python code should be **typed**. This repo uses both [`mypy`](http://mypy-lang.org/) (by Python makers) and [`pytype`](https://opensource.google/projects/pytype) (by Google) as type checkers. They have each other's back.

Further, this repo uses these dev-cycle tools:

- A [requirements file](https://pip.pypa.io/en/stable/user_guide/#requirements-files) **defines dependencies** that are parsable to [`pip`](https://pip.pypa.io/en/stable/getting-started/). [`pip-tools`](https://github.com/jazzband/pip-tools) reads the `.in` files and generates pip-friendly `requirements.txt`.
- [`makefile`](https://www.gnu.org/software/make/manual/make.html) defines most of the **dev-cycle actions**.
  - Many of these actions are automatically triggered with [pre-commit hooks](https://pre-commit.com/).

- [`pytest`](https://docs.pytest.org/en/6.2.x/) is for **unit tests**.
  - [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/) generates the `.coverage` file. It computes **coverage** from `pytest` unit tests.

- [Codacy](https://www.codacy.com/) **checks code quality** and keep track of technical debt. It integrates well into GitHub reviews.
- [Pylint](https://pylint.org/) is another Python code analyzer.
- [Dependabot](https://docs.github.com/en/code-security/supply-chain-security/managing-vulnerabilities-in-your-projects-dependencies/configuring-dependabot-security-updates) makes security updates.
- [CodeQL](https://codeql.github.com/) (by GitHub) and [LGTM](https://lgtm.com/) (by Semmle) **discover vulnerabilities**. They have each other's back.

## Structure

This repo uses these modules:

- [Alembic](https://alembic.sqlalchemy.org/en/latest/) is a lightweight **database migration** tool for usage with the [SQLAlchemy](https://www.sqlalchemy.org/) Database Toolkit for Python.
- [google-auth](https://google-auth.readthedocs.io/en/master/) is the Google authentication library for Python.
- [Gunicorn](https://gunicorn.org/) 'Green Unicorn' is a Python WSGI HTTP Server for UNIX.
- [SQLAlchemy](https://www.sqlalchemy.org/) is a Python SQL toolkit.
- [Blinker](https://pythonhosted.org/blinker/) provides fast & simple object-to-object and broadcast signaling for Python objects.
- [Flask](https://flask.palletsprojects.com/en/2.0.x/) is a web framework for Python. Flask depends on the [Jinja](https://www.palletsprojects.com/p/jinja/) template engine and the [Werkzeug](https://www.palletsprojects.com/p/werkzeug/) WSGI toolkit. We use these plugins of Flask:
  - [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/quickstart.html) enables one to define API endpoints via a class-method structure.
  - [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/).
  - [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/stable/).
  - [Flask-Dance](https://flask-dance.readthedocs.io/en/latest/) for OAuth.
  - [Flask-Login](https://flask-login.readthedocs.io/en/latest/) provides user session management for Flask.
