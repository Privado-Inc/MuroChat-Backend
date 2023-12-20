import json
import logging
import urllib.error
import urllib.request

# Get an instance of a logger
log = logging.getLogger(__name__)


class HttpClient:

    @classmethod
    def getTheContent(cls, url):

        req = urllib.request.Request(url=url)
        try:
            response = urllib.request.urlopen(req, timeout=2)
            return json.loads(response.read())

        except urllib.error.HTTPError as httpError:
            log.error(f'Unable to connect: {url}, {httpError}, {str(httpError.read().decode())}')
            return str(httpError.read().decode())

        except TimeoutError:
            log.error(f"Timeout Error at {url}")

        except urllib.error.URLError as urlError:
            log.error(f'Unable to connect: {url}, {urlError}')
        return None

    @classmethod
    def postTheContent(cls, url, data, headers=None):
        dataBytes = bytes(json.dumps(data).encode("utf-8"))

        req = urllib.request.Request(url=url, data=dataBytes, method='POST')

        if headers:
            for headerKey in headers.keys():
                req.add_header(headerKey, headers[headerKey])

        try:
            response = urllib.request.urlopen(req, timeout=5)
            return response.status, json.loads(response.read())

        except urllib.error.HTTPError as httpError:
            message = httpError.read().decode()
            log.error(f'Unable to connect: {url}, {httpError}, {message}, {data}')
            if "message" in message:
                return None, f"{json.loads(message)['message']}"

        except TimeoutError:
            log.error(f"Timeout Error at {url}")

        except urllib.error.URLError as urlError:
            log.error(f'Unable to connect: {url}, {urlError}')

        return None, None
