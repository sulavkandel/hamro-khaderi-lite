from django.urls import path

from . import views

urlpatterns = [
    path("districts/", views.district_list, name="district-list"),
    path("districts/<int:pk>/spi/", views.district_spi, name="district-spi"),
    path("districts/<int:pk>/current/", views.district_current, name="district-current"),
    path("map/current/", views.map_current, name="map-current"),
    path("ingest/run/", views.ingest_run, name="ingest-run"),
    path("health/", views.health, name="health"),
]
