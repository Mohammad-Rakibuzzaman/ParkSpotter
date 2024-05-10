from django.http import HttpResponse


def home(request):
    return HttpResponse("This is a Home request...hi i am siyan")