# FangCloudServicesAPIAccessSDK
The SDK for accessing FangCloudServices with API Access Credentials

Support for more endpoints is coming soon.

## Installation
```shell
pip install FCSAPIAccessSDK
```

## Usage
Credentials are obtained from the web portal via `Project > API Access`. You must be an admin user in order to access this page.

Do not forget to enable the scopes in the web portal before attempting authentication.
```python
from FCSAPIAccess import FCSAPIAccess, Scope

FCSAPIAccess(client_id, client_secret, [Scope.PROJECT_VIEW_SCOPE, Scope.PROJECT_VIEW_USER])
```

Or if you only require a single scope:
```python
from FCSAPIAccess import FCSAPIAccess, Scope

FCSAPIAccess(client_id, client_secret, Scope.FULL_ACCESS)
```
