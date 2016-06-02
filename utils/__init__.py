

import importlib


__all__ = ['object_form_class_name']

def object_form_class_name(module_class):
    ps = module_class.split('.')
    module_name = '.'.join(ps[0:-1])
    class_name = ps[-1]
    module = importlib.import_module(module_name)
    class_obj = getattr(module, class_name)
    return class_obj()

