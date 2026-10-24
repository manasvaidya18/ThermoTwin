from rest_framework.routers import SimpleRouter

from .views import IncidentViewSet

router = SimpleRouter(trailing_slash=False)
router.register("incidents", IncidentViewSet, basename="incident")
urlpatterns = router.urls
