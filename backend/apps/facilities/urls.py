from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)
router.register("facilities", views.FacilityViewSet, basename="facility")
router.register("units", views.StorageUnitViewSet, basename="unit")
router.register("vaccines", views.VaccineViewSet, basename="vaccine")
router.register("stock", views.StockItemViewSet, basename="stock")
router.register("technicians", views.TechnicianViewSet, basename="technician")
urlpatterns = router.urls
