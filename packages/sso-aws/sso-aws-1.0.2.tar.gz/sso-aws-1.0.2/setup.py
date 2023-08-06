from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='sso-aws',
    version='1.0.2',
    author='Tom R',
    description='Login to AWS SSO with this simple utility - just invoke get_aws_session '
                'with: region, role_name, account_id, sso_endpoint. Then use the returned aws session '
                'instead of boto3',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'boto3',
    ],
)
