import json

from airflow.providers.http.hooks.http import HttpHook
from airflow.exceptions import AirflowException
from airflow.exceptions import AirflowBadRequest

from json import JSONDecodeError


class Planio:
    __customFields = [
        {'column': 'project_status', 'name': 'Project Status'},
        {'column': 'customer', 'name': 'Customer'},
        {'column': 'to_invoice', 'name': 'to invoice'},
        {'column': 'invoiced', 'name': 'invoiced'},
        {'column': 'additional_requirement', 'name': 'Additional requirement'},
    ]

    __refrenceFields = [
        {'column': 'project_id', 'ref': ['project', 'id']},
        {'column': 'user_id', 'ref': ['user', 'id']},
        {'column': 'activity_id', 'ref': ['activity', 'id']},
        {'column': 'activity_name', 'ref': ['activity', 'name']},
        {'column': 'tracker_id', 'ref': ['tracker', 'id']},
        {'column': 'tracker_name', 'ref': ['tracker', 'name']},
        {'column': 'status_id', 'ref': ['status', 'id']},
        {'column': 'status_name', 'ref': ['status', 'name']},
        {'column': 'priority_id', 'ref': ['priority', 'id']},
        {'column': 'issue_id', 'ref': ['issue', 'id']},
        {'column': 'priority_name', 'ref': ['priority', 'name']},
        {'column': 'author_id', 'ref': ['author', 'id']},
        {'column': 'assigned_to', 'ref': ['assigned_to', 'id']},
        {'column': 'fixed_version_id', 'ref': ['fixed_version', 'id']},
    ]

    userColumns = ['id', 'login', 'firstname', 'lastname', 'mail']
    projectColumns = ['id', 'name', 'identifier', 'description', 'customer', 'status']
    timeEntryColumns = ['id', 'issue_id', 'user_id', 'activity_id', 'activity_name', 'hours', 'comments', 'spent_on']
    versionColumns = ['id', 'project_id', 'name', 'description', 'status', 'due_date', 'to_invoice', 'invoiced']
    issueColumns = ['id', 'project_id', 'tracker_id', 'tracker_name', 'fixed_version_id', 'status_id', 'status_name', 'priority_id', 'priority_name', 'author_id', 'assigned_to', 'subject', 'description', 'estimated_hours', 'spent_hours', 'additional_requirement']
    customFieldColumns = ['value', 'label']

    def __init__(self, planio_connection_id):
        self.__planio_connection_id = planio_connection_id

    def __toTuple(self, item, columns):
        tuple = ();
        for column in columns:
            customField = list(filter(lambda cf: cf['column'] == column, self.__customFields))
            referenceField = list(filter(lambda cf: cf['column'] == column, self.__refrenceFields))
            if len(customField) > 0:
                try:
                    customValue = list(filter(lambda x: x["name"] == customField[0]["name"], item["custom_fields"]));
                    if (len(customValue) > 0):
                        tuple += (customValue[0]["value"],);
                    else:
                        tuple += (None,)
                except (KeyError):
                    tuple += (None,)

            elif (len(referenceField) > 0):
                value = item
                for prop in referenceField[0]['ref']:
                    try:
                        value = value[prop]
                    except (KeyError):
                        value = None
                        break
                tuple += (value,)
            else:
                tuple += (item[column],)
        return tuple

    def __toTuples(self, arr, columns):
        return list(map(lambda item: self.__toTuple(item=item, columns=columns), arr))

    def __read_pages(self, endpoint, resultProperty, offset, limit):
        pagedEndpoint = f'{endpoint}&limit={limit}&offset={offset}'
        http = HttpHook(method="GET", http_conn_id=self.__planio_connection_id)
        response = http.run(pagedEndpoint)
        try:
            jsonO = json.loads(response.content)
            data = jsonO[resultProperty];
            totalCount = jsonO['total_count']
            if totalCount > offset + limit:
                offset = offset + limit
                data += self.__read_pages(endpoint=endpoint, resultProperty=resultProperty, offset=offset, limit=limit)
            return data
        except (JSONDecodeError, LookupError, AirflowException) as ex:
            print(ex)
            raise AirflowBadRequest(ex)

    def __loadProperty(self, property, columns, query=None):
        endpoint = f'/{property}.json?encoding=UTF-8'
        if query != None:
            endpoint += query
        limit = 100
        offset = 0;
        data = self.__read_pages(endpoint=endpoint, resultProperty=property, offset=offset, limit=limit)
        return self.__toTuples(arr=data, columns=columns)


    def loadUsers(self, columns):
        return self.__loadProperty(property='users', columns=columns)

    def loadProjects(self, columns):
        return self.__loadProperty(property='projects', columns=columns)

    def loadIssues(self, columns):
        query = "&status_id=*&created_on=%3E%3D2022-01-01"
        return self.__loadProperty(property='issues', columns=columns, query=query)

    def loadTimeEntries(self, columns, date):
        query = "&spent_on={}".format(date)
        return self.__loadProperty(property='time_entries', columns=columns, query=query)

    def __loadVersionsOfProject(self, columns, projectId):
        endpoint = f'/projects/{projectId}/versions.json?encoding=UTF-8'
        resultProperty = 'versions'
        limit = 100
        offset = 0;
        data = self.__read_pages(endpoint=endpoint, resultProperty=resultProperty, offset=offset, limit=limit)
        return self.__toTuples(arr=data, columns=columns)

    def loadVersions(self, columns):
        versions = [];
        for tuple in self.loadProjects(columns=['id', 'status']):
            if (int(tuple[1] == 1)):
                try:
                    versions += self.__loadVersionsOfProject(columns=columns, projectId=tuple[0])
                except (AirflowException):
                    pass
        return versions

    def loadCustomFields(self, customFieldName):
        endpoint = '/custom_fields.json?encoding=UTF-8'
        http = HttpHook(method="GET", http_conn_id=self.__planio_connection_id)
        response = http.run(endpoint)
        try:
            jsonO = json.loads(response.content)['custom_fields']
            print('-----------')
            print(jsonO)
            iterable = list(jsonO)
            data = list(filter(lambda cf: cf['name'] == 'Customer', iterable))
            #customField = list(filter(lambda cf: cf['column'] == column, self.__customFields))

            self.__toTuples(arr=data[0]['possible_values'], columns=self.customFieldColumns)
        except (JSONDecodeError, LookupError, AirflowException) as ex:
            print(ex)
            raise AirflowBadRequest(ex)
