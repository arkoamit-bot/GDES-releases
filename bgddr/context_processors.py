"""Template context processors for BGDDR."""
from .version import __version__


def app_version(request):
    """Expose the running application version to every template as ``APP_VERSION``
    so the UI can show which build the clinician is on."""
    return {"APP_VERSION": __version__}
