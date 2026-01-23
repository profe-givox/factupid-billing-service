from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .cfdi_viewsets import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
# ruta para los viewsets de la app Console
router.register(r'customers', CustomerViewSet)
router.register(r'seleted-services',SelectedServiceViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'service-plans', ServicePlanViewSet)
router.register(r'supplier-stamps', SupplierStampViewSet)
router.register(r'plans', PlanViewSet)
router.register(r'post', PostViewSet)
router.register(r'user-services', UserServiceViewSet)
# ruta para los viewsets de permisos y grupos de Django
router.register(r'auth/permissions', UserPermissionViewSet, basename='user-permissions')

# Rutas para los viewsets de la app CFDI
router.register(r'fiscal-informations', FiscalInformationViewSet, basename='fiscal-information')
router.register(r'digital-stamp-certificates', DigitalStampCertificateViewSet, basename='digital-stamp-certificate')
router.register(r'emited-receipts', EmitedReceiptViewSet, basename='emited-receipt')
router.register(r'electronic-invoices', ElectronicInvoiceViewSet, basename='electronic-invoice')
router.register(r'electronic-invoice-drafts', ElectronicInvoiceDraftViewSet, basename='electronic-invoice-draft')
router.register(r'issuers', IssuerCFDIViewSet, basename='issuer-cfdi')
router.register(r'receivers', ReceiverCFDIViewSet, basename='receiver-cfdi')
router.register(r'related-vouchers', RelatedVouchersViewSet, basename='related-voucher')
router.register(r'origin-cfdi', OriginCFDIViewSet, basename='origin-cfdi')
router.register(r'fiscal-legends', FiscalLegendViewSet, basename='fiscal-legend')
router.register(r'concepts', ConceptViewSet, basename='concept')
router.register(r'taxes', TaxViewSet, basename='tax') # For CFDI tax nodes, not the catalog
router.register(r'global-informations', GlobalInformationViewSet, basename='global-information')
router.register(r'payment-informations', PaymentInformationViewSet, basename='payment-information')

# Catalogs
router.register(r'catalogs/countries', CountryViewSet, basename='catalog-country')
router.register(r'catalogs/tax-regimes', TaxRegimeViewSet, basename='catalog-taxregime')
router.register(r'catalogs/cfdi-uses', CFDIUseViewSet, basename='catalog-cfdiuse')
router.register(r'catalogs/cfdi-versions', CFDIVersionViewSet, basename='catalog-cfdiversion')
router.register(r'catalogs/relation-types', RelationTypeViewSet, basename='catalog-relationtype')
router.register(r'catalogs/unit-keys', UnitKeyViewSet, basename='catalog-unitkey')
router.register(r'catalogs/product-service-keys', ProductServiceKeyViewSet, basename='catalog-productservicekey')
router.register(r'catalogs/tax-objects', TaxObjectViewSet, basename='catalog-taxobject')
router.register(r'catalogs/months', MonthViewSet, basename='catalog-month')
router.register(r'catalogs/periodicities', PeriodicityViewSet, basename='catalog-periodicity')
router.register(r'catalogs/payment-forms', PaymentMethodViewSet, basename='catalog-paymentform') # Corresponds to FormaPago
router.register(r'catalogs/payment-ways', PaymentWayViewSet, basename='catalog-paymentway') # Corresponds to MetodoPago
router.register(r'catalogs/currencies', CurrencyViewSet, basename='catalog-currency')
router.register(r'catalogs/voucher-types', VoucherTypeViewSet, basename='catalog-vouchertype') # Corresponds to TipoComprobante
# Newly added catalog endpoints
router.register(r'catalogs/states', StateViewSet, basename='catalog-state')
router.register(r'catalogs/localities', LocalityViewSet, basename='catalog-locality')
router.register(r'catalogs/municipalities', MunicipalityViewSet, basename='catalog-municipality')
router.register(r'catalogs/postal-codes', PostalCodeViewSet, basename='catalog-postalcode')
router.register(r'catalogs/neighborhoods', NeighborhoodViewSet, basename='catalog-neighborhood')
router.register(r'catalogs/tax-catalogs', TaxCatalogViewSet, basename='catalog-taxcatalog') # Corresponds to Impuesto catalog
router.register(r'catalogs/factor-types', FactorTypeViewSet, basename='catalog-factortype')
router.register(r'catalogs/tax-rates-fees', TaxRateOrFeeViewSet, basename='catalog-taxrateorfee')
router.register(r'catalogs/exportations', ExportationViewSet, basename='catalog-exportation')
router.register(r'catalogs/customs', CustomsViewSet, basename='catalog-customs')
router.register(r'catalogs/customs-patents', CustomsPatentViewSet, basename='catalog-customspatent')


# User and Tax Information
router.register(r'cfdi-users', CFDIUserViewSet, basename='cfdiuser') # For admin or internal management
router.register(r'tax-information', TaxInformationViewSet, basename='taxinformation')
router.register(r'digital-seal-certificates', DigitalSealCertificateViewSet, basename='digitalsealcertificate')

# Vouchers (before stamping)
router.register(r'voucher', VoucherViewSet, basename='voucher')

# CFDI Issuance (actions related to issuing new CFDIs)
router.register(r'cfdi-issuance', CFDIIssuanceViewSet, basename='cfdi-issuance')

# Issued (stamped) Vouchers
router.register(r'issued-vouchers', IssuedVoucherViewSet, basename='issued-voucher')


# Billing Entities (Payroll, E-Invoice, Waybill) - for managing drafts/templates
router.register(r'payroll-invoices', PayrollInvoice12ViewSet, basename='payroll-invoice')
router.register(r'e-invoices', EInvoiceViewSet, basename='e-invoice') # For managing e-invoice templates or base data
router.register(r'e-invoice-drafts', EInvoiceDraftViewSet, basename='e-invoice-draft')
router.register(r'waybill-transfer-invoices', WaybillTransferInvoiceViewSet, basename='waybill-transfer-invoice')


urlpatterns = [
    path('', include(router.urls)),
    # Endpoint para obtener tokens
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Endpoint para refrescar tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Endpoint para seleccionar un servicio y plan
    path('select-service/', SeleccionServicioAPIView.as_view(), name='select-service'),
]
