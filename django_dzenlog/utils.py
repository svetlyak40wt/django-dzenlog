from django.db.models.query import CollectedObjects

def upcast(obj):
    try:
        return getattr(obj, '_upcast_result')
    except AttributeError:
        sub_objects = CollectedObjects()
        obj._collect_sub_objects(sub_objects)
        child = sub_objects.items()[0][1].values()[0]
        setattr(obj, '_upcast_result', child)
        return child
