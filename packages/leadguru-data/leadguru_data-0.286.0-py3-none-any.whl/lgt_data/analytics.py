import datetime
import os
from typing import Optional, List, Dict, Union
from collections import OrderedDict

from bson import ObjectId
from dateutil import tz
from lgt_data.mongo_repository import to_object_id
from pymongo import MongoClient

client = MongoClient(os.environ.get('MONGO_CONNECTION_STRING', 'mongodb://127.0.0.1:27017/'))
db = client.lgt_analytics


def _build_date_aggregated_analytics_pipeline(name=None,
                                              started_at: datetime.datetime = None,
                                              ended_at: datetime.datetime = None,
                                              bots_ids: [str] = None):
    pipeline = [
        {
            "$sort": {"created_at": 1}
        },
        {
            "$project": {
                "created_at": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "name": "$name"
            }
        },
        {
            "$group":
                {
                    "_id": "$created_at",
                    "count": {"$sum": 1}
                }
        },
        {
            "$project": {
                "_id": {"$dateFromString": {"format": "%Y-%m-%d", "dateString": "$_id"}},
                "count": "$count"
            }
        },
        {
            "$sort": {"_id": 1}
        },
        {"$limit": 1000}
    ]

    if name:
        pipeline.insert(0, {"$match": {"name": name}})

    if started_at:
        beginning_of_the_day = datetime.datetime(started_at.year, started_at.month, started_at.day, 0, 0, 0, 0)
        pipeline.insert(0, {"$match": {"created_at": {"$gte": beginning_of_the_day}}})

    if ended_at:
        end_of_the_day = datetime.datetime(ended_at.year, ended_at.month, ended_at.day, 23, 59, 59, 999)
        pipeline.insert(0, {"$match": {"created_at": {"$lte": end_of_the_day}}})

    if bots_ids is not None:
        pipeline.insert(0, {"$match": {'extra_ids': {'$in': bots_ids}}})

    return pipeline


def _build_date_aggregated_user_analytics_pipeline(user_id: str = None,
                                                   started_at: datetime.datetime = None,
                                                   ended_at: datetime.datetime = None):
    pipeline = [
        {
            '$sort': {'created_at': 1}
        },
        {
            '$project': {
                'created_at':
                    {
                        '$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}
                    },
                'name': '$name'
            }
        },
        {
            '$group': {
                '_id':
                    {
                        'created_at': '$created_at',
                        'name': '$name'
                    },
                'count': {'$sum': 1}
            }
        },
        {
            '$project': {
                '_id': {
                    'created_at':
                        {
                            '$dateFromString': {'format': '%Y-%m-%d', 'dateString': '$_id.created_at'}
                        },
                    'name': '$_id.name'
                },
                'count': '$count'
            }
        },
        {'$sort': {'_id.created_at': 1}},
        {'$limit': 1000}
    ]

    if user_id:
        pipeline.insert(0, {"$match": {"data": str(user_id)}})

    if started_at:
        beginning_of_the_day = datetime.datetime(started_at.year, started_at.month, started_at.day, 0, 0, 0, 0)
        pipeline.insert(0, {"$match": {"created_at": {"$gte": beginning_of_the_day}}})

    if ended_at:
        end_of_the_day = datetime.datetime(ended_at.year, ended_at.month, ended_at.day, 23, 59, 59, 999)
        pipeline.insert(0, {"$match": {"created_at": {"$lte": end_of_the_day}}})

    return pipeline


def _create_result_dic(started_at: datetime.datetime = None, ended_at: datetime.datetime = None):
    analytics_dict = OrderedDict()

    if started_at and ended_at:
        days_range = range(0, (ended_at - started_at).days + 1)
        for day in days_range:
            cur_date = started_at + datetime.timedelta(days=day)
            str_date = f'{cur_date.year}-{cur_date.month:02d}-{cur_date.day:02d}'
            analytics_dict[str_date] = 0

    return analytics_dict


def _prepare_date_analytics_doc(doc, ordered_result_dict: Dict[str, int]):
    for item in doc:
        str_date = f'{item["_id"].year}-{item["_id"].month:02d}-{item["_id"].day:02d}'
        ordered_result_dict[str_date] = item["count"]
    return ordered_result_dict


def get_aggregated_user_leads(user_id: Union[ObjectId, str],
                              from_date: datetime.datetime,
                              to_date: datetime.datetime = None):
    pipeline = [
        {
            '$match': {
                'user_id': to_object_id(user_id),
                'created_at': {'$gte': from_date}
            }
        }, {
            '$group': {
                '_id': {
                    '$dateFromParts': {
                        'day': {
                            '$dayOfMonth': '$created_at'
                        },
                        'month': {
                            '$month': '$created_at'
                        },
                        'year': {
                            '$year': '$created_at'
                        }
                    }
                },
                'count': {
                    '$sum': 1
                },
                'leads': {
                    '$push': {
                        'id': '$id',
                        'created_at': '$created_at'
                    }
                }
            }
        }, {
            '$sort': {
                '_id': 1
            }
        }
    ]

    if to_date:
        end = datetime.datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, tzinfo=tz.tzutc())
        pipeline[0]["$match"]["created_at"]['$lte'] = end

    user_leads_data = list(client.lgt_admin.user_leads.aggregate(pipeline))
    result = _create_result_dic(from_date, to_date)

    for item in user_leads_data:
        str_date = f'{item["_id"].year}-{item["_id"].month:02d}-{item["_id"].day:02d}'
        result[str_date] = item["count"]
    return result


def get_date_aggregated_analytics(name=None, started_at: datetime.datetime = None, ended_at: datetime.datetime = None,
                                  bots_ids: [str] = None):
    pipeline: list = _build_date_aggregated_analytics_pipeline(name, started_at, ended_at, bots_ids)

    received_messages = list(db[f'received_messages'].aggregate(pipeline))
    filtered_messages = list(db[f'filtered_messages'].aggregate(pipeline))

    received_messages_dic = _create_result_dic(started_at, ended_at)
    filtered_messages_dic = _create_result_dic(started_at, ended_at)

    return _prepare_date_analytics_doc(received_messages, received_messages_dic), _prepare_date_analytics_doc(
        filtered_messages, filtered_messages_dic)


def get_bots_aggregated_analytics(from_date: datetime.datetime = None,
                                  to_date: datetime.datetime = None,
                                  bot_ids: Optional[List[str]] = None):
    pipeline = [
        {
            "$group": {
                "_id": "$name",
                "count": {"$sum": 1}
            }
        },
        {"$limit": 1000}
    ]

    if from_date:
        beginning_of_the_day = datetime.datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 0)
        pipeline.insert(0, {"$match": {"created_at": {"$gte": beginning_of_the_day}}})

    if to_date:
        end_of_the_day = datetime.datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 999)
        pipeline.insert(0, {"$match": {"created_at": {"$lte": end_of_the_day}}})

    if bot_ids is not None:
        pipeline.insert(0, {"$match": {"extra_ids": {"$in": bot_ids}}})

    received_messages = list(db[f'received_messages'].aggregate(pipeline))
    filtered_messages = list(db[f'filtered_messages'].aggregate(pipeline))

    received_messages_dic = OrderedDict()
    filtered_messages_dic = OrderedDict()

    for item in received_messages:
        received_messages_dic[item["_id"]] = item["count"]

    for item in filtered_messages:
        filtered_messages_dic[item["_id"]] = item["count"]

    return received_messages_dic, filtered_messages_dic


def get_channel_aggregated_analytics(from_date: datetime.datetime = None, to_date: datetime.datetime = None,
                                     bot_id: Optional[str] = None):
    pipeline = [
        {
            '$match': {
                'extra_ids': {"$in": [str(bot_id)]}
            }
        },
        {
            "$group": {
                '_id': {
                    '$arrayElemAt': [
                        '$attributes', 0
                    ]
                },
                'count': {"$sum": 1}
            }
        },
        {
            '$limit': 1000
        }
    ]

    if from_date:
        beginning_of_the_day = datetime.datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 0)
        pipeline.insert(0, {"$match": {"created_at": {"$gte": beginning_of_the_day}}})

    if to_date:
        end_of_the_day = datetime.datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 999)
        pipeline.insert(0, {"$match": {"created_at": {"$lte": end_of_the_day}}})

    received_messages = list(db[f'received_messages'].aggregate(pipeline))
    filtered_messages = list(db[f'filtered_messages'].aggregate(pipeline))

    received_messages_dic = OrderedDict()
    filtered_messages_dic = OrderedDict()

    for item in received_messages:
        received_messages_dic[item["_id"]] = item["count"]

    for item in filtered_messages:
        filtered_messages_dic[item["_id"]] = item["count"]

    return received_messages_dic, filtered_messages_dic


def get_users_aggregated_analytics(event_type: str = 'user-lead-extended',
                                   from_date: datetime.datetime = None,
                                   to_date: datetime.datetime = None,
                                   email: str = None):
    pipeline = [
        {
            "$group": {
                "_id": "$name",
                "count": {"$sum": 1}
            }
        },
        {"$limit": 1000}
    ]

    if email:
        pipeline.insert(0, {"$match": {"name": email}})

    if from_date:
        beginning_of_the_day = datetime.datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 0)
        pipeline.insert(0, {"$match": {"created_at": {"$gte": beginning_of_the_day}}})

    if to_date:
        end_of_the_day = datetime.datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 999)
        pipeline.insert(0, {"$match": {"created_at": {"$lte": end_of_the_day}}})

    read_messages = list(db[event_type].aggregate(pipeline))
    read_messages_dic = OrderedDict()

    for item in read_messages:
        read_messages_dic[item["_id"]] = item["count"]

    return read_messages_dic


def get_user_date_aggregated_analytics(email=None, event_type: str = 'user-lead-extended',
                                       started_at: datetime.datetime = None,
                                       ended_at: datetime.datetime = None):
    pipeline = _build_date_aggregated_analytics_pipeline(email, started_at, ended_at)

    messages = list(db[event_type].aggregate(pipeline))
    messages_dic = _create_result_dic(started_at, ended_at)

    for item in messages:
        str_date = f'{item["_id"].year}-{item["_id"].month:02d}-{item["_id"].day:02d}'
        messages_dic[str_date] = item["count"]

    return messages_dic


def get_user_read_count(lead_ids: [str]):
    pipeline = [
        {
            "$group":
                {
                    "_id": "$data",
                    "count": {"$sum": 1}
                }
        },
        {
            "$match": {
                "_id": {"$in": lead_ids}
            }
        }
    ]
    messages = list(db['user-lead-extended'].aggregate(pipeline))
    result = dict()

    for message in messages:
        result[message['_id']] = message['count']

    return result


def get_events_leads(email, event, from_date, to_date=None):
    pipeline = {
        'name': email,
        'created_at': {'$gte': from_date}
    }

    if to_date:
        end = datetime.datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, tzinfo=tz.tzutc())
        pipeline['created_at']['$lte'] = end

    return list(db[event].find(pipeline))


def get_leads_aggregation(email, event, from_date, to_date=None):
    pipeline = get_event_pipeline(email, from_date, to_date)
    return list(db[event].aggregate(pipeline))


def get_event_pipeline(email, from_date, to_date=None):
    pipeline = [
        {
            "$match": {
                'name': email,
                'created_at': {'$gte': from_date}
            }
        },
        {
            '$group': {
                '_id': {
                    '$dateFromParts': {
                        'day': {
                            '$dayOfMonth': '$created_at'
                        },
                        'month': {
                            '$month': '$created_at'
                        },
                        'year': {
                            '$year': '$created_at'
                        }
                    }
                },
                'count': {
                    '$sum': 1
                }
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    if to_date:
        end = datetime.datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, tzinfo=tz.tzutc())
        pipeline[0]["$match"]["created_at"]['$lte'] = end

    return pipeline
