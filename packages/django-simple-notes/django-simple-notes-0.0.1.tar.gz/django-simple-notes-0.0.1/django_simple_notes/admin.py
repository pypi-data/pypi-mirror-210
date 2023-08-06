# Standard Library
from re import search

# Django
from django.contrib import admin
from django.forms import HiddenInput
from django.utils.html import mark_safe, strip_tags
from django.utils.translation import gettext_lazy as _

# Local application / specific library imports
from .conf.settings import SIMPLE_NOTES_ADMIN_URLS
from .models import SimpleNote


def url(obj):
    url = None
    if SIMPLE_NOTES_ADMIN_URLS:
        url = SIMPLE_NOTES_ADMIN_URLS(obj)

    if url is None:
        if obj.content_type.model == "page":
            # Third party
            from cms.models import Page

            url = Page.objects.get(id=obj.object_id).get_absolute_url()
        elif obj.content_type.model == "post":
            # Third party
            from djangocms_blog.models import Post

            url = Post.objects.get(id=obj.object_id).get_absolute_url()
        else:
            return obj

    return mark_safe(f"<a href='{url}' target='_blank'>{obj}</a>")


url.short_description = _("Url")


def beginning_content(obj):
    words = strip_tags(obj.note).split(" ")
    too_long = "" if len(words) < 16 else "..."
    return " ".join(words) + too_long


beginning_content.short_description = _("Beginning content")


def categories(obj):
    return ", ".join([category.name for category in obj.categories.all()])


categories.short_description = _("Categories")


def create_date(obj):
    return obj.create_date


create_date.short_description = _("Creation date")


def edit_date(obj):
    return obj.edit_date


edit_date.short_description = _("Edit date")


def on_list_view(request):
    return (
        search(r"\/django_simple_notes\/simplenote\/[0-9]+\/change\/", request.path)
        is None
    )


@admin.register(SimpleNote)
class SimpleNoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        beginning_content,
        categories,
        "language_code",
        "author",
        url,
        edit_date,
        create_date,
    )
    list_display_links = (
        "id",
        beginning_content,
    )
    list_filter = (
        "language_code",
        "create_date",
        "edit_date",
    )
    search_fields = (
        "categories__name",
        "note",
        "author__first_name",
        "author__last_name",
        "author__username",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if we're on list view, hide empty notes
        # (do not hide them in change view though, so user can access the object)
        if on_list_view(request):
            qs = qs.exclude(note__exact="")
        return qs

    def has_add_permission(self, request):
        # hide the "add" button on list view
        if on_list_view(request):
            return False
        return True

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["content_type"].widget = HiddenInput()
        form.base_fields["object_id"].widget = HiddenInput()
        form.base_fields["language_code"].widget = HiddenInput()
        form.base_fields["author"].widget = HiddenInput()
        return form
