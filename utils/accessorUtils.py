import logging

def getOrNone(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
    except Exception as e:
        logging.exception("Failed and it is here: %s", str(e))



def getOrCreate(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs), False
    except model.DoesNotExist:
        return model.objects.create(*args, **kwargs), True


def create(model, *args, **kwargs):
    return model.objects.create(*args, **kwargs)


def getList(model, *args, **kwargs):
    try:
        return model.objects.filter(*args, **kwargs)
    except model.DoesNotExist:
        return list()
    except Exception as e:
        logging.exception("Failed and it is here: %s", str(e))

