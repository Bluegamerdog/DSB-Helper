def DSBCOMM_A(user): # function to check if user is DSBCOMM+
    roles = user.roles
    for role in roles:
        if role.name in ["QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def DSBPC_A(user): # function to check if user is DSBPreCom+ 
    roles = user.roles
    for role in roles:
        if role.name in ["DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def FMR_A(user): # function to check if user is MR+
    roles = user.roles
    for role in roles:
        if role.name in ["Staff Sergeant","Sergeant Major","Chief Sergeant", "DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def ITMR_A(user): # MR in-training and above
    roles = user.roles
    for role in roles:
        if role.name in ["Junior Staff Sergeant", "Operation Ringleader" ,"DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def DSBMEMBER(user): # PFC+
    roles = user.roles
    for role in roles:
        if role.name in ["DSB"] and role.name not in ["DSB Private"] or role.permissions.administrator:
            return True
    return False

def DSBROLE(user): # PRV+
    roles = user.roles
    for role in roles:
        if role.name in ["DSB"]:
            return True
    return False

def onLoA(user): # On LoA?
    roles = user.roles
    for role in roles:
        if role.name in ["DSB Leave of Absence"]:
            return True
    return False

def DEVACCESS(user):
    allowed_ids = [776226471575683082, 395505414000607237, 1053377038490292264] # Blue, Orange and Shush
    if user.id in allowed_ids or user.guild_permissions.administrator:
        return True
    return False
