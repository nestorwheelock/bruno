from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.conf.urls.i18n import i18n_patterns

# Non-localized URLs (admin, media, i18n)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # Language switching
    # Serve media files (user uploads) in all environments
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Localized URLs (will be prefixed with /en/, /es/, etc.)
urlpatterns += i18n_patterns(
    path("", include("fundraiser.urls")),
    path("tracker/", include("health.urls")),
    prefix_default_language=False,  # Don't require /en/ for default language
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
