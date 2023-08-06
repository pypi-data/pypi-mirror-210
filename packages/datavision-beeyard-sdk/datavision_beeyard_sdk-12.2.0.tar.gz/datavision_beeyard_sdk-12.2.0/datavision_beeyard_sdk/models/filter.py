import datetime


class Filter:
    def id_collection(param: []):
        id_list = [f'UUID("{i}")' for i in param]
        return f'{{"_id":{{"$in":[{", ".join(map(str, id_list))}]}}}}'

    def tags(param):
        tag_list = [f'{{"category":"{i.category}", "name":"{i.name}"}}' for i in param]
        return f'{{"tags":{{"$all":[{", ".join(map(str, tag_list))}]}}}}'

    def tag_not_present(param):
        tag_list = [f'{{"category":"{i.category}", "name":"{i.name}"}}' for i in param]
        return f'{{"tags":{{"$nin":[{", ".join(map(str, tag_list))}]}}}}'

    def date_created_between(param):
        time_list = []
        for date in param:
            date_time_obj = datetime.datetime.strptime(date, "%d-%m-%Y %H:%M")
            time_list.append(date_time_obj.isoformat())
        return f'{{"$and":[ \
            {{"created":\
              {{"$gt":ISODate("{time_list[0]}")}}}}, \
                {{"created":\
                  {{"$lt":ISODate("{time_list[1]}")}}}}]}}'

    def date_modified_between(param):
        time_list = []
        for date in param:
            date_time_obj = datetime.datetime.strptime(date, "%d-%m-%Y %H:%M")
            time_list.append(date_time_obj.isoformat())
        return f'{{"$and":[ \
            {{"modified":\
              {{"$gt":ISODate("{time_list[0]}")}}}}, \
                {{"modified":\
                  {{"$lt":ISODate("{time_list[1]}")}}}}]}}'

    def date_uploaded_between(param):
        time_list = []
        for date in param:
            date_time_obj = datetime.datetime.strptime(date, "%d-%m-%Y %H:%M")
            time_list.append(date_time_obj.isoformat())
        return f'{{"$and":[ \
            {{"uploaded":\
              {{"$gt":ISODate("{time_list[0]}")}}}}, \
                {{"uploaded":\
                  {{"$lt":ISODate("{time_list[1]}")}}}}]}}'

    def date_created_before(param):
        date_time_obj = datetime.datetime.strptime(param, "%d-%m-%Y %H:%M")
        time_list = date_time_obj.isoformat()
        return f'{{"created":{{"$lt":ISODate("{time_list}")}}}}'

    def date_created_after(param):
        date_time_obj = datetime.datetime.strptime(param, "%d-%m-%Y %H:%M")
        time_list = date_time_obj.isoformat()
        return f'{{"created":{{"$gt":ISODate("{time_list}")}}}}'

    def property_equals(param):
        prop_list = [f'{{"key":"{i.category}", "value":"{i.name}"}}' for i in param]
        return f'{{"properties":{{"$all":[{", ".join(map(str, prop_list))}]}}}}'

    def create_or_filter(filters: []):
        return f'{{"$or":[{", ".join(map(str, filters))}]}}'

    def create_and_filter(filters: []):
        return f'{{"$and":[{", ".join(map(str, filters))}]}}'
