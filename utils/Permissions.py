class Permission:

    ManageOnboarding = "manageOnboarding"
    ReadIDPConfig = "readIDPConfig"
    ManageIDPConfig = "manageIDPConfig"
    ReadGroups = "readGroups"
    ManageGroups = "manageGroups"

    ReadUser = "readUser"
    
    # Chat
    ReadChat = "readChat"
    WriteChat = "writeChat"
    ManageChat = "manageChat"

    ReadChatHistory = "readChatHistory"
    WriteChatHistory = "writeChatHistory"
    ManageChatHistory = "manageChatHistory"

    WriteShareChat = "WriteShareChat"
    ReadShareChat = "ReadShareChat"
    ManageShareChat = "ManageShareChat"
    ManagePinnedChats = "managePinnedChats"
    ManageBookmarks = "ManageBookmarks"
    ManageLlmModels = "ManageLlmModels"
    
    # End

    #Legacy
    ReadEmployeeChats = "readEmployeeChats"
    
    AllUser = "allUsers"
    ManageInviteUsers = "managerInviteUsers"
    ReadInviteUsers = "readInviteUsers"
    ReadUsers = "readUsers"
    ManageUsers = "manageUsers"
    
    ManageUser = "manageUser"
    ReadUserFilters = "readUserFilters"
    ManageOkta = "manageOkta"

PermissionList = [value for name, value in vars(Permission).items() if isinstance(value, str)]
class Roles:
    IT_ADMIN = 'IT_ADMIN'
    SECURITY_PRIVACY_ADMIN = 'SECURITY_PRIVACY_ADMIN'
    USER = 'USER'


class RolePermissionsMapping:
    BASE_PERMISSIONS = [
        Permission.ManageChat,
        Permission.ReadChat,
        Permission.WriteChat,
        Permission.ReadChatHistory,
        Permission.WriteChatHistory,
        Permission.ManageChatHistory,

        Permission.WriteShareChat,
        Permission.ReadShareChat,
        Permission.ManageShareChat,
        Permission.ManagePinnedChats,
        Permission.ManageBookmarks,
        Permission.ManageLlmModels,

        Permission.ReadUser,
    ]

    def getUIPermissions(role):
        if role == Roles.IT_ADMIN:
            return {
                "settings": True,
                "chats": True,
                "onboarding": True
            }
        elif role == Roles.SECURITY_PRIVACY_ADMIN:
            return {
                "chats": True,
            }
        elif role == Roles.USER:
            return {
                "chats": True,
            }
     
    
    def getPermissions(role):
        if role == Roles.IT_ADMIN:
            return ['*']
        elif role == Roles.SECURITY_PRIVACY_ADMIN:
            return RolePermissionsMapping.BASE_PERMISSIONS
        elif role == Roles.USER:
            return RolePermissionsMapping.BASE_PERMISSIONS
        raise "Invalid Role"
