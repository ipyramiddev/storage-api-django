import os
import mimetypes

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.utils.encoding import force_unicode, smart_str

try:
    from boto.s3.connection import S3Connection, S3ResponseError
    from boto.s3.key import Key
except ImportError:
    raise ImproperlyConfigured, "Could not load Boto's S3 bindings.\
    \nSee http://code.google.com/p/boto/"

ACCESS_KEY_NAME     = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
SECRET_KEY_NAME     = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
HEADERS             = getattr(settings, 'AWS_HEADERS', {})
STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
AUTO_CREATE_BUCKET  = getattr(settings, 'AWS_AUTO_CREATE_BUCKET', True)
DEFAULT_ACL         = getattr(settings, 'AWS_DEFAULT_ACL', 'public-read')
BUCKET_ACL          = getattr(settings, 'AWS_BUCKET_ACL', DEFAULT_ACL)
QUERYSTRING_AUTH    = getattr(settings, 'AWS_QUERYSTRING_AUTH', True)
QUERYSTRING_EXPIRE  = getattr(settings, 'AWS_QUERYSTRING_EXPIRE', 3600)
REDUCED_REDUNDANCY  = getattr(settings, 'AWS_REDUCED_REDUNDANCY', False)
LOCATION            = getattr(settings, 'AWS_LOCATION', '')
CUSTOM_DOMAIN       = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
SECURE_URLS         = getattr(settings, 'AWS_S3_SECURE_URLS', True)
FILE_NAME_CHARSET   = getattr(settings, 'AWS_S3_FILE_NAME_CHARSET', 'utf-8')
IS_GZIPPED          = getattr(settings, 'AWS_IS_GZIPPED', False)
GZIP_CONTENT_TYPES  = getattr(settings, 'GZIP_CONTENT_TYPES', (
    'text/css',
    'application/javascript',
    'application/x-javascript'
))

if IS_GZIPPED:
    from gzip import GzipFile

def safe_join(base, *paths):
    """
    A version of django.utils._os.safe_join for S3 paths.

    Joins one or more path components to the base path component intelligently.
    Returns a normalized version of the final path.

    The final path must be located inside of the base path component (otherwise
    a ValueError is raised).
    
    Paths outside the base path indicate a possible security sensitive operation.
    """
    from urlparse import urljoin
    base_path = force_unicode(base)
    paths = map(lambda p: force_unicode(p), paths)
    final_path = urljoin(base_path + ("/" if not base_path.endswith("/") else ""), *paths)
    # Ensure final_path starts with base_path and that the next character after
    # the final path is '/' (or nothing, in which case final_path must be
    # equal to base_path).
    base_path_len = len(base_path)
    if not final_path.startswith(base_path) \
       or final_path[base_path_len:base_path_len+1] not in ('', '/'):
        raise ValueError('the joined path is located outside of the base path'
                         ' component')
    return final_path

class S3BotoStorage(Storage):
    """Amazon Simple Storage Service using Boto"""
    
    def __init__(self, bucket=STORAGE_BUCKET_NAME, access_key=None,
                       secret_key=None, bucket_acl=BUCKET_ACL, acl=DEFAULT_ACL, headers=HEADERS,
                       gzip=IS_GZIPPED, gzip_content_types=GZIP_CONTENT_TYPES,
                       querystring_auth=QUERYSTRING_AUTH, querystring_expire=QUERYSTRING_EXPIRE,
                       reduced_redundancy=REDUCED_REDUNDANCY,
                       custom_domain=CUSTOM_DOMAIN, secure_urls=SECURE_URLS,
                       location=LOCATION, file_name_charset=FILE_NAME_CHARSET):
        self.bucket_acl = bucket_acl
        self.bucket_name = bucket
        self.acl = acl
        self.headers = headers
        self.gzip = gzip
        self.gzip_content_types = gzip_content_types
        self.querystring_auth = querystring_auth
        self.querystring_expire = querystring_expire
        self.reduced_redundancy = reduced_redundancy
        self.custom_domain = custom_domain
        self.secure_urls = secure_urls
        self.location = location or ''
        self.location = self.location.lstrip('/')
        self.file_name_charset = file_name_charset
        
        if not access_key and not secret_key:
             access_key, secret_key = self._get_access_keys()
        
        self.connection = S3Connection(access_key, secret_key)

    @property
    def bucket(self):
        if not hasattr(self, '_bucket'):
            self._bucket = self._get_or_create_bucket(self.bucket_name)
        return self._bucket
    
    def _get_access_keys(self):
        access_key = ACCESS_KEY_NAME
        secret_key = SECRET_KEY_NAME
        if (access_key or secret_key) and (not access_key or not secret_key):
            access_key = os.environ.get(ACCESS_KEY_NAME)
            secret_key = os.environ.get(SECRET_KEY_NAME)
        
        if access_key and secret_key:
            # Both were provided, so use them
            return access_key, secret_key
        
        return None, None
    
    def _get_or_create_bucket(self, name):
        """Retrieves a bucket if it exists, otherwise creates it."""
        try:
            return self.connection.get_bucket(name)
        except S3ResponseError, e:
            if AUTO_CREATE_BUCKET:
                bucket = self.connection.create_bucket(name)
                bucket.set_acl(self.bucket_acl)
                return bucket
            raise ImproperlyConfigured, ("Bucket specified by "
            "AWS_STORAGE_BUCKET_NAME does not exist. Buckets can be "
            "automatically created by setting AWS_AUTO_CREATE_BUCKET=True")
    
    def _clean_name(self, name):
        # Useful for windows' paths
        return os.path.normpath(name).replace('\\', '/')

    def _normalize_name(self, name):
        try:
            return safe_join(self.location, name).lstrip('/')
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)

    def _encode_name(self, name):
        return smart_str(name, encoding=self.file_name_charset)

    def _compress_content(self, content):
        """Gzip a given string."""
        zbuf = StringIO()
        zfile = GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
        zfile.write(content.read())
        zfile.close()
        content.file = zbuf
        return content
        
    def _open(self, name, mode='rb'):
        name = self._normalize_name(self._clean_name(name))
        f = S3BotoStorageFile(name, mode, self)
        if not f.key:
            raise IOError('File does not exist: %s' % name)
        return f
    
    def _save(self, name, content):
        cleaned_name = self._clean_name(name)
        name = self._normalize_name(cleaned_name)
        headers = self.headers
        content_type = getattr(content,'content_type', mimetypes.guess_type(name)[0] or Key.DefaultContentType)

        if self.gzip and content_type in self.gzip_content_types:
            content = self._compress_content(content)
            headers.update({'Content-Encoding': 'gzip'})

        content.name = cleaned_name
        k = self.bucket.get_key(self._encode_name(name))
        if not k:
            k = self.bucket.new_key(self._encode_name(name))

        k.set_metadata('Content-Type',content_type)
        k.set_contents_from_file(content, headers=headers, policy=self.acl, 
                                 reduced_redundancy=self.reduced_redundancy)
        return cleaned_name
    
    def delete(self, name):
        name = self._normalize_name(self._clean_name(name))
        self.bucket.delete_key(self._encode_name(name))
    
    def exists(self, name):
        name = self._normalize_name(self._clean_name(name))
        k = self.bucket.new_key(self._encode_name(name))
        return k.exists()
    
    def listdir(self, name):
        name = self._normalize_name(self._clean_name(name))
        dirlist = self.bucket.list(self._encode_name(name))
        files = []
        dirs = set()
        base_parts = name.split("/") if name else []
        for item in dirlist:
            parts = item.name.split("/")
            parts = parts[len(base_parts):]
            if len(parts) == 1:
                # File 
                files.append(parts[0])
            elif len(parts) > 1:
                # Directory
                dirs.add(parts[0])
        return list(dirs),files

    def size(self, name):
        name = self._normalize_name(self._clean_name(name))
        return self.bucket.get_key(self._encode_name(name)).size
    
    def url(self, name):
        name = self._normalize_name(self._clean_name(name))
        if self.custom_domain:
            return "%s://%s/%s" % ('https' if self.secure_urls else 'http', self.custom_domain, name)
        else:
            return self.connection.generate_url(self.querystring_expire, method='GET', \
                    bucket=self.bucket.name, key=self._encode_name(name), query_auth=self.querystring_auth, \
                    force_http=not self.secure_urls)

    def get_available_name(self, name):
        """ Overwrite existing file with the same name. """
        name = self._clean_name(name)
        return name


class S3BotoStorageFile(File):
    def __init__(self, name, mode, storage):
        self._storage = storage
        self.name = name[len(self._storage.location):].lstrip('/')
        self._mode = mode
        self.key = storage.bucket.get_key(self._storage._encode_name(name))
        self._is_dirty = False
        self._file = None

    @property
    def size(self):
        return self.key.size

    @property
    def file(self):
        if self._file is None:
            self._file = StringIO()
            if 'r' in self._mode:
                self._is_dirty = False
                self.key.get_contents_to_file(self._file)
                self._file.seek(0)
        return self._file

    def read(self, *args, **kwargs):
        if 'r' not in self._mode:
            raise AttributeError("File was not opened in read mode.")
        return super(S3BotoStorageFile, self).read(*args, **kwargs)

    def write(self, *args, **kwargs):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self._is_dirty = True
        return super(S3BotoStorageFile, self).write(*args, **kwargs)

    def close(self):
        if self._is_dirty:
            self.key.set_contents_from_file(self._file, headers=self._storage.headers, policy=self._storage.acl)
        self.key.close()
