from locust import HttpLocust, TaskSet, task
from urllib.parse import urlencode, urlparse, parse_qs
import sys, logging, csv, random
import auth0Env, auth0Constants

logger = logging.getLogger(__name__)
logger.setLevel(auth0Constants.LOG_LEVEL)
TEST_USERS = None

# this class represents a user's actions
# it has only one task (ex. user clicks on login (/co/authenticate) link)
class UserBehavior(TaskSet):

    email = None
    password = None

    def on_start(self):
            if len(TEST_USERS) > 0:
                self.email, self.password = random.choice(TEST_USERS)
                logger.info("{}: {}".format("testing with user", self.email))
            else:
                sys.exit("users.csv must be populated with users")

    @task(1)
    def co(self):
        # prepare cross origin call
        logger.debug("---------------cross-origin-call------------------")
        jsonBody = {
            "client_id": auth0Env.AUTH0_CLIENT_ID,
            "username": self.email,
            "password": self.password,
            "realm": auth0Env.AUTH0_CONNECTION,
            "credential_type": auth0Constants.CREDENTIAL_TYPE
        }
        headers = {
            "content-type": "application/json",
            "auth0-clients": auth0Constants.CLIENT_TYPE,
            "origin": auth0Env.ORIGIN
        }
        # make cross-origin call
        logger.info("making cross-origin call")
        response = self.client.post(
            "/co/authenticate", json=jsonBody, headers=headers)
        loginTicket = response.json().get("login_ticket")
        logger.debug("{}: {}".format("login_ticket", loginTicket))
        logger.info("{}: {}".format("response status_code", response.status_code))
        
        cookieJar = response.cookies
        if(logger.getEffectiveLevel() == "DEBUG"):
            for cookie in cookieJar:
                logging.debug("{}: {}".format("response cookie.name", cookie.name))

        # authorize
        logger.debug("----------------------authorize-call----------------------")
        encodedArgs = urlencode({
            "client_id": auth0Env.AUTH0_CLIENT_ID,
            "response_type": "id_token token",
            "redirect_uri": auth0Env.REDIRECT_URI,
            "scope": "openid profile email",
            "login_ticket": loginTicket,
            "state": "some-state",
            "nonce": "some-nonce",
            "audience": auth0Env.AUDIENCE,
            "realm": auth0Env.AUTH0_CONNECTION
        })
        authorizeUrl = "/authorize?" + encodedArgs
        logger.debug("{}: {}".format("authorizeUrl", authorizeUrl))
        logger.info("making authorize call with login_ticket")
        response = self.client.get(
            authorizeUrl, cookies=cookieJar, allow_redirects=False)
        
        logger.info("{}: {}".format("response status_code", response.status_code))
        logger.debug("{}: {}".format("response location",
                              response.headers['Location']))
        logger.debug("{}: {}".format("response url (i.e. request)", response.url))
        parsedUrl = urlparse(
            response.headers['Location'], allow_fragments=True)
        fragment = parsedUrl.fragment
        logger.debug("{}: {}".format("fragment", fragment))
        logger.info("{}: {}".format("access_token",
                              parse_qs(fragment)['access_token'][0]))
        logger.info("{}: {}".format("id_token", parse_qs(fragment)['id_token'][0]))
        
        cookieJar = response.cookies
        if(logger.getEffectiveLevel() == "DEBUG"):
            for cookie in cookieJar:
                logger.debug("{}: {}".format("response cookie.name", cookie.name))

# this class represents a user
class User(HttpLocust):

    task_set = UserBehavior

    def __init__(self):
        super(User, self).__init__()
        global TEST_USERS
        with open('users.csv', 'rt') as users_csv:
            reader = csv.reader(users_csv)
            TEST_USERS = list(reader)

