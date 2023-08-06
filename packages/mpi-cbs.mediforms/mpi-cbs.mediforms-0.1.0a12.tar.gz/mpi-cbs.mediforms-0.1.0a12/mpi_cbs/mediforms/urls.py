from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.urls import include, path, register_converter

from mpi_cbs.mediforms import views


class MethodConverter:
    regex = 'mrt|mrt7tptx|mrtbegleitung|mrtconnectom|tms'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(MethodConverter, 'method')


urlpatterns = [
    path('', views.Index.as_view(), name='index'),

    path('login/', LoginView.as_view(template_name='mediforms/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path(r'i18n/', include('django.conf.urls.i18n')),

    path('form/<uuid:token>/', views.FormView.as_view(), name='form'),
    path('form/complete/', views.FormCompleteView.as_view(), name='form-complete'),

    path(
        'mrt/erklaerung-datenspeicherung-und-nutzung/',
        TemplateView.as_view(template_name='mediforms/pages/data_storage_and_usage_consent_mrt.html'),
        name='data-storage-and-usage-consent-mrt',
    ),
    path(
        'mrtbegleitung/erklaerung-datenspeicherung-und-nutzung/',
        TemplateView.as_view(template_name='mediforms/pages/data_storage_and_usage_consent_mrtbegleitung.html'),
        name='data-storage-and-usage-consent-mrtbegleitung',
    ),
    path(
        '<method:method>/einwilligung-datenspeicherung/',
        views.DataStorageConsentView.as_view(),
        name='data-storage-consent',
    ),
    path(
        '<method:method>/einwilligung-untersuchung/',
        TemplateView.as_view(template_name='mediforms/pages/exploration_consent.html'),
        name='exploration-consent',
    ),
    path(
        '<method:method>/informationtext/',
        TemplateView.as_view(template_name='mediforms/pages/information_text.html'),
        name='information-text',
    ),

    path('tokens/', views.TokenListView.as_view(), name='token-list'),
]
