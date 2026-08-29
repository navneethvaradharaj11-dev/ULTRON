# ULTRON ENVIRONMENT CONFIGURATION REFERENCE

| Variable Name | Default | Required in Prod? | Description |
| :--- | :--- | :---: | :--- |
| `ENVIRONMENT` | `development` | Yes | Target runtime (`development`, `staging`, `production`). |
| `DEBUG` | `True` | Yes (`False`) | Controls verbose debugging output. Must be `False` in prod. |
| `JWT_SECRET` | *dev secret* | Yes | Key for signing JWT access and refresh tokens. Must be >=32 bytes. |
| `MYSQL_HOST` | `localhost` | Yes | MySQL server hostname or service name (`mysql`). |
| `MYSQL_USER` | `root` | Yes | MySQL database user. |
| `MYSQL_PASSWORD` | `root` | Yes | MySQL user password. Cannot be `root` in prod. |
| `REDIS_HOST` | `localhost` | Yes | Redis server hostname (`redis`). |
| `RATE_LIMIT_PER_MINUTE` | `60` | No | Sliding window REST API rate limit per client IP/user. |
