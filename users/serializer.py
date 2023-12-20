from users.models import User
from utils.accessorUtils import getOrNone

def getUserById(userId):
    return getOrNone(model=User, id=userId)


def getUserByEmail(email):
    return getOrNone(model=User, email=email)


def updateUser(userId, **kwargs):
    attrsNotEdited = list()
    user: User = getUserById(userId=userId)
    
    allowedAttributes = ['firstName', 'lastName' ]
    kwargs.pop('id', None)
    
    for attribute in kwargs:
        if getattr(user, attribute, None) != kwargs[attribute]:
            if attribute in allowedAttributes:
                user.__setattr__(attribute, kwargs[attribute])
            else:
                attrsNotEdited.append(attribute)

    user.save()
    user.refresh_from_db()
    return user, attrsNotEdited



def serializeUserObject(user: User):
    newUser = dict(
        id=user.id,
        email=user.email,
        firstName=user.firstName,
        lastName=user.lastName,
        isOkta=user.isOkta,
        account=list(user.accounts.values('id', 'name', 'is_setup_done'))[0]
    )

    return newUser
