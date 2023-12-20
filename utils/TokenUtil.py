import jwt

class TokenUtil:
    accessToken = None
    idToken = None

    def __init__(self, request):
        self.accessToken = request.headers['authorization'].split(' ')[1]

    def getUserName(self):
        try:
            return jwt.decode(self.idToken, verify=False)['given_name']
        except KeyError:
            return "User"

    def getUserId(self):
        return jwt.decode(self.idToken, verify=False)['sub']
    
    def getEmail(self):
        return jwt.decode(self.idToken, verify=False)['email']

