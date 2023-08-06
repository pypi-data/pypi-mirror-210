# -*- coding: utf-8 -*-


__all__ = []


def register_api(name, func):
    globals()[name] = func
    __all__.append(name)









