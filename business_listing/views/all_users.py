from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.db.models import Q
User = get_user_model()
from django.shortcuts import render

class AllUsersView(ListView):
    model = User
    template_name = 'business_listing/all_users.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.select_related('profile').all().order_by('-date_joined')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
                | Q(profile__city__icontains=query)
                | Q(profile__country__icontains=query)
                | Q(profile__postal_code__icontains=query)
                | Q(profile__about_me__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        return context

# For function-based import compatibility
all_users = AllUsersView.as_view()