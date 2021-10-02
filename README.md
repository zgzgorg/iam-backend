# IAM Backend

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
