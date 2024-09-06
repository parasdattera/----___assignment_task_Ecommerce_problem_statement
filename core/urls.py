from django.urls import path
from .views import *


urlpatterns = [
    path("api/customers/", CustomersAPIView.as_view()),
    path("api/customers/<int:id>/", CustomersAPIView.as_view()),
    path("api/products/", ProductAPIView.as_view()),
    path("api/orders/", OrderAPIView.as_view()),
    path("api/orders/<int:id>/", OrderAPIView.as_view()),
]
