# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['palantir_oauth_client']

package_data = \
{'': ['*']}

install_requires = \
['oauthlib>=3.2.2,<4.0.0',
 'requests-oauthlib>=1.3.1,<2.0.0',
 'requests>=2.28.2,<3.0.0']

setup_kwargs = {
    'name': 'palantir-oauth-client',
    'version': '1.5.6',
    'description': 'OAuth2 client for Palantir Foundry',
    'long_description': 'Palantir OAuth Client\n==============\n\nA library for performing OAuth2 authentication with Multipass in order to obtain credentials for querying Foundry APIs.\n\nThis library supports two modes of operation for the [Authorization code](https://oauth.net/2/grant-types/authorization-code/)\nOAuth2 flow:\n\n1. Command line prompt: A user will be prompted to navigate to Foundry and enter the resulting ``authorization_code``\n   in their console after successful authentication.\n   \n2. Local webserver: A local webserver will be created to receive the redirect after successful authentication. The token\n   exchange will be performed automatically.\n\nIf the ``offline_access`` scope is specified, the credential will additionally contain a refresh token. When loading\ncached credentials (see below), the refresh token will be used to update invalid or expired credentials. In the case\ncredentials cannot be obtained the user will be prompted to log in as above.\n\nUsage\n-----\nUse the ``palantir_oauth_client.get_user_credentials()`` function to authenticate to Foundry APIs. \n\n```python\nimport requests\nfrom palantir_oauth_client import get_user_credentials\n\nhostname = "127.0.0.1:8080"\nclient_id = "f5496be223e4db85c6a7c99bc5c2d81a"\ncredentials = get_user_credentials(["offline_access"], hostname, client_id)\n\nheaders = {"Authorization": "Bearer " + credentials.token}\nresponse = requests.get(f"https://{hostname}/multipass/api/me", headers=headers)\nprint("Hello, {}!".format(response.json().get("username")))\n```\n\n## Client Registration\n\nA third-party client application needs to have been created in Multipass and the ``client_id`` provided when calling\n``palantir_oauth_client.get_user_credentials()``. This client should be registered as a _Public client_ (native or single-page\napplication) when it is not possible to securely store the ``client_secret``. The library uses the\n[PKCE OAuth2 extension](https://oauth.net/2/pkce/) for all requests regardless of the type of client that has been\nregistered.\n\nThe following redirect URIs should use be specified for each mode of operation:\n\n1. Command line prompt: ``https://<hostname>/multipass/api/oauth2/callback``\n\n2. Local webserver: ``http://127.0.0.1/``\n\n## Caching\n\nWhen obtaining credentials using ``palantir_oauth_client.get_user_credentials()`` you may specify a\n``palantir_oauth_client.cache.CredentialsCache``. There are three implementations:\n\n1. ``palantir_oauth_client.cache.READ_WRITE`` (default): A read-write cache that will persist credentials to disk when\n   ``offline_access`` scope is requested. The cached refresh tokens will be used when obtaining credentials where\n   possible to avoid explicit re-authentication.\n   \n2. ``palantir_oauth_client.cache.REAUTH``: A write-only cache that will persist credentials to disk when ``offline_access``\n   scope is requested but will require reauthentication when obtaining credentials.\n   \n3. ``palantir_oauth_client.cache.NOOP``: Always requires reauthentication and never persists credentials to disk.\n\nPersisted credentials will be stored in the default user home directory at ``~/.foundry/oauth``. Caching should\nonly be used when this home directory is secure and inaccessible by other users who would not otherwise have access to\nthe Foundry credentials.\n\n## Contributing\n\nSee the [CONTRIBUTING.md](./CONTRIBUTING.md) document. Releases are published to [pypi](https://pypi.org/project/palantir-oauth-client/) on tag builds and are automatically re-published to conda using conda-forge.\n\n## License\nThis project is made available under the [Apache 2.0 License](/LICENSE).\n',
    'author': 'Thomas Powell',
    'author_email': 'tpowell@palantir.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/palantir/palantir-oauth-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
