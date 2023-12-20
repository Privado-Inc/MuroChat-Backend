from django.urls import path
from utils.Permissions import Permission
from .views import usersview

urlpatterns = [
    path('sso/okta', usersview.handleOktaLoginOrSignup),
    path('meta', usersview.handleMeta),
    path('idp-configuration', usersview.handleIDP),
    path('onboarding', usersview.handleOnboarding),
    path('clearall', usersview.clearALL),
    path('idp-groups', usersview.fetchOktaGroups),
    path('idp-role-mapping', usersview.handleIDPRoleMapping),
    path('session-user', usersview.handleSessionUser),
    path('sync-users', usersview.getUsers),
    path('invite-users', usersview.inviteUsers),
    path('users', usersview.users),
    path('user-filters', usersview.userFilters),
]
