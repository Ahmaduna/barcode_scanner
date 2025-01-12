from django.urls import path
from .views import scan_page, scan_barcode

urlpatterns = [
    path('scan/', scan_page, name='scan_page'),  # Page pour scanner le QR code
    path('scan/<str:barcode>/', scan_barcode, name='scan_barcode'),  # Recherche par code-barres
    
]
