from setuptools import setup

setup(name='papai_public',
      version='0.1.16',
      description="Public papAI minio writer/reader",
      author="Datategy",
      py_modules=['papai_minio'],
      package_dir={'': 'src'},
      install_requires=["pyarrow", "minio", "loguru", "azure-storage-blob", "google-cloud-storage", "boto3"]
)