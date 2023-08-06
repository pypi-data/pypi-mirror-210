# Django
from django.conf import settings
from django.utils.translation import gettext_lazy as _

SIMPLE_NOTES_CUSTOM_CONTENT_TYPE_AND_ID = getattr(
    settings, "SIMPLE_NOTES_CUSTOM_CONTENT_TYPE_AND_ID", None
)

SIMPLE_NOTES_ADMIN_URLS = getattr(settings, "SIMPLE_NOTES_ADMIN_URLS", None)

SIMPLE_NOTES_TOOLBAR_MENU_TEXT = getattr(
    settings, "SIMPLE_NOTES_TOOLBAR_MENU_TEXT", _("Simple notes")
)

SIMPLE_NOTES_TOOLBAR_EDIT_TEXT = getattr(
    settings, "SIMPLE_NOTES_TOOLBAR_EDIT_TEXT", _("Edit note for current page")
)

SIMPLE_NOTES_TOOLBAR_LIST_TEXT = getattr(
    settings, "SIMPLE_NOTES_TOOLBAR_LIST_TEXT", _("Notes list")
)
