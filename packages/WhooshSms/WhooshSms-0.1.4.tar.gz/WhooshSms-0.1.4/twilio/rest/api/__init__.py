from warnings import warn

from twilio.rest.api.ApiBase import ApiBase
from twilio.rest.api.v2010.account import AccountContext, AccountList


class Api(ApiBase):
    @property
    def account(self) -> AccountContext:
        return self.v2010.account

    @property
    def accounts(self) -> AccountList:
        return self.v2010.accounts
    