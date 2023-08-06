import json

from airflow.providers.http.hooks.http import HttpHook
from airflow.exceptions import AirflowException
from airflow.exceptions import AirflowBadRequest

from json import JSONDecodeError


class Hubspot:

    def __init__(self, hubspot_conn_id):
        self.__hubspot_conn_id = hubspot_conn_id

    def __toTuple(self, item, colNames):
        tuple = (item['id'],)

        for colName in colNames:
            try:
                tuple = tuple + (item['properties'][colName],)
            except KeyError:
                tuple = tuple + ('UNDEFINED',)

        return tuple

    def __labelToTuple(self, labelType, item):
        tuple = (labelType,)
        if item['value'] == "":
            tuple = tuple + ('UNDEFINED',)
        else:
            tuple = tuple + (item['value'],)
        if item['label'] == '':
            tuple = tuple + ('UNDEFINED',)
        else:
            tuple = tuple + (item['label'],)
        return tuple

    def __read_page(self, endpoint, resultProperty, after=None):
        pagedEndpoint = endpoint
        if after != None:
            pagedEndpoint += '&after=' + after
        response = HttpHook(method="GET", http_conn_id=self.__hubspot_conn_id).run(pagedEndpoint)
        try:
            jsonO = json.loads(response.content)
            data = jsonO[resultProperty];
            if 'paging' in jsonO:
                after = jsonO['paging']['next']['after']
                data += self.__read_page(endpoint=endpoint, resultProperty=resultProperty, after=after)
            return data
        except (JSONDecodeError, LookupError, AirflowException) as ex:
            print(ex)
            raise AirflowBadRequest(ex)

    def __companyToTuple(self, item, colNames):
        tuple = (item['id'],)

        for colName in colNames:
            try:
                if item['properties'][colName] == '':
                    tuple = tuple + (None,)
                else:
                    tuple = tuple + (item['properties'][colName],)
            except KeyError:
                tuple = tuple + ('UNDEFINED',)

        try:
            companies = item["associations"]["companies"]["results"]
            companyId = [*filter(lambda x: x["type"] == "deal_to_company", companies)][0]["id"]
        except (KeyError, IndexError):
            companyId = None
        tuple += (companyId,)
        return tuple

    def __stageToTuple(self, item):
        tuple = (item['stageId'], item['label'], item['metadata']['isClosed'], item['metadata']['probability'])
        return tuple

    def __ownerToTuple(self, item):
        tuple = (item['id'], item['email'], item['firstName'], item['lastName'], item['userId'])
        try:
            tuple = tuple + (item['teams'][0]['id'],)
        except KeyError:
            tuple = tuple + ('UNDEFINED',)

        try:
            tuple = tuple + (item['teams'][0]['name'],)
        except KeyError:
            tuple = tuple + ('UNDEFINED',)
        return tuple

    def read_deals(self, colNames):


        dealsEndpoint = "/crm/v4/objects/deals?limit=100&properties=closed_lost_category&properties=critical_opp_review&properties=dealname&properties=dealType&properties=dealstage&properties=amount&properties=deal_currency_code&properties=hy2_market&properties=hy2_product&properties=hy2_application&properties=hubspot_owner_id&properties=hs_deal_stage_probability&properties=hs_exchange_rate&properties=of_systems&properties=expected_delivery&properties=h2_kg_&properties=hy2_battery&properties=hy2_storage&properties=hs_object_id&properties=electrolyzer&properties=sales_team&properties=hy_invoice_co_&properties=hy_mfg_co_&associations=companies"
        dealList = self.__read_page(endpoint=dealsEndpoint, resultProperty='results')
        try:
            data = [*map(lambda x: self.__companyToTuple(x, colNames), dealList)]
            return data

        except (JSONDecodeError, LookupError, AirflowException) as ex:
            print(ex)
            raise AirflowBadRequest(ex)

    def read_companies(self, colNames):
        companiesEndpoint = "/crm/v3/objects/companies?limit=100&properties=city&properties=name&properties=country&properties=industry&properties=state&properties=type"
        companiesList = self.__read_page(endpoint=companiesEndpoint, resultProperty='results')
        try:
            data = [*map(lambda x: self.__toTuple(x, colNames), companiesList)]
            return data

        except (JSONDecodeError, LookupError, AirflowException) as ex:
            print(ex)
            raise AirflowBadRequest(ex)

    def read_stages(self):
        pipelineEndpoint = "/crm-pipelines/v1/pipelines/deals"
        response = HttpHook(method="GET", http_conn_id=self.__hubspot_conn_id).run(pipelineEndpoint)
        try:
            stagesList = json.loads(response.content)["results"][0]["stages"]
            data = [*map(lambda x: self.__stageToTuple(x), stagesList)]
            return data

        except (JSONDecodeError, LookupError, AirflowException) as ex:
            print(ex)
            raise AirflowBadRequest(ex)

    def read_owners(self):
        pipelineEndpoint = "/crm/v3/owners?limit=100"
        response = HttpHook(method="GET", http_conn_id=self.__hubspot_conn_id).run(pipelineEndpoint)
        try:
            ownersList = json.loads(response.content)["results"]
            data = [*map(lambda x: self.__ownerToTuple(x), ownersList)]
            return data

        except (JSONDecodeError, LookupError, AirflowException) as ex:
            print(ex)
            raise AirflowBadRequest(ex)

    def read_labels(self):
        dealsPropertiesEndpoint = "/crm/v3/properties/deals"
        dealsResponse = HttpHook(method="GET", http_conn_id=self.__hubspot_conn_id).run(dealsPropertiesEndpoint)
        companiesPropertiesEndpoint = "/crm/v3/properties/companies"
        companiesResponse = HttpHook(method="GET", http_conn_id=self.__hubspot_conn_id).run(companiesPropertiesEndpoint)
        try:
            dealsResult = json.loads(dealsResponse.content)["results"]
            hy2Applications = [*filter(lambda x: x['name'] == "hy2_application", dealsResult)][0]['options']
            hy2Markets = [*filter(lambda x: x['name'] == "hy2_market", dealsResult)][0]['options']
            dealtypes = [*filter(lambda x: x['name'] == "dealtype", dealsResult)][0]['options']
            hy2Products = [*filter(lambda x: x['name'] == "hy2_product", dealsResult)][0]['options']
            closedLostCategory = [*filter(lambda x: x['name'] == "closed_lost_category", dealsResult)][0]['options']
            expectedDeliveries = [*filter(lambda x: x['name'] == "expected_delivery", dealsResult)][0]['options']
            hy2Batteries = [*filter(lambda x: x['name'] == "hy2_battery", dealsResult)][0]['options']
            hy2Storages = [*filter(lambda x: x['name'] == "hy2_storage", dealsResult)][0]['options']
            electrolyzers = [*filter(lambda x: x['name'] == "electrolyzer", dealsResult)][0]['options']
            salesteams = [*filter(lambda x: x['name'] == "sales_team", dealsResult)][0]['options']

            companiesResult = json.loads(companiesResponse.content)["results"]
            industries = [*filter(lambda x: x['name'] == "industry", companiesResult)][0]['options']
            types = [*filter(lambda x: x['name'] == "type", companiesResult)][0]['options']

            data = [*map(lambda x: self.__labelToTuple('hy2_application', x), hy2Applications)]
            data = data + [*map(lambda x: self.__labelToTuple('hy2_market', x), hy2Markets)]
            data = data + [*map(lambda x: self.__labelToTuple('dealtype', x), dealtypes)]
            data = data + [*map(lambda x: self.__labelToTuple('hy2_product', x), hy2Products)]
            data = data + [*map(lambda x: self.__labelToTuple('closed_lost_category', x), closedLostCategory)]
            data = data + [*map(lambda x: self.__labelToTuple('expected_delivery', x), expectedDeliveries)]
            data = data + [*map(lambda x: self.__labelToTuple('hy2_battery', x), hy2Batteries)]
            data = data + [*map(lambda x: self.__labelToTuple('hy2_storage', x), hy2Storages)]
            data = data + [*map(lambda x: self.__labelToTuple('electrolyzer', x), electrolyzers)]
            data = data + [*map(lambda x: self.__labelToTuple('salesteam', x), salesteams)]

            data = data + [*map(lambda x: self.__labelToTuple('industry', x), industries)]
            data = data + [*map(lambda x: self.__labelToTuple('type', x), types)]
            return data

        except (JSONDecodeError, LookupError, AirflowException) as ex:
            print(ex)
            raise AirflowBadRequest(ex)

