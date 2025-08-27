import logging
from django.forms import Select
import cloudinary
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError

logger = logging.getLogger(__name__)


class CloudinarySelectWidget(Select):
    """Select widget populated with Cloudinary image public IDs."""

    def __init__(self, attrs=None):
        choices = []
        try:
            response = cloudinary.api.resources(type="upload")
            resources = response.get("resources", [])
            choices = [(r["public_id"], r["public_id"]) for r in resources]
        except CloudinaryError as err:
            logger.exception("Cloudinary API error: %s", err)
            choices = [("", "No images found")]
        except Exception as err:  # Catch any unexpected issues
            logger.exception("Unexpected error while loading Cloudinary images: %s", err)
            choices = [("", "No images found")]
        super().__init__(attrs=attrs, choices=choices)