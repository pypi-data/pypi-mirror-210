'''
Created on 24 avr. 2018

@author: cbrun
'''
import h5py


class OperaH5Reader:
    class _Object:
        def __init__(self, group):
            self._group = group
            self._keys = self._group.keys()

        def get(self, key):
            if key in self._keys:
                # return self._group['data'][self._group[key][0]]
                return self._group[key]
            raise Exception("Unknown key: {}".format(key))

        def getKeys(self):
            return list(self._keys)

        def getAttrsNames(self, key):
            return self._group[key].attrs.keys()

        def getAttrs(self, key, attr=None):
            if attr is None:
                return self._group[key].attrs
            if attr in self._group[key].attrs.keys():
                attrs = self._group[key].attrs[attr]
                if hasattr(attrs, 'decode'):
                    attrs = attrs.decode('utf-8')
                return tuple(map(str.strip, attrs.split(',')))
            return ()

        def getHeaders(self, key):
            return self.getAttrs(key, 'Header')

        def getShape(self, key):
            return self.get(key).shape

    def __init__(self, fname):
        self._objects = dict()
        self._time = None
        self._root = h5py.File(fname, 'r')
        self._root.visit(self._extract)

    def _extract(self, key):
        try:
            type_ = self._root[key].attrs['Type']
            if hasattr(type_, 'decode'):
                type_ = type_.decode('utf-8')
        except KeyError:
            if type(self._root[key]) == h5py._hl.group.Group:
                type_ = "Miscellaneous"
            else:
                return
        if type_ not in self._objects:
            self._objects[type_] = dict()
        self._objects[type_][key] = self._Object(self._root[key])

    def getRigidBodiesNames(self):
        return list(self._objects['Rigid bodies'].keys())

    def getRigidBody(self, name):
        return self._objects['Rigid bodies'][name]

    def getTypes(self):
        return list(self._objects.keys())

    def getNames(self, typeName):
        return list(self._objects[typeName].keys())

    def get(self, typeName, name):
        return self._objects[typeName][name]

    def close(self):
        self._root.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        ll = []
        for t in self.getTypes():
            ll.append(f"{t}:")
            for n in self.getNames(t):
                ll.append(f"  - {n}")
        return '\n'.join(ll)
