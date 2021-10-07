# IAM Backend

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/40c7e61928a844ff857374bce18dee5d)](https://www.codacy.com/gh/zgzgorg/iam-backend/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=zgzgorg/iam-backend&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/zgzgorg/iam-backend/branch/master/graph/badge.svg?token=IJHGG265W1)](https://codecov.io/gh/zgzgorg/iam-backend)
[![Maintainability](https://api.codeclimate.com/v1/badges/30c4351f9da4107634cf/maintainability)](https://codeclimate.com/github/zgzgorg/iam-backend/maintainability)
[![Actions Status](https://github.com/zgzgorg/iam-backend/workflows/CI/badge.svg)](https://github.com/zgzgorg/iam-backend/actions)

This is Identity Access Management(IAM) system using with Google workspace account

## Config file

Our app support config file under `/etc/zgiam/zgiam.cfg` or use Environment variable `IAM_CONFIG_PATH` point over

The example config file is same as `default_iam.cfg` under `zgiam/conf/default_iam.cfg`

## Environment variable

Check the default config file uder `zgiam/conf/default_iam.cfg`
The variable format is `IAM_{section}_{option}`

Here is some example:

```txt
IAM_CORE_DEBUG

IAM_DATABASE_TYPE
IAM_DATABASE_FILE_PATH
IAM_DATABASE_HOST
IAM_DATABASE_PORT
IAM_DATABASE_USER
IAM_DATABASE_PASSWORD
IAM_DATABASE_DBNAME
IAM_DATABASE_SQLALCHEMY_TRACK_MODIFICATIONS

IAM_LOGGING_CONFIG_PATH
```
