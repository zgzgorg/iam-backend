# IAM Backend

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e00783cf6d234f67ba3c0527918daddb)](https://app.codacy.com/gh/zgzgorg/iam-backend?utm_source=github.com&utm_medium=referral&utm_content=zgzgorg/iam-backend&utm_campaign=Badge_Grade_Settings)

This is Identity Access Management(IAM) system using with g-suite

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
