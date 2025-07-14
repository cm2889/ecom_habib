from backend.models import UserMenuPermission


def menu_items(request):
    menu_list = UserMenuPermission.objects.filter(user_id=request.user.id, menu__is_main_menu=True, can_view=True, menu__parent_id=0, menu__is_active=True, is_active=True).select_related('menu', 'user')
    search_menu_list = UserMenuPermission.objects.filter(user_id=request.user.id, can_view=True, menu__is_active=True, is_active=True).select_related('menu', 'user')

    return {'main_menu_list':  menu_list, 'search_menu_list': search_menu_list}
