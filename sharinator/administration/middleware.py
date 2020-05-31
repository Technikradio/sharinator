from django.contrib.auth import logout
from django.http import HttpRequest

class ForceLogoutMiddleware(object):
    def process_request(self, request: HttpRequest):
        if request.user.is_authenticated() and request.user.force_logout_date and \
                request.session['LAST_LOGIN_DATE'] < request.user.force_logout_date:
                    logout(request)

