import abc
from _typeshed import Incomplete
from abc import abstractmethod
from aioworkers.core.base import AbstractNamedEntity as AbstractNamedEntity

class AbstractBaseStorage(AbstractNamedEntity, metaclass=abc.ABCMeta):
    @abstractmethod
    async def raw_key(self, key): ...

class AbstractStorageReadOnly(AbstractBaseStorage, metaclass=abc.ABCMeta):
    @abstractmethod
    async def get(self, key): ...

class AbstractFindStorage(AbstractBaseStorage, metaclass=abc.ABCMeta):
    @abstractmethod
    async def find(self, *args, **kwargs): ...

class AbstractStorageWriteOnly(AbstractBaseStorage, metaclass=abc.ABCMeta):
    @abstractmethod
    async def set(self, key, value): ...

class AbstractStorage(AbstractStorageReadOnly, AbstractStorageWriteOnly, metaclass=abc.ABCMeta):
    async def copy(self, key_source, storage_dest, key_dest): ...
    async def move(self, key_source, storage_dest, key_dest): ...

class AbstractListedStorage(AbstractStorage, metaclass=abc.ABCMeta):
    @abstractmethod
    async def list(self): ...
    @abstractmethod
    async def length(self): ...

class AbstractExpiryStorage(AbstractStorage, metaclass=abc.ABCMeta):
    @abstractmethod
    async def expiry(self, key, expiry): ...

class FieldStorageMixin(AbstractStorage, metaclass=abc.ABCMeta):
    model = dict
    async def get(self, key, *, field: Incomplete | None = ..., fields: Incomplete | None = ...): ...
    async def set(self, key, value, *, field: Incomplete | None = ..., fields: Incomplete | None = ...) -> None: ...
