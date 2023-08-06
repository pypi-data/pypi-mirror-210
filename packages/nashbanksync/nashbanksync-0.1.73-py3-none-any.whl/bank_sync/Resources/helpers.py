# This Decorator Class is used to execute methods that can only be executed in a Django Framework
# They mainly inlude methods that use the django ORM to access a database
class IsDjangoAppClass(object):
    def __init__(self,flag):
        self.flag = flag
    def __call__(self, original_func):
        def wrappee( *args, **kwargs):
            # 'in decorator before wrapee with flag '
            if self.flag:
                return original_func(*args,**kwargs)
            # 'in decorator after wrapee with flag '
        return wrappee