# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from dojah_client.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    KYC = "KYC"
    FINANCIAL = "Financial"
    GENERAL = "General"
    AUTHENTICATION = "Authentication"
    WALLET = "Wallet"
    KYB = "KYB"
    ML = "ML"
    WEB_HOOKS = "WebHooks"
    GH_KYC = "GH KYC"
    AML = "AML"
    SERVICES = "Services"
    UG_KYC = "UG KYC"
    KE_KYC = "KE KYC"
