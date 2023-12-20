import re
from chats.data_firewall.util import *
from typing import List
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.entities.engine.result.engine_result import EngineResult

class DataFirewall:
    
    analyzer = AnalyzerEngine()
    anonymizerEngine = AnonymizerEngine()
    entities = ["PHONE_NUMBER", "CREDIT_CARD", "CRYPTO", "DATE_TIME", "EMAIL_ADDRESS", "IBAN_CODE", "IP_ADDRESS", "NRP", "LOCATION", 
                "PERSON", "PHONE_NUMBER", "MEDICAL_LICENSE", "URL", "US_BANK_NUMBER", "US_DRIVER_LICENSE", "US_ITIN", "US_PASSPORT",
                "US_SSN", "UK_NHS", "ES_NIF", "IT_FISCAL_CODE", "IT_DRIVER_LICENSE", "IT_VAT_CODE", "IT_PASSPORT", "IT_IDENTITY_CARD",
                "SG_NRIC_FIN", "AU_ABN", "AU_ACN", "AU_TFN", "AU_MEDICARE"]

    @classmethod
    def detectPii(cls, inputString):
        analyzerOutput = cls.analyzer.analyze(text=inputString, entities=cls.entities, language='en')
        return analyzerOutput
    
    @classmethod
    def getPiiValues(cls, analyzerOutput, inputString):
        piiValues = cls.anonymizerEngine.anonymize(text=inputString,
                                                      analyzer_results=analyzerOutput,
                                                      operators={"DEFAULT": OperatorConfig("custom", {"lambda": lambda x: x})})
        return piiValues
    
    @classmethod
    def generateAndAssignIndexToPii(cls, piiValuesList, analyzerOutput, existingMap):
        generateAndAssignIndexToPiiUtils(piiValuesList, existingMap)
        for item1 in analyzerOutput:
            for item2 in piiValuesList:
                if ( item1.start == item2.start ) and ( item1.end == item2.end ):
                    item1.entity_type = item2.entity_type
        return analyzerOutput
    
    @classmethod
    def anonymize(cls, inputString, existingMap):
        analyzerOutput = cls.detectPii(inputString)
        piiValues = cls.getPiiValues(analyzerOutput, inputString)
        analyzerOutput = cls.generateAndAssignIndexToPii(piiValues.items, analyzerOutput, existingMap)
        anonymizerOutput = cls.anonymizerEngine.anonymize(text=inputString, analyzer_results=analyzerOutput)
        return anonymizerOutput.text, piiValues
    
    @classmethod
    def getPiiToEntityMap(cls, piiValuesList, exitingPIIMapForChat):
        piiToEntityTypeMap = exitingPIIMapForChat

        for item in piiValuesList:
            entityType = item.entity_type
            text = item.text
            piiToEntityTypeMap[text] = entityType
        return piiToEntityTypeMap

    @classmethod
    def deanonymize(cls, anonymizeText, piiValuesList):
        entityTypeToPiiMap = {}

        for item in piiValuesList:
            entityType = item.entity_type
            text = item.text
            entityTypeToPiiMap[entityType] = text

        deanonymizeText = anonymizeText
        for entity in entityTypeToPiiMap:
            deanonymizeText = deanonymizeText.replace("<" + entity + ">", entityTypeToPiiMap[entity])
        return deanonymizeText
        

    



