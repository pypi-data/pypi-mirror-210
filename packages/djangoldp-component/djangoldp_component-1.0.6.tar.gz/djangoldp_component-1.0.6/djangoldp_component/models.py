import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from djangoldp.models import Model
from rest_framework.exceptions import ValidationError


class Component(Model):
    friendly_name = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(
        max_length=255, blank=True, null=True, help_text="Component tag"
    )
    short_description = models.CharField(max_length=255, blank=True, null=True)
    creator = models.ForeignKey(
        get_user_model(),
        related_name="components",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    preferred_route = models.CharField(
        max_length=255, blank=True, null=True, default="false"
    )
    auto_import = models.BooleanField(
        default=False,
        help_text="Enable the experimental routing functionnality, does not require script declaration.",
    )
    auto_menu = models.BooleanField(
        default=False,
        help_text="Enable the experimental menu functionnality, require a solid-***-menu component.",
    )
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        try:
            return "{} ({})".format(self.friendly_name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit", "add"]
        auto_author = "creator"
        container_path = "/components/"
        depth = 1  # Do not serialize user
        lookup_field = "slug"
        nested_fields = ["parameters", "script_tags"]
        ordering = ["slug"]
        owner_field = "creator"
        owner_perms = ["inherit", "change", "delete"]
        # rdf_context = {
        #     "friendly_name": "sib:friendlyName",
        #     "name": "sib:tag",
        #     "short_description": "sib:shortDescription",
        #     "preferred_route": "sib:route",
        #     "auto_import": "sib:componentAutoImport",
        #     "auto_menu": "sib:componentAutoMenu",
        #     "creator": "foaf:user",
        #     "parameters": "ldp:Container",
        #     "script_tags": "ldp:Container",
        # }
        rdf_type = "sib:component"
        serializer_fields = [
            "@id",
            "friendly_name",
            "name",
            "short_description",
            "preferred_route",
            "auto_import",
            "auto_menu",
            "creator",
            "parameters",
            "script_tags",
        ]
        superuser_perms = ["view"]
        verbose_name = _("component")
        verbose_name_plural = _("components")


class ComponentScriptTag(Model):
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="script_tags",
        null=True,
        blank=True,
    )
    friendly_name = models.CharField(max_length=255, blank=True, null=True)
    src = models.URLField(max_length=255, blank=True, null=True)
    integrity = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        try:
            return "{} ({})".format(self.component.friendly_name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "script-tags/"
        owner_field = "component__creator"
        owner_perms = ["inherit", "change", "delete"]
        # rdf_context = {
        #     "component": "sib:component",
        #     "friendly_name": "sib:friendlyName",
        #     "src": "sib:componentScriptTagSrc",
        #     "integrity": "sib:componentScriptTagIntegrity",
        # }
        rdf_type = "sib:scriptTag"
        serializer_fields = ["@id", "friendly_name", "src", "integrity"]
        superuser_perms = ["inherit"]
        verbose_name = _("script tag")
        verbose_name_plural = _("script tags")


class Parameter(Model):
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="parameters",
        null=True,
        blank=True,
    )
    friendly_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    default = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        try:
            return "{} -> {} ({})".format(
                self.component.friendly_name, self.friendly_name, self.urlid
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "parameters/"
        owner_field = "component__creator"
        owner_perms = ["inherit", "change", "delete"]
        # rdf_context = {
        #     "friendly_name": "sib:friendlyName",
        #     "description": "sib:description",
        #     "component": "sib:component",
        #     "key": "sib:key",
        #     "default": "sib:value",
        # }
        rdf_type = "sib:parameter"
        serializer_fields = ["@id", "friendly_name", "description", "key", "default"]
        superuser_perms = ["inherit"]
        verbose_name = _("parameter")
        verbose_name_plural = _("parameters")


class Package(Model):
    friendly_name = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.CharField(max_length=255, blank=True, null=True)
    creator = models.ForeignKey(
        get_user_model(),
        related_name="packages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    distribution = models.CharField(max_length=255, blank=True, null=True)
    module = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        try:
            return "{} ({})".format(self.friendly_name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit", "add"]
        auto_author = "creator"
        container_path = "/packages/"
        depth = 0
        lookup_field = "slug"
        nested_fields = ["parameters"]
        ordering = ["slug"]
        owner_field = "creator"
        owner_perms = ["inherit", "change", "delete"]
        # rdf_context = {
        #     "friendly_name": "sib:friendlyName",
        #     "short_description": "sib:shortDescription",
        #     "creator": "foaf:user",
        #     "distribution": "sib:distribution",
        #     "module": "sib:module",
        #     "parameters": "ldp:Container",
        # }
        rdf_type = "sib:package"
        serializer_fields = [
            "@id",
            "friendly_name",
            "short_description",
            "creator",
            "distribution",
            "module",
            "parameters",
        ]
        superuser_perms = ["view"]
        verbose_name = _("package")
        verbose_name_plural = _("packages")


class ServerParameter(Model):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="parameters",
        null=True,
        blank=True,
    )
    friendly_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    default = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        try:
            return "{} -> {} ({})".format(
                self.package.friendly_name, self.friendly_name, self.urlid
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "server-parameters/"
        owner_field = "package__creator"
        owner_perms = ["inherit", "change", "delete"]
        # rdf_context = {
        #     "friendly_name": "sib:friendlyName",
        #     "description": "sib:description",
        #     "package": "sib:package",
        #     "key": "sib:key",
        #     "default": "sib:value",
        # }
        rdf_type = "sib:parameter"
        serializer_fields = ["@id", "friendly_name", "description", "key", "default"]
        superuser_perms = ["inherit"]
        verbose_name = _("server parameter")
        verbose_name_plural = _("server parameters")


@receiver(pre_save, sender=Component)
@receiver(pre_save, sender=Package)
def pre_save_slugify(sender, instance, **kwargs):
    if not instance.urlid or instance.urlid.startswith(settings.SITE_URL):
        if getattr(instance, Model.slug_field(instance)) != slugify(
            instance.friendly_name
        ):
            if (
                sender.objects.local()
                .filter(slug=slugify(instance.friendly_name))
                .count()
                > 0
            ):
                raise ValidationError(sender.__name__  + str(_(" must be unique")))
            setattr(
                instance, Model.slug_field(instance), slugify(instance.friendly_name)
            )
            setattr(instance, "urlid", "")
    else:
        # Is a distant object, generate a random slug
        setattr(instance, Model.slug_field(instance), uuid.uuid4().hex.upper()[0:8])
