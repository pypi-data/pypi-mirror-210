import typing_extensions

from dojah_client.apis.tags import TagValues
from dojah_client.apis.tags.kyc_api import KYCApi
from dojah_client.apis.tags.financial_api import FinancialApi
from dojah_client.apis.tags.general_api import GeneralApi
from dojah_client.apis.tags.authentication_api import AuthenticationApi
from dojah_client.apis.tags.wallet_api import WalletApi
from dojah_client.apis.tags.kyb_api import KYBApi
from dojah_client.apis.tags.ml_api import MLApi
from dojah_client.apis.tags.web_hooks_api import WebHooksApi
from dojah_client.apis.tags.ghkyc_api import GHKYCApi
from dojah_client.apis.tags.aml_api import AMLApi
from dojah_client.apis.tags.services_api import ServicesApi
from dojah_client.apis.tags.ugkyc_api import UGKYCApi
from dojah_client.apis.tags.kekyc_api import KEKYCApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.KYC: KYCApi,
        TagValues.FINANCIAL: FinancialApi,
        TagValues.GENERAL: GeneralApi,
        TagValues.AUTHENTICATION: AuthenticationApi,
        TagValues.WALLET: WalletApi,
        TagValues.KYB: KYBApi,
        TagValues.ML: MLApi,
        TagValues.WEB_HOOKS: WebHooksApi,
        TagValues.GH_KYC: GHKYCApi,
        TagValues.AML: AMLApi,
        TagValues.SERVICES: ServicesApi,
        TagValues.UG_KYC: UGKYCApi,
        TagValues.KE_KYC: KEKYCApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.KYC: KYCApi,
        TagValues.FINANCIAL: FinancialApi,
        TagValues.GENERAL: GeneralApi,
        TagValues.AUTHENTICATION: AuthenticationApi,
        TagValues.WALLET: WalletApi,
        TagValues.KYB: KYBApi,
        TagValues.ML: MLApi,
        TagValues.WEB_HOOKS: WebHooksApi,
        TagValues.GH_KYC: GHKYCApi,
        TagValues.AML: AMLApi,
        TagValues.SERVICES: ServicesApi,
        TagValues.UG_KYC: UGKYCApi,
        TagValues.KE_KYC: KEKYCApi,
    }
)
