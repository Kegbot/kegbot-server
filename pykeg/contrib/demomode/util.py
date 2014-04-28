import random
from django.db.models import Count


def random_item(model_cls):
    count = model_cls.objects.aggregate(count=Count('id'))['count']
    if count == 0:
        return None
    random_index = random.randint(0, count - 1)
    return model_cls.objects.all()[random_index]
