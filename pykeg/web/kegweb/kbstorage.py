import urllib.parse

from django.conf import settings
from django.core.files.storage import FileSystemStorage

try:
    from storages.backends.s3boto import S3BotoStorage
except ImportError:
    S3BotoStorage = None

from pykeg.backend import get_kegbot_backend

S3_STATIC_BUCKET = getattr(settings, "S3_STATIC_BUCKET", None)


class KegbotFileSystemStorage(FileSystemStorage):
    """Default storage backend that crafts absolute urls from KegbotSite.base_url.

    Since the storage backed is not a singleton within django request
    processing (and thus there's not a single object we can pre-configure
    with the base URL), this custom backend seems necessary.
    """

    def url(self, name):
        be = get_kegbot_backend()
        base_url = be.get_base_url()
        if not self.base_url.startswith(base_url):
            self.base_url = urllib.parse.urljoin(base_url, self.base_url)
        return super(KegbotFileSystemStorage, self).url(name)


if S3BotoStorage:

    class S3StaticStorage(S3BotoStorage):
        """Uses settings.S3_STATIC_BUCKET instead of AWS_STORAGE_BUCKET_NAME."""

        def __init__(self, *args, **kwargs):
            kwargs["bucket"] = S3_STATIC_BUCKET
            super(S3StaticStorage, self).__init__(*args, **kwargs)
