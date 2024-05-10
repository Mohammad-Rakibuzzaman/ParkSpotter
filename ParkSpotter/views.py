from django.http import HttpResponse

def Home(request):
    """Render the home/default view.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    return HttpResponse("Home")