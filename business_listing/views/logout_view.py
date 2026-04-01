from django.contrib.auth.views import LogoutView

class SecureLogoutView(LogoutView):
    """Restrict logout to POST so third parties cannot trigger it with a link."""

    http_method_names = ['post', 'options']


logout_view = SecureLogoutView.as_view(next_page='listed_businesses')
