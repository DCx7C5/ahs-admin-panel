import asyncio
from django.utils.functional import LazyObject, empty


class AsyncLazyObject(LazyObject):
    """
    A lazy object that works with async callables.
    """

    def __init__(self, factory):
        """
        Pass in a callable (async) that returns the object to be wrapped.
        """
        super().__init__()
        self._setupfunc = factory
        self._wrapped = empty
        self._lock = asyncio.Lock()  # Ensure thread safety during lazy evaluation

    async def _setup(self):
        """
        Call the factory to create the wrapped object when needed.
        """
        async with self._lock:
            if self._wrapped is empty:  # Ensure setup is not duplicated
                self._wrapped = await self._setupfunc()

    def __await__(self):
        """
        Allow the object itself to be awaited to retrieve the wrapped object.
        """

        async def get_wrapped():
            if self._wrapped is empty:
                await self._setup()
            return self._wrapped

        return get_wrapped().__await__()

    def __getattr__(self, name):
        """
        Delegate attribute access to the wrapped object.
        """
        if self._wrapped is empty:
            raise RuntimeError(
                f"The '{type(self).__name__}' object has not been awaited yet. "
                f"Use 'await obj' before accessing attributes."
            )
        return getattr(self._wrapped, name)

    def __setattr__(self, name, value):
        """
        Support setting attributes on the wrapped object or this instance.
        """
        if name in ("_setupfunc", "_wrapped", "_lock"):
            object.__setattr__(self, name, value)
        elif self._wrapped is empty:
            raise RuntimeError(
                f"The '{type(self).__name__}' object has not been awaited yet. "
                f"Use 'await obj' before setting attributes."
            )
        else:
            setattr(self._wrapped, name, value)
