import requests

from dcentrapi.Base import Base


class Web3Index(Base):
    # ----- Data from DUB Backend -----

    def get_reserves_from_pairs(self, pools: list, network, rpc_url=None):
        url = self.url + "getReservesFromPairs"
        data = {"network": network, "lp_tokens": pools, "rpc_url": rpc_url}
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    # ----- Data from Web3Index -----

    def get_pairs(self, network_name: str, token_address: str):
        url = self.web3index_url + "pairs" + f"/{network_name}/{token_address}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_factories(self):
        url = self.web3index_url + "factories"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_token_price_snapshot(self, info):
        # Currently info is token symbol (str), e.g. "XCAD"
        # In future, might also have the base token id (int)
        url = self.web3index_url + "token_price_snapshot" + f"/{info}"
        response = requests.get(url, headers=self.headers)
        return response.json()
