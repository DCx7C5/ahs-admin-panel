from abc import ABCMeta

from backend.ahs_core.utils import adecode_b64urlsafe, ajson_decode


class AbstractBaseTokenSegment(metaclass=ABCMeta):
    __slots__ = ('errors', 'segment', '_segment')

    def __getitem__(self, key):
        """Allow dict-style access: obj['key']"""
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """Allow dict-style assignment: obj['key'] = value"""
        setattr(self, key, value)

    def __delitem__(self, key):
        """Allow dict-style deletion: del obj['key']"""
        try:
            delattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __contains__(self, key):
        """Allow 'key in obj' syntax"""
        return hasattr(self, key)

    def __iter__(self):
        """Allow iteration over attribute names (keys)"""
        # Filter out built-in attributes and methods
        return iter([attr for attr in dir(self)
                     if not attr.startswith('__') and not callable(getattr(self, attr))])

    async def __aiter__(self):
        """Allow async iteration over attribute names (keys)"""
        return self.__iter__()

    def __len__(self):
        """Return number of attributes"""
        return len(list(iter(self)))

    def get(self, key, default=None):
        """Mimic dict.get() method"""
        return getattr(self, key, default)

    def keys(self):
        """Return attribute names as keys"""
        return list(iter(self))

    def values(self):
        """Return attribute values"""
        return [getattr(self, key) for key in self.keys()]

    def items(self):
        """Return (key, value) pairs"""
        return [(key, getattr(self, key)) for key in self.keys()]

    def update(self, other=None, **kwargs):
        """Update attributes with new key-value pairs"""
        if other is not None:
            for key, value in other.items() if hasattr(other, 'items') else other:
                setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def clear(self):
        """Remove all custom attributes"""
        for key in list(self.keys()):
            delattr(self, key)

    async def decode(self, enc_segment: str) -> dict:
        """
        Create an instance of TokenHeader from an encoded header segment.
        """
        data = None
        try:
            json_data = await adecode_b64urlsafe(enc_segment)
            data = await ajson_decode(json_data)
        except Exception as e:
            self.errors.append(f"Error decoding {self.__class__.__name__} segment: {e}")

        return data


