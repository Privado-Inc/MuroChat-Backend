from collections import defaultdict
from presidio_anonymizer.entities.engine.result.operator_result import OperatorResult

def getPIICount(entity, entityMap):
        count = 1
        for key, value in entityMap.items():
            if entity in value:
                count += 1
        return count

# get the unique count for each entity_type
# sample output: {'PERSON': defaultdict(<class 'int'>, {'Thomas': 2, 'James Bond': 1}), 'PHONE_NUMBER': defaultdict(<class 'int'>, {'212-555-5555': 1}), '# LOCATION': defaultdict(<class 'int'>, {'Minnosota': 1})}
def groupPiiByTypeHelper(inputData):
    groupedData = defaultdict(lambda: defaultdict(int))
    
    for item in inputData:
        print(type(item))
        entityType = item.entity_type
        text = item.text
        groupedData[entityType][text] += 1 

    # Convert the defaultdict to a regular dictionary
    groupedData = dict(groupedData)

    return groupedData

# use grouped data and assign indexes 
def assignIndexToEachPiiHelper(inputData, groupedData, existingMap):
    # iterate through the data and generate index for each text
    for entityType, entityCounts in groupedData.items():
        newEntityCounts = defaultdict(int)
        count = getPIICount(entityType, existingMap)
        for text in entityCounts:
            newEntityCounts[text] = count
            count += 1
        groupedData[entityType] = newEntityCounts

    # assign index to each text
    for item in inputData:
        entityType = item.entity_type
        text = item.text
        item.entity_type = entityType + str(groupedData[entityType][text])

    print(type(inputData))
    return inputData


# After PII is identified in the data, we need to generate unique entity type for each PII
# If there are two person - Tom and Jerry in the sentence. We want to use PERSON1 for Tom and PERSON2 for Jerry.
# Function AnalyzerEngine.analyze() doesn't generate the unique entity types. For both - Tome and Jerry, it will generate
# PERSON as the type
# Input: 
# [
#    {'start': 93, 'end': 105, 'entity_type': 'PHONE_NUMBER', 'text': '212-555-5555', 'operator': 'custom'},
#    {'start': 63, 'end': 72, 'entity_type': 'LOCATION', 'text': 'Minnosota', 'operator': 'custom'},
#    {'start': 43, 'end': 49, 'entity_type': 'PERSON', 'text': 'Thomas', 'operator': 'custom'},
#    {'start': 17, 'end': 27, 'entity_type': 'PERSON', 'text': 'James Bond', 'operator': 'custom'}
# ]
# Output:
# [ 
#   {'start': 93, 'end': 105, 'entity_type': 'PHONE_NUMBER1', 'text': '212-555-5555', 'operator': 'custom'}, 
#   {'start': 63, 'end': 72, 'entity_type': 'LOCATION1', 'text': 'Minnosota', 'operator': 'custom'}, 
#   {'start': 43, 'end': 49, 'entity_type': 'PERSON1', 'text': 'Thomas', 'operator': 'custom'}, 
#   {'start': 17, 'end': 27, 'entity_type': 'PERSON2', 'text': 'James Bond', 'operator': 'custom'}
# ]

def generateAndAssignIndexToPiiUtils(inputData, existingMap):
    # Call the function to group the entities
    groupedOutput = groupPiiByTypeHelper(inputData)

    indexes = assignIndexToEachPiiHelper(inputData, groupedOutput, existingMap)
    return indexes
