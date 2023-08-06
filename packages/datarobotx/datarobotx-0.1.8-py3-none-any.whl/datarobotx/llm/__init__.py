# flake8: noqa

try:
    from .chains.data_dict import DataDictChain
    from .chains.enrich import embed, enrich
except ImportError:
    pass
