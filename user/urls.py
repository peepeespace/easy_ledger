from django.urls import path

from user.views import (
    UserViewList,
    UserDetailView,
    LoginView,
)

from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', UserViewList.as_view()),
    path('<int:pk>/', UserDetailView.as_view()),
    path('login/', LoginView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)