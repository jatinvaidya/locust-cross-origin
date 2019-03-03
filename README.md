Prerequisites:
[Locust](https://locust.io) must be setup

Steps to run the load test:
1. Clone this repository
2. Copy `auth0Env.sample.py` to `auth0Env.py`
3. Edit `auth0Env.py` with values for your environment
4. On `Terminal`: ```locust --host="https://AUTH0_TENANT_URL"```
5. On `Browser`: http://localhost:8089
6. Input `Number of users` and `Hatch rate` and `Start swarming`
7. Check `Terminal` for logs

