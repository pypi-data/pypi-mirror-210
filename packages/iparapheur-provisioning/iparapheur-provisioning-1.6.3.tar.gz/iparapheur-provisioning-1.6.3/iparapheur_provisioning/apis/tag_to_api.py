import typing_extensions

from iparapheur_provisioning.apis.tags import TagValues
from iparapheur_provisioning.apis.tags.admin_tenant_user_api import AdminTenantUserApi
from iparapheur_provisioning.apis.tags.admin_desk_api import AdminDeskApi
from iparapheur_provisioning.apis.tags.admin_typology_api import AdminTypologyApi
from iparapheur_provisioning.apis.tags.admin_tenant_api import AdminTenantApi
from iparapheur_provisioning.apis.tags.admin_all_users_api import AdminAllUsersApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.ADMINTENANTUSER: AdminTenantUserApi,
        TagValues.ADMINDESK: AdminDeskApi,
        TagValues.ADMINTYPOLOGY: AdminTypologyApi,
        TagValues.ADMINTENANT: AdminTenantApi,
        TagValues.ADMINALLUSERS: AdminAllUsersApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.ADMINTENANTUSER: AdminTenantUserApi,
        TagValues.ADMINDESK: AdminDeskApi,
        TagValues.ADMINTYPOLOGY: AdminTypologyApi,
        TagValues.ADMINTENANT: AdminTenantApi,
        TagValues.ADMINALLUSERS: AdminAllUsersApi,
    }
)
