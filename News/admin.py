from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.template.response import TemplateResponse

from .models import NewsArticle, SavedArticle, UserProfile


class SiyasiAdminSite(AdminSite):
    site_header = "Siyasi News Admin"
    site_title = "Siyasi News Admin"
    index_title = "Administration"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def login(self, request, extra_context=None):
        if request.user.is_authenticated and not self.has_permission(request):
            context = {
                **self.each_context(request),
                "title": "Access denied",
            }
            return TemplateResponse(request, "admin/denied.html", context, status=403)
        return super().login(request, extra_context)


siyasi_admin_site = SiyasiAdminSite(name="siyasi_admin")


@admin.register(User, site=siyasi_admin_site)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(Group, site=siyasi_admin_site)
class CustomGroupAdmin(GroupAdmin):
    pass


@admin.register(NewsArticle, site=siyasi_admin_site)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at")
    search_fields = ("title", "content")
    list_filter = ("published_at",)
    ordering = ("-published_at",)


@admin.register(SavedArticle, site=siyasi_admin_site)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("user__username", "article__title")
    ordering = ("-saved_at",)


@admin.register(UserProfile, site=siyasi_admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location")
    search_fields = ("user__username", "location")
