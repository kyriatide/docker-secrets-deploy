"""
# Secret Providers
A *Secrets Provider* provides for reading secrets/values from a secrets store.

Extensibility: Add support for additional secrets providers, such as secrets managers,
by deriving from class `provider.Provider`.

Currently available providers are:
* `EnvironProvider` for reading secrets/values from environment variables.
"""
import os

class Provider:

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get(self, name: str) -> str:
        raise NotImplementedError


class EnvironProvider(Provider):

    def __init__(self, **kwargs):
        super(EnvironProvider, self).__init__(**kwargs)

    def get(self, name: str) -> str:
        return os.environ[name]
