# Django
from django.contrib.contenttypes.models import ContentType

# Third party
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse

# Local application / specific library imports
from .conf.settings import (
    SIMPLE_NOTES_CUSTOM_CONTENT_TYPE_AND_ID,
    SIMPLE_NOTES_TOOLBAR_EDIT_TEXT,
    SIMPLE_NOTES_TOOLBAR_LIST_TEXT,
    SIMPLE_NOTES_TOOLBAR_MENU_TEXT,
)
from .models import SimpleNote


def get_content_type_and_id(request):
    """get contenttype + object id for each "type" of page (apphooks pages, then in last regular djangocms pages)"""

    found = False
    if SIMPLE_NOTES_CUSTOM_CONTENT_TYPE_AND_ID:
        object_ct, object_id = SIMPLE_NOTES_CUSTOM_CONTENT_TYPE_AND_ID(request)
        if object_ct is not None and object_id is not None:
            found = True

    if not found:
        # djangocms blog post (not the homepage of the blog, which should be treated as a regular cms page)
        if (
            request.resolver_match.app_name == "djangocms_blog"
            and "slug" in request.resolver_match.kwargs
        ):
            # Third party
            from djangocms_blog.models import Post

            post = Post.objects.get(
                translations__slug=request.resolver_match.kwargs["slug"]
            )
            object_ct = Post
            object_id = post.id
        # regular cms pages

        elif (
            "slug" in request.resolver_match.kwargs
            and request.resolver_match.kwargs["slug"] == ""
        ):
            # Third party
            from cms.models import Page

            # homepage
            page = Page.objects.get(
                title_set__language=request.LANGUAGE_CODE,
                title_set__publisher_is_draft=False,
                is_home=True,
            )
            object_ct = Page
            object_id = page.id
        else:
            # Third party
            from cms.models import Page

            # regular page
            if "slug" in request.resolver_match.kwargs:
                slug = request.resolver_match.kwargs["slug"].split("/")[-1]
            else:
                slug = request.resolver_match.route.split("/")
                if slug[-1] == r"\Z":
                    slug = slug[-2]
                else:
                    slug = slug[:-1]

                if type(slug) is list and len(slug) > 1:
                    slug = slug[-1]

            try:
                page = Page.objects.get(
                    title_set__language=request.LANGUAGE_CODE,
                    title_set__publisher_is_draft=False,
                    title_set__slug=slug,
                )
                object_ct = Page
                object_id = page.id
            except Page.DoesNotExist:
                # print(request.resolver_match.__dict__)  # debug
                # breakpoint()
                object_ct = None
                object_id = None

    if object_ct is not None:
        object_ct = ContentType.objects.get_for_model(object_ct)

    return (object_ct, object_id)


def get_edit_link(request):
    """
    Edit link will create an empty note if no one if found, and return the change url. That way, no need to reload the url in the toolbar!
    """
    ct, id = get_content_type_and_id(request)
    if ct and id:
        try:
            note = SimpleNote.objects.get(
                content_type=ct, object_id=id, language_code=request.LANGUAGE_CODE
            )
            return admin_reverse(
                "django_simple_notes_simplenote_change", args={note.id}
            )
        except SimpleNote.DoesNotExist:
            SimpleNote(
                content_type=ct,
                object_id=id,
                language_code=request.LANGUAGE_CODE,
                author=request.user,
            ).save()
            note = SimpleNote.objects.get(
                content_type=ct, object_id=id, language_code=request.LANGUAGE_CODE
            )
            return admin_reverse(
                "django_simple_notes_simplenote_change", args={note.id}
            )
    return None


@toolbar_pool.register
class SimpleNoteToolbar(CMSToolbar):
    watch_models = [SimpleNote]

    def populate(self):

        notes_menu = self.toolbar.get_or_create_menu(
            key="simple_notes_cms_integration",
            verbose_name=SIMPLE_NOTES_TOOLBAR_MENU_TEXT,
        )

        edit_link = get_edit_link(self.request)

        if edit_link:
            notes_menu.add_sideframe_item(
                name=SIMPLE_NOTES_TOOLBAR_EDIT_TEXT, url=edit_link
            )

        notes_menu.add_sideframe_item(
            name=SIMPLE_NOTES_TOOLBAR_LIST_TEXT,
            url=admin_reverse("django_simple_notes_simplenote_changelist"),
        )
