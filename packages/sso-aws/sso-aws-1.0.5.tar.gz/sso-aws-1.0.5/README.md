# sso-aws - AWS SSO Login Utility 🔒

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/tom-r-o/sso-aws/blob/master/LICENSE)

## Overview 📝
The AWS SSO Login Utility is a Python package that simplifies the process of logging in to AWS Single Sign-On (SSO) and retrieving an AWS session for programmatic access. With just a single function call, `get_aws_session`, you can easily obtain an AWS session to use instead of `boto3`.

## Installation 🚀
You can install the package via pip:

```shell
pip install sso-aws
```

## Usage 💻
To use the utility, follow these steps:

1. Import the package:

   ```python
   from aws_sso_login import get_aws_session
   ```

2. Invoke the `get_aws_session` function with the required parameters:

   ```python
   session = get_aws_session(region='us-west-2', role_name='MyRole', account_id='123456789012', sso_endpoint='https://example.awsapps.com/start')
   ```

   Make sure to provide the correct values for `region`, `role_name`, `account_id`, and `sso_endpoint`.

3. Now you can use the returned `session` object instead of `boto3` to interact with AWS services:

   ```python
   # Example: List S3 buckets
   s3_client = session.client('s3')
   response = s3_client.list_buckets()
   print(response['Buckets'])
   ```

## Example 📃
Here's an example that demonstrates how to use the utility:

```python
from aws_sso_login import get_aws_session

region = 'us-west-2'
role_name = 'MyRole'
account_id = '123456789012'
sso_endpoint = 'https://example.awsapps.com/start'

session = get_aws_session(region=region, role_name=role_name, account_id=account_id, sso_endpoint=sso_endpoint)

# Use the session object for AWS API calls
s3_client = session.client('s3')
response = s3_client.list_buckets()
print(response['Buckets'])
```

## Contributing 👥
Contributions are welcome! If you find any issues or want to enhance this utility, please submit an issue or a pull request in the GitHub repository.

## License 📜
This project is licensed under the MIT License.

## Acknowledgements 👏
This utility was inspired by the need for a simpler way to log in to AWS SSO and retrieve AWS sessions programmatically. Special thanks to all the contributors and the open-source community.

## Contact ✉️
If you have any questions, suggestions, or feedback, feel free to reach out to the project maintainer at GitHub

---

Enjoy using the AWS SSO Login Utility! ✨