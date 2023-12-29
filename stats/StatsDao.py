"""
id
user ID 
timestamp
created date 
modified date - last_updated
createdFrom - null / chatId # this is need to know  if the chat is created from shared chat
type (of AI) GPT 
"""
from datetime import datetime, timedelta
from chats.dao.ChatHistoryDao import ChatHistoryDao
from utils.MongoConnection import MongoConnection
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
from chats.data_firewall.DataFirewall import DataFirewall

TYPE_OF_AI = {
    'GPT': 'GPT',
    'LLAMA': 'LLAMA',
}

chatHistoryDao = ChatHistoryDao()

class StatsDao(MongoConnection):

    def __init__(self):
        super(StatsDao, self).__init__('chat')
        self.get_collection("stats")

    def getPeriodForToday(self):
        today = datetime.now()
        return {
            "createdAt": {
                "$gte": today.replace(hour=0, minute=0, second=0, microsecond=0),
                "$lt": today.replace(hour=23, minute=59, second=59, microsecond=999),
            }
        }
    
    def getPeriodForLastNDays(self, delta, until_now = False):
        today = datetime.now()
        start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        days_ago = start_of_today - timedelta(days=delta)
        return {
            "createdAt": {
                "$gte": days_ago,
                "$lt": today if until_now else start_of_today,
            }
        }
 
    def getPeriodForLastNDaysDaily(self, no_of_days = 7):
        periods = list()
        periods.append(self.getPeriodForToday())

        today = datetime.now()
        start_of_new_day = today.replace(hour=0, minute=0, second=0, microsecond=0)

        for delta in range(no_of_days - 1):
            start_of_previous_day = start_of_new_day - timedelta(days=1)
            periods.append({
                "createdAt": {
                    "$gte": start_of_previous_day,
                    "$lt": start_of_new_day,
                }
            })
            start_of_new_day = start_of_previous_day
        return periods

    def getPeriodForLastNMonthsMonthly(self, no_of_months = 2):
        periods = list()
        today = datetime.now()
        current_month = today.replace(hour=0, minute=0, second=0, microsecond=0)

        for delta in range(no_of_months):
            previous_month = current_month - timedelta(days=30)
            periods.append({
                "createdAt": {
                    "$gte": previous_month,
                    "$lt": today if delta == 0 else current_month,
                }
            })
            current_month = previous_month
        return periods
    
    def calculateStat(self):
        data = {}
        data['monthly'] = self.calculateStatsForLastNMonths(2)
        data['daily'] = self.calculateStatsForLastNDays()
        data['topRedactedSensitiveData'] = self.calculateTopRedactedSensitiveData()
        return data

    def calculateStatsForLastNDays(self, no_of_days = 7):
        periods = self.getPeriodForLastNDaysDaily(no_of_days)
        stats = dict()
        for period in periods:
            stat = json.loads(dumps(chatHistoryDao.calculateStat(period)))
            stats[period['createdAt']['$gte'].strftime('%d %b') ] = stat[0] if stat else {'_id': 0, 'totalMessageCount': 0, 'totalPiiCount': 0}
        return stats

    def calculateStatsForLastNMonths(self, no_of_months = 2):
        periods = self.getPeriodForLastNMonthsMonthly(no_of_months)
        stats = dict()
        for period in periods:
            stat = json.loads(dumps(chatHistoryDao.calculateStat(period)))
            stats[str(period['createdAt']['$gte'].strftime('%d %b')) + ' to ' + str(period['createdAt']['$lt'].strftime('%d %b'))] = stat[0] if stat else {'_id': 0, 'totalMessageCount': 0, 'totalPiiCount': 0}
        return stats

    def calculateTopRedactedSensitiveData(self):
        entities = {entitity: 0 for entitity in DataFirewall.entities}
        
        period = self.getPeriodForLastNDays(30, until_now = True)
        data = json.loads(dumps(chatHistoryDao.calculateTopRedactedSensitiveData(period)))

        for chatHistory in data:
            print(chatHistory['piiToEntityTypeMap'])
            for key, value in chatHistory['piiToEntityTypeMap'].items():
                for entity in DataFirewall.entities:
                    if entity in value:
                        entities[entity] += 1
                        continue
        entities = dict(sorted(entities.items(), key = lambda x:x[1], reverse = True))
        return entities
