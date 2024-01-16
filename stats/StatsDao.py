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
from chats.dao.ChatDao import TYPE_OF_AI
from chats.dao.ChatHistoryDao import ChatHistoryDao
from users.models import User
from utils.MongoConnection import MongoConnection
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
from chats.data_firewall.DataFirewall import DataFirewall
from utils.accessorUtils import getOrNone
from users.models import User

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
        return periods[::-1]

    def getPeriodForLastNMonthsWeekly(self, no_of_weeks = 8):
        periods = list()
        today = datetime.now()
        current_month = today.replace(hour=0, minute=0, second=0, microsecond=0)

        for delta in range(no_of_weeks):
            previous_month = current_month - timedelta(days=7)
            periods.append({
                "createdAt": {
                    "$gte": previous_month,
                    "$lt": today if delta == 0 else current_month,
                }
            })
            current_month = previous_month
        return periods[::-1]

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
        data['monthly'] = self.calculateStatsForLastNMonths()
        data['bimonthly'] = self.calculateStatsForLast2Months()
        data['daily'] = self.calculateStatsForLastNDays()
        data['topRedactedSensitiveData'] = self.calculateTopRedactedSensitiveData()
        data['UsageAcrossUserGroups'] = self.calculateUsageAcrossUserGroups()
        return data

    def calculateStatsForLastNDays(self, no_of_days = 7):
        periods = self.getPeriodForLastNDaysDaily(no_of_days)
        stats = list()
        for period in periods:
            stat = json.loads(dumps(chatHistoryDao.calculateStat(period)))
            stats.append(stat[0] if stat else { '_id': 0, 'totalMessageCount': 0, 'totalPiiCount': 0})
            stats[-1]['label'] = period['createdAt']['$gte'].strftime('%d %b')
        return stats

    def calculateStatsForLastNMonths(self, no_of_months = 8):
        periods = self.getPeriodForLastNMonthsWeekly(no_of_months)
        stats = list()
        for period in periods:
            stat = json.loads(dumps(chatHistoryDao.calculateStat(period)))
            if stat:
                stats.append(stat[0])
            else:
                stats.append({'_id': 0, 'totalMessageCount': 0, 'totalPiiCount': 0, 'activeUsers': 0})
            activeUsers = len(self.getActiveUsers(period))
            stats[-1]['activeUsers'] = activeUsers if activeUsers else 0
            stats[-1]['time'] = str(period['createdAt']['$gte'].strftime('%d %b')) + ' to ' + str(period['createdAt']['$lt'].strftime('%d %b'))
        return stats
    
    def getActiveUsers(self, period):
        return User.objects.filter(last_login__gte=period['createdAt']['$gte']).filter(last_login__lt=period['createdAt']['$lt'])

    def calculateStatsForLast2Months(self, no_of_months = 2):
        periods = self.getPeriodForLastNMonthsMonthly(no_of_months)
        stats = list()
        for period in periods:
            stat = json.loads(dumps(chatHistoryDao.calculateStat(period)))
            if stat:
                stats.append(stat[0])
            else:
                stats.append({'_id': 0, 'totalMessageCount': 0, 'totalPiiCount': 0, 'activeUsers': 0})
            activeUsers = len(self.getActiveUsers(period))
            stat[0]['activeUsers'] = activeUsers if activeUsers else 1
            stats[-1]['time'] = str(period['createdAt']['$gte'].strftime('%d %b')) + ' to ' + str(period['createdAt']['$lt'].strftime('%d %b'))
        return {
            'activeUsers': stats[0]['activeUsers'],
            'promptSent': stats[0]['totalMessageCount'],
            'piiCount': stats[0]['totalPiiCount'],
            'activeUsersPercent': (stats[0]['activeUsers']-stats[1]['activeUsers']) * 100 / stats[1]['activeUsers'],
            'promptSentPercent': (stats[0]['totalMessageCount']-stats[1]['totalMessageCount']) * 100 / stats[1]['totalMessageCount'],
            'piiCountPercent': (stats[0]['totalPiiCount']-stats[1]['totalPiiCount']) * 100 / stats[1]['totalPiiCount'],
        }
        

    def calculateTopRedactedSensitiveData(self):
        entities = {entitity: 0 for entitity in DataFirewall.entities}
        
        period = self.getPeriodForLastNDays(30, until_now = True)
        data = json.loads(dumps(chatHistoryDao.calculateTopRedactedSensitiveData(period)))

        for chatHistory in data:
            for key, value in chatHistory['piiToEntityTypeMap'].items():
                for entity in DataFirewall.entities:
                    if entity in value:
                        entities[entity] += 1
                        continue
        entities = dict(sorted(entities.items(), key = lambda x:x[1], reverse = True))
        entity_list = list()
        cnt = 0
        for entity, value in entities.items():
            if cnt == 4:
                entity_list.append({"label":"Others", "value": value})
            elif cnt > 4:
                entity_list[-1]["value"] += value
            else:
                entity_list.append({"label": ' '.join(entity.split('_')), "value": value})
            cnt += 1
        return entity_list
    
    def getUserGroup(self, userId):
        user = getOrNone(model=User, id=userId)
        return user.invitedRole
    
    def calculateUsageAcrossUserGroups(self, no_of_months = 1):
        periods = self.getPeriodForLastNMonthsMonthly(no_of_months)
        stats = list()
        for period in periods:
            statByUserId = json.loads(dumps(chatHistoryDao.calculateUsageAcrossUserGroups(period)))
            
            statsByPeriod = dict()
            for stat in statByUserId:
                userGroup = self.getUserGroup(stat['_id'])
                if userGroup not in statsByPeriod:
                    statsByPeriod[userGroup] = { 'totalMessageCount': stat['totalMessageCount'], 'totalPiiCount': stat['totalPiiCount'], 'userGroup': userGroup }
                else:
                    statsByPeriod[userGroup]['totalMessageCount'] += stat['totalMessageCount']
                    statsByPeriod[userGroup]['totalPiiCount'] += stat['totalPiiCount']
            
            stats.append(statsByPeriod[userGroup])
        return stats


