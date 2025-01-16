import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import AccessMixin

from django.template.response import TemplateResponse

from django.views.generic import DetailView, TemplateView


logger = logging.getLogger(__name__)


class AdminRequiredMixin(LoginRequiredMixin, AccessMixin):
    async def dispatch(self, request, *args, **kwargs):
        user = await request.auser()
        if not user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class BaseLogReqView(LoginRequiredMixin):
    class Meta:
        abstract = True


class BaseAdminReqView(AdminRequiredMixin):
    class Meta:
        abstract = True


class BaseReactView(BaseLogReqView):
    class Meta:
        abstract = True


@login_required
async def async_dashboard_view(request):

    return TemplateResponse(request, 'ahs_core/index.html', {})


class ReactView(BaseReactView, TemplateView):
    template_name = "ahs_core/index.html"
    http_method_names = ('GET', 'POST')


class UserProfileView(LoginRequiredMixin, DetailView):
    http_method_names = ('GET', 'POST')
    User = get_user_model()
    template_name = "profile/index.html"
    context_object_name = "user"

    async def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['username'] = self.request.user.username
        return ctx
