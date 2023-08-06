from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from .models import (
    Component,
    Parameter,
    ComponentScriptTag,
    Package,
    ServerParameter,
)


class EmptyAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


class ParameterInline(admin.TabularInline):
    model = Parameter
    exclude = ("urlid", "is_backlink", "allow_create_backlink")
    extra = 0


class ComponentScriptTagInline(admin.TabularInline):
    model = ComponentScriptTag
    exclude = ("urlid", "is_backlink", "allow_create_backlink")
    extra = 0


class ServerParameterInline(admin.TabularInline):
    model = ServerParameter
    exclude = ("urlid", "is_backlink", "allow_create_backlink")
    extra = 0


class ComponentAdmin(DjangoLDPAdmin):
    list_display = ("urlid", "friendly_name", "short_description")
    exclude = ("urlid", "slug", "is_backlink", "allow_create_backlink")
    inlines = [ComponentScriptTagInline, ParameterInline]
    search_fields = ["urlid", "friendly_name", "name", "parameters__parameter__name"]
    ordering = ["urlid"]


class PackageAdmin(DjangoLDPAdmin):
    list_display = ("urlid", "friendly_name", "short_description")
    exclude = ("urlid", "slug", "is_backlink", "allow_create_backlink")
    inlines = [ServerParameterInline]
    search_fields = ["urlid", "friendly_name", "parameters__parameter__name"]
    ordering = ["urlid"]


admin.site.register(Component, ComponentAdmin)
admin.site.register(Parameter, EmptyAdmin)
admin.site.register(ComponentScriptTag, EmptyAdmin)
admin.site.register(ServerParameter, EmptyAdmin)
admin.site.register(Package, PackageAdmin)
