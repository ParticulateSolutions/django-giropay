from django.conf.urls import url

from .views import NotifyGiropayView, GiropayReturnView

urlpatterns = [
    url(r'^notify/$', NotifyGiropayView.as_view(), name='notifiy'),
    url(r'^return/$', GiropayReturnView.as_view(), name='return'),
]
