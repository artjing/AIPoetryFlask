import os
ADMIN_USERNAME=os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD=os.environ.get('ADMIN_PASSOWORD')

#S3 BUCKETS CONFIG

INSTALLED_APPS = ('storages',)
AWS_ACCESS_KEY_ID = 'AKIAYNYF6BDMPB5XFYAN'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'aipoetry'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
