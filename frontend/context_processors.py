from backend.models import FrontendDesignSettings


def frontend_design_settings(request):
    
    design = FrontendDesignSettings.objects.first()
    return {
        'design': design
    }
