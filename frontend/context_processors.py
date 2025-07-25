from backend.models import FrontendDesignSettings


def frontend_design_settings(request):
    if request.user.is_authenticated:
        design = FrontendDesignSettings.objects.filter(created_by=request.user).first()
    else:
        design = None
    return {
        'design': design
    }
