# TL_sample_task


## Spin up docker containers
```
docker compose up
```

## Run python parse
```
docker compose exec python_service python sample_data_parsing.py -c site.conf
```

MySQL is exposed to
port: 3307
user: develop
password: develop


## Log into database container
```
docker compose exec db mysql -p tl_data
```
