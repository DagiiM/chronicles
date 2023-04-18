from rest_framework.authtoken.models import Token

class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if '/api/' in request.path:
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
