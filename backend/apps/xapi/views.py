from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse



def testview(request: HttpRequest) -> HttpResponse:

    return TemplateResponse(
        request=request,
        template='ahs_core/index.html',
        context={}
    )
