from rest_framework.authtoken.models import Token

class TokenAuthMiddleware:
    def __init__(self, get_response, excluded_methods=None, included_methods=None):
        self.get_response = get_response
        self.excluded_methods = excluded_methods or []
        self.included_methods = included_methods or []
        
    def __call__(self, request):
        if '/api/' in request.path:
            if request.method in self.excluded_methods:
                request.user = None
            elif request.method in self.included_methods or not self.included_methods:
                if 'Authorization' in request.headers:
                    auth = request.headers['Authorization'].split()
                    if len(auth) == 2 and auth[0].lower() == 'token':
                        token = auth[1]
                        try:
                            token = Token.objects.select_related('user').get(key=token)
                            request.user = token.user
                        except Token.DoesNotExist:
                            request.user = None
                else:
                    request.user = None
        response = self.get_response(request)
        return response
