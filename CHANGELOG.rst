django-storages change log
==========================

1.1.7 (2013-03-20)
******************

* Listing of huge buckets on S3 is now prevented by using the prefix argument to boto's list() method
* Initial support for Windows Azure Storage
* Switched to useing boto's parse_ts date parser getting last modified info when using S3boto backend
* Fixed key handling in S3boto and Google Storage backends
* Account for lack of multipart upload in Google Storage backend
* Fixed seek() issue when using AWS_IS_GZIPPED by darkness51 with pull-request `#50`_
* Improvements to S3BotoStorage and GSBotoStorage

.. _#50: https://bitbucket.org/david/django-storages/pull-request/50/

1.1.6 (2013-01-06)
******************

* Merged many changes from Jannis Leidel (mostly regarding gzipping)
* Fixed tests by Ian Lewis
* Added support for Google Cloud Storage backend by Jannis Leidel
* Updated license file by Dan Loewenherz, fixes `#133`_ with pull-request `#44`_
* Set Content-Type header for use in upload_part_from_file by Gerardo Curiel
* Pass the rewind parameter to Boto's set_contents_from_file method by Jannis Leidel with pull-request `#45`_
* Fix for FTPStorageFile close() method by Mathieu Comandon with pull-request `#43`_
* Minor refactoring by Oktay Sancak with pull-request `#48`_
* Ungzip on download based on Content-Encoding by Gavin Wahl with pull-request `#46`_
* Add support for S3 server-side encryption by Tobias McNulty with pull-request `#17`_
* Add an optional setting to the boto storage to produce protocol-relative URLs, fixes `#105`_

.. _#133: https://bitbucket.org/david/django-storages/issue/133/license-file-refers-to-incorrect-project
.. _#44: https://bitbucket.org/david/django-storages/pull-request/44/
.. _#45: https://bitbucket.org/david/django-storages/pull-request/45/
.. _#43: https://bitbucket.org/david/django-storages/pull-request/43/
.. _#48: https://bitbucket.org/david/django-storages/pull-request/48/
.. _#46: https://bitbucket.org/david/django-storages/pull-request/46/
.. _#17: https://bitbucket.org/david/django-storages/pull-request/17/
.. _#105: https://bitbucket.org/david/django-storages/issue/105/add-option-to-produce-protocol-relative


1.1.5 (2012-07-18)
******************

* Merged pull request `#36`_ from freakboy3742 Keith-Magee, improvements to Apache Libcloud backend and docs
* Merged pull request `#35`_ from atodorov, allows more granular S3 access settings
* Add support for SSL in Rackspace Cloudfiles backend
* Fixed the listdir() method in s3boto backend, fixes `#57`_
* Added base url tests for safe_join in s3boto backend
* Merged pull request `#20`_ from alanjds, fixed SuspiciousOperation warning if AWS_LOCATION ends with '/'
* Added FILE_BUFFER_SIZE setting to s3boto backend
* Merged pull request `#30`_ from pendletongp, resolves `#108`_, `#109`_ and `#110`_
* Updated the modified_time() method so that it doesn't require dateutil. fixes `#111`_
* Merged pull request `#16`_ from chamal, adds Apache Libcloud backend
* When preloading the S3 metadata make sure we reset the files key during saving to prevent stale metadata
* Merged pull request `#24`_ from tobias.mcnulty, fixes bug where s3boto backend returns modified_time in wrong time zone
* Fixed HashPathStorage.location to no longer use settings.MEDIA_ROOT
* Remove download_url from setup file so PyPI dist is used

.. _#36: https://bitbucket.org/david/django-storages/pull-request/36/
.. _#35: https://bitbucket.org/david/django-storages/pull-request/35/
.. _#57: https://bitbucket.org/david/django-storages/issue/57
.. _#20: https://bitbucket.org/david/django-storages/pull-request/20/
.. _#30: https://bitbucket.org/david/django-storages/pull-request/30/
.. _#108: https://bitbucket.org/david/django-storages/issue/108
.. _#109: https://bitbucket.org/david/django-storages/issue/109
.. _#110: https://bitbucket.org/david/django-storages/issue/110
.. _#111: https://bitbucket.org/david/django-storages/issue/111
.. _#16: https://bitbucket.org/david/django-storages/pull-request/16/
.. _#24: https://bitbucket.org/david/django-storages/pull-request/24/

1.1.4 (2012-01-06)
******************

* Added PendingDeprecationWarning for mosso backend
* Merged pull request `#13`_ from marcoala, adds ``SFTP_KNOWN_HOST_FILE`` setting to SFTP storage backend
* Merged pull request `#12`_ from ryankask, fixes HashPathStorage tests that delete remote media
* Merged pull request `#10`_ from key, adds support for django-mongodb-engine 0.4.0 or later, fixes GridFS file deletion bug
* Fixed S3BotoStorage performance problem calling modified_time()
* Added deprecation warning for s3 backend, refs `#40`_
* Fixed CLOUDFILES_CONNECTION_KWARGS import error, fixes `#78`_
* Switched to sphinx documentation, set official docs up on http://django-storages.rtfd.org/
* HashPathStorage uses self.exists now, fixes `#83`_

.. _#13: https://bitbucket.org/david/django-storages/pull-request/13/a-version-of-sftp-storage-that-allows-you
.. _#12: https://bitbucket.org/david/django-storages/pull-request/12/hashpathstorage-tests-deleted-my-projects
.. _#10: https://bitbucket.org/david/django-storages/pull-request/10/support-django-mongodb-engine-040
.. _#40: https://bitbucket.org/david/django-storages/issue/40/deprecate-s3py-backend
.. _#78: https://bitbucket.org/david/django-storages/issue/78/import-error
.. _#83: https://bitbucket.org/david/django-storages/issue/6/symlinkorcopystorage-new-custom-storage

1.1.3 (2011-08-15)
******************

* Created this lovely change log
* Fixed `#89`_: broken StringIO import in CloudFiles backend
* Merged `pull request #5`_: HashPathStorage path bug

.. _#89: https://bitbucket.org/david/django-storages/issue/89/112-broke-the-mosso-backend
.. _pull request #5: https://bitbucket.org/david/django-storages/pull-request/5/fixed-path-bug-and-added-testcase-for

