import pickle
import cachetools
import pkg_resources


@cachetools.cached(cache={})
def get_pkg_instance():
    data_file = pkg_resources.resource_filename(__name__, "data.pkl")
    with open(data_file, 'rb') as fd:
        data = pickle.load(fd)
    return data


def split_chinese_char(c, default):
    pkg_instance = get_pkg_instance()
    result = pkg_instance.get(c, default)
    if result:
        return result[0]
    else:
        return []
