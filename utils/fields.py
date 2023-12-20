def hasMandatoryFieldsProvided(mandatoryAttributes, data):
    for attribute in mandatoryAttributes:
        if attribute not in data:
            return False
    return True