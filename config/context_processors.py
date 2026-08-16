from .translations import DEFAULT_LANGUAGE, LANGUAGES


def language(request):
    return {
        "LANG": request.session.get("lang", DEFAULT_LANGUAGE),
        "AVAILABLE_LANGUAGES": LANGUAGES,
    }
