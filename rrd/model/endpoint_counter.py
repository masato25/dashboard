#-*- coding:utf-8 -*-
from rrd.store import graph_db_conn as db_conn
import re

class EndpointCounter(object):
    def __init__(self, id, endpoint_id, counter, step, type_):
        self.id = str(id)
        self.endpoint_id = str(endpoint_id)
        self.counter = counter
        self.step = step
        self.type_ = type_

    def __repr__(self):
        return "<EndpointCounter id=%s, endpoint_id=%s, counter=%s>" %(self.id, self.endpoint_id, self.counter)
    __str__ = __repr__

    @classmethod
    def search_in_endpoint_ids(cls, qs, endpoint_ids, start=0, limit=100):
        if not endpoint_ids:
            return []

        holders = ["%s" for x in endpoint_ids]
        placeholder = ",".join(holders)

        args = endpoint_ids

        sql = '''select id, endpoint_id, counter, step, type from endpoint_counter where endpoint_id in (''' +placeholder+ ''') '''
        tags = {}
        isPacketLossRate = False
        isAverage = False

        for q in qs:
            matchObj = re.match('([^\0]+)=([^\0]+)', q)
            if matchObj:
                tags[matchObj.group(1)] = matchObj.group(2).split(',')
            else:
                if "packet-loss-rate" in q:
                    q = "packets-sent"
                    isPacketLossRate = True
                if "average" in q:
                    q = "transmission-time"
                    isAverage = True
                args.append("%"+q+"%")
                sql += ''' and counter like %s'''

        if 'isp' in tags:
            sql += ''' and ('''
            for isp in tags['isp'][:-1]:
                args.append("%"+isp+"%")
                sql += ''' counter like %s or'''
            args.append("%"+tags['isp'][-1]+"%")
            sql += ''' counter like %s )'''
        if 'province' in tags:
            sql += ''' and ('''
            for province in tags['province'][:-1]:
                args.append("%"+province+"%")
                sql += ''' counter like %s or'''
            args.append("%"+tags['province'][-1]+"%")
            sql += ''' counter like %s )'''
        if 'city' in tags:
            sql += ''' and ('''
            for city in tags['city'][:-1]:
                args.append("%"+city+"%")
                sql += ''' counter like %s or'''
            args.append("%"+tags['city'][-1]+"%")
            sql += ''' counter like %s )'''
        if 'tag' in tags:
            sql += ''' and ('''
            for tag in tags['tag'][:-1]:
                args.append("%"+tag+"%")
                sql += ''' counter like %s or'''
            args.append("%"+tags['tag'][-1]+"%")
            sql += ''' counter like %s )'''

        args += [start, limit]
        sql += ''' limit %s,%s'''

        cursor = db_conn.execute(sql, args)
        rows = cursor.fetchall()
        cursor and cursor.close()

        if isPacketLossRate:
            rows = list(rows)
            newLists = list()
            #for row in rows:
            #    newList = list(row)
            #    newList[2] = 'packet-loss-rate'
            #    newList = tuple(newList)
            #    newLists.append(newList)
            newList = list(rows[0]) # 隨便找一個
            newList[2] = 'packet-loss-rate'
            newList = tuple(newList)
            newLists.append(newList)

            rows = rows + newLists
            rows = tuple(rows)
        elif isAverage:
            rows = list(rows)
            newLists = list()
            newList = list(rows[0]) # 隨便找一個
            newList[2] = 'average'
            newList = tuple(newList)
            newLists.append(newList)

            rows = rows + newLists
            rows = tuple(rows)
        return [cls(*row) for row in rows]

    @classmethod
    def gets_by_endpoint_ids(cls, endpoint_ids, start=0, limit=100):
        if not endpoint_ids:
            return []

        holders = ["%s" for x in endpoint_ids]
        placeholder = ",".join(holders)
        args = endpoint_ids + [start, limit]

        cursor = db_conn.execute('''select id, endpoint_id, counter, step, type from endpoint_counter where endpoint_id in ('''+placeholder+''') limit %s, %s''', args)
        rows = cursor.fetchall()
        cursor and cursor.close()

        return [cls(*row) for row in rows]

    @classmethod
    def gets(cls, ids, deadline=0):
        if not ids:
            return []

        holders = ["%s" for x in ids]
        placeholder = ",".join(holders)
        args = ids + [start, limit]

        cursor = db_conn.execute('''select id, endpoint, ts from endpoint where id in ('''+placeholder+''') and ts > %s''', args)
        rows = cursor.fetchall()
        cursor and cursor.close()

        return [cls(*row) for row in rows]
