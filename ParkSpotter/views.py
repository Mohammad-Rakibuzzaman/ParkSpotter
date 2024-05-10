from django.http import HttpResponse


def home(request):
    return HttpResponse("This is a Home request...Hello from siyan, ratul and habib")