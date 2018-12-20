from django_giropay import settings as django_giropay_settings


def build_giropay_full_uri(url):
    if url.startswith('/'):
        url = '{0}{1}'.format(django_giropay_settings.GIROPAY_ROOT_URL, url)
    return url
