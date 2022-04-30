from .models import Category


def custom_proc(request):

    return {

        'is_not_premium': not request.user.groups.filter(
            name='authors').exists(),
        'categories': Category.objects.all(),
        'is_authenticated': request.user.is_authenticated,
    }
