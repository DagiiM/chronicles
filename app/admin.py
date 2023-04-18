from django.contrib import admin
from django.conf import settings

class MyAdminSite(admin.AdminSite):
    site_header = settings.APP_NAME
    site_title = settings.APP_DOMAIN
    #site_url = settings.APP_TAGLINE
    index_title = settings.APP_TAGLINE
    #available_apps
    

class BaseAdmin(admin.ModelAdmin):
    """
    A mixin to restrict write access to the admin panel for users who are not staff
    or do not belong to the specified permission group.
    """
    staff_group_name = None  # set the group name in subclass

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            staff_group = Group.objects.get(name=self.staff_group_name)
            if not request.user.groups.filter(id=staff_group.id).exists():
                return qs.none()
        return qs

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            staff_group = Group.objects.get(name=self.staff_group_name)
            if not request.user.groups.filter(id=staff_group.id).exists():
                return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            staff_group = Group.objects.get(name=self.staff_group_name)
            if not request.user.groups.filter(id=staff_group.id).exists():
                return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            staff_group = Group.objects.get(name=self.staff_group_name)
            if not request.user.groups.filter(id=staff_group.id).exists():
                return False
        return super().has_delete_permission(request, obj)
