import json

import wagtail.admin.rich_text.editors.draftail.features as draftail_features

from django.urls import include, path, reverse
from django.utils.safestring import mark_safe
from django.views.i18n import JavaScriptCatalog
from wagtail import hooks

from .prompts import get_prompts
from .views import process


@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = [
        path(
            "jsi18n/",
            JavaScriptCatalog.as_view(packages=["wagtail_ai"]),
            name="javascript_catalog",
        ),
        path(
            "process/",
            process,
            name="process",
        ),
    ]

    return [
        path(
            "ai/",
            include(
                (urls, "wagtail_ai"),
                namespace="wagtail_ai",
            ),
        )
    ]


class ControlFeature(draftail_features.Feature):
    def construct_options(self, options):
        return None


@hooks.register("register_rich_text_features")
def register_ai_feature(features):
    features.default_features.append("ai")
    features.register_editor_plugin(
        "draftail",
        "ai",
        ControlFeature(
            js=["wagtail_ai/wagtail-ai.js"], css={"all": ["wagtail_ai/main.css"]}
        ),
    )


@hooks.register("insert_editor_js")
def ai_editor_js():
    prompt_json = json.dumps([prompt.as_dict() for prompt in get_prompts()])
    process_url = reverse("wagtail_ai:process")

    return mark_safe(
        f"""
        <script>
            window.WAGTAIL_AI_PROCESS_URL = "{process_url}";
            window.WAGTAIL_AI_PROMPTS = {prompt_json};
        </script>
        """
    )
