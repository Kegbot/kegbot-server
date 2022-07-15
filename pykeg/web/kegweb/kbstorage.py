import urllib.parse

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from pykeg.web.util import get_base_url

try:
    from storages.backends.s3boto import S3BotoStorage
except ImportError:
    S3BotoStorage = None

S3_STATIC_BUCKET = getattr(settings, "S3_STATIC_BUCKET", None)


class KegbotFileSystemStorage(FileSystemStorage):
    """Default storage backend that crafts absolute urls from KegbotSite.base_url.

    Since the storage backed is not a singleton within django request
    processing (and thus there's not a single object we can pre-configure
    with the base URL), this custom backend seems necessary.
    """

    def url(self, name):
        base_url = get_base_url()
        if not self.base_url.startswith(base_url):
            self.base_url = urllib.parse.urljoin(base_url, self.base_url)
        return super(KegbotFileSystemStorage, self).url(name)


if S3BotoStorage:

    class S3StaticStorage(S3BotoStorage):
        """Uses settings.S3_STATIC_BUCKET instead of AWS_STORAGE_BUCKET_NAME."""

        def __init__(self, *args, **kwargs):
            kwargs["bucket"] = S3_STATIC_BUCKET
            super(S3StaticStorage, self).__init__(*args, **kwargs)
