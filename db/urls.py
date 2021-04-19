from django.urls import path
from db.views import HelloView

urlpatterns = [
    path('hello/', HelloView.as_view(), name='hello'),
]