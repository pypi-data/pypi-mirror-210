from dcentrapi.common import get_dapi_version


class Base:
    def __init__(self, stage, username=None, key=None):
        self.__version__ = get_dapi_version()

        if stage == "develop":
            self.headers = {"Authorization": username + "," + key}
            self.url = "https://test-api.dcentralab.com/"
            self.web3index_url = "https://test-api.web3index.info/"
        if stage == "staging":
            self.headers = {"Authorization": username + "," + key}
            self.url = "https://staging.dcentralab.com/"
            self.web3index_url = "https://staging-api.web3index.info/"
        if stage == "main":
            self.headers = {"Authorization": username + "," + key}
            self.url = "https://main-api.dcentralab.com/"
            self.web3index_url = "https://api.web3index.info/"
