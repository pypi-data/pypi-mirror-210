import requests

from dcentrapi.Base import Base


class EventPolling(Base):
    def get_collection(self, collection_name):
        url = self.url + "event_polling/collection"
        data = {"collection_name": collection_name}
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_latest_contract_version(self, contract_name):
        url = self.url + "event_polling/get_latest_contract_version"  # test comment for deployment trigger
        data = {"contract_name": contract_name}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def register_user(self, user_name: str, collection_name: str):
        url = self.url + "event_polling/register_user"
        data = {
            "user_name": user_name,
            "collection_name": collection_name,
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def subscribe_contract(
        self, contract_name, contract_address, network, abi, collection_name, contract_version=None, git_tag=None
    ):
        url = self.url + "event_polling/subscribe_contract"
        data = {
            "contract_name": contract_name,
            "contract_address": contract_address,
            "contract_version": contract_version,
            "network": network,
            "collection_name": collection_name,
            "abi": abi,
            "git_tag": git_tag,
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_schema(self, contract_name, contract_version):
        url = self.url + "event_polling/schema"
        data = {"contract_name": contract_name, "contract_version": contract_version}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_events_sum_of_values_in_range(
        self, collection_name, contract_address, event_name, field_name, start_time, end_time
    ):
        url = self.url + "event_polling/events_sum_of_values_in_range"
        data = {
            "collection_name": collection_name,
            "contract_address": contract_address,
            "event_name": event_name,
            "field_name": field_name,
            "start_time": start_time,
            "end_time": end_time,
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_sum_of_values_in_range(self, collection_name, event_name, field_name, start_time, end_time):
        url = self.url + "event_polling/collection_sum_of_values_in_range"
        data = {
            "collection_name": collection_name,
            "event_name": event_name,
            "field_name": field_name,
            "start_time": start_time,
            "end_time": end_time,
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_contracts_sum_of_values(self, collection_name, event_name, field_name, start_time, end_time):
        url = self.url + "event_polling/collection_contracts_sum_of_values"
        data = {
            "collection_name": collection_name,
            "event_name": event_name,
            "field_name": field_name,
            "start_time": start_time,
            "end_time": end_time,
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_daily_nof_transactions(self, collection_name, start_time, end_time):
        url = self.url + "event_polling/collection_daily_nof_transactions"
        data = {"collection_name": collection_name, "start_time": start_time, "end_time": end_time}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_nof_transactions(self, collection_name):
        url = self.url + "event_polling/collection_nof_transactions"
        data = {"collection_name": collection_name}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_nof_transactions_by_time(self, collection_name, start_time, end_time):
        url = self.url + "event_polling/collection_nof_transactions_by_time"
        data = {"collection_name": collection_name, "start_time": start_time, "end_time": end_time}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_nof_users_in_time_range(self, collection_name, start_time, end_time):
        url = self.url + "event_polling/collection_nof_users_in_time_range"
        data = {"collection_name": collection_name, "start_time": start_time, "end_time": end_time}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_contract_nof_transactions(self, collection_name, contract_address):
        url = self.url + "event_polling/contract_nof_transactions"
        data = {"collection_name": collection_name, "contract_address": contract_address}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_users_in_time_range(self, collection_name, start_time, end_time):
        url = self.url + "event_polling/collection_users_in_time_range"
        data = {"collection_name": collection_name, "start_time": start_time, "end_time": end_time}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_contract_users_in_time_range(self, collection_name, contract_address, start_time, end_time):
        url = self.url + "event_polling/contract_users_in_time_range"
        data = {
            "collection_name": collection_name,
            "contract_address": contract_address,
            "start_time": start_time,
            "end_time": end_time,
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_contracts_events_info(
        self, collection_name, contract_addresses, event_names, user_web3_addresses=None, start_time=None, end_time=None
    ):
        url = self.url + "event_polling/contracts_events_info"
        data = {
            "collection_name": collection_name,
            "contract_addresses": contract_addresses,
            "start_time": start_time,
            "end_time": end_time,
            "user_web3_addresses": user_web3_addresses,
            "event_names": event_names,
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_nof_contracts_events_unique_transactions(self, collection_name, contract_addresses, event_names):
        url = self.url + "event_polling/contracts_events_info"
        data = {
            "collection_name": collection_name,
            "contract_addresses": contract_addresses,
            "event_names": event_names,
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_nof_token_transfers(self, contract_addresses):
        url = self.url + "event_polling/token_transfers"
        data = {"contract_addresses": contract_addresses}
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_event_details(self, collection_name, list_of_events, event_parameter):
        url = self.url + "event_polling/get_event_details"
        data = {
            "collection_name": collection_name,
            "list_of_events": list_of_events,
            "event_parameter": event_parameter,
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
