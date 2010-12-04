from operator import itemgetter

def upcast(obj):
    '''Upcast object to it's child.'''

    try:
        return obj._upcast_result
    except AttributeError:
        from django.db.models.query import Collector

        query = obj._default_manager.filter(pk = obj.pk)
        collector = Collector(using = query.db)
        collector.collect(query)

        def cmp_types(left, right):
            if issubclass(left, right):
                return -1
            return 1

        data = sorted(
            map(itemgetter(0), collector.data.values()),
            cmp = cmp_types,
            key = type,
        )

        if data:
            child = data[0]
        else:
            child = obj

        setattr(obj, '_upcast_result', child)
        setattr(child, '_upcast_result', child)
        return child


def virtual(func):
    '''Decorator for 'virtual' methods.

       Find a child object and call method against it
       instead os original 'func'.

       Apply this decorator to any method of the base
       class.
    '''

    def wrap(self, *args, **kwargs):
        child_object = upcast(self)
        child_method = getattr(child_object, func.__name__)
        if getattr(child_method, '_is_virtual_wrap', False):
            return func(self, *args, **kwargs)
        return child_method(*args, **kwargs)
    wrap.__doc__  = func.__doc__
    wrap.__name__ = func.__name__
    setattr(wrap, '_is_virtual_wrap', True)
    return wrap
