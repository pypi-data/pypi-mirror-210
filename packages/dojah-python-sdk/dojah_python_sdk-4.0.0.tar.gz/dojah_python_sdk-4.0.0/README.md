# dojah-python-sdk@4.0.0
Use Dojah to verify, onboard and manage user identity across Africa!


## Requirements

Python >=3.7

## Installing

```sh
pip install dojah-python-sdk==4.0.0
```

## Getting Started

```python
from pprint import pprint
from dojah_client import Dojah, ApiException

dojah = Dojah(
    # Defining the host is optional and defaults to https://api.dojah.io
    # See configuration.py for a list of all supported configuration parameters.
    host="https://api.dojah.io",
    # Configure API key authorization: apikeyAuth
    authorization="YOUR_API_KEY",
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # api_key_prefix = {'apikeyAuth': 'Bearer'},
    # Configure API key authorization: appIdAuth
    app_id="YOUR_API_KEY",
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # api_key_prefix = {'appIdAuth': 'Bearer'},
)

try:
    # Get AML Info
    get_screening_info_response = dojah.aml.get_screening_info(
        reference_id="c574a3c8-dc27-4013-8bbc-462e7ed87d55",  # optional
    )
    pprint(get_screening_info_response.body)
    pprint(get_screening_info_response.body["entity"])
    pprint(get_screening_info_response.headers)
    pprint(get_screening_info_response.status)
    pprint(get_screening_info_response.round_trip_time)
except ApiException as e:
    print("Exception when calling AMLApi.get_screening_info: %s\n" % e)
    pprint(e.body)
    pprint(e.headers)
    pprint(e.status)
    pprint(e.reason)
    pprint(e.round_trip_time)
```

## Async

`async` support is available by prepending `a` to any method.

```python
import asyncio
from pprint import pprint
from dojah_client import Dojah, ApiException

dojah = Dojah(
    # Defining the host is optional and defaults to https://api.dojah.io
    # See configuration.py for a list of all supported configuration parameters.
    host="https://api.dojah.io",
    # Configure API key authorization: apikeyAuth
    authorization="YOUR_API_KEY",
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # api_key_prefix = {'apikeyAuth': 'Bearer'},
    # Configure API key authorization: appIdAuth
    app_id="YOUR_API_KEY",
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # api_key_prefix = {'appIdAuth': 'Bearer'},
)


async def main():
    try:
        # Get AML Info
        get_screening_info_response = await dojah.aml.aget_screening_info(
            reference_id="c574a3c8-dc27-4013-8bbc-462e7ed87d55",  # optional
        )
        pprint(get_screening_info_response.body)
        pprint(get_screening_info_response.body["entity"])
        pprint(get_screening_info_response.headers)
        pprint(get_screening_info_response.status)
        pprint(get_screening_info_response.round_trip_time)
    except ApiException as e:
        print("Exception when calling AMLApi.get_screening_info: %s\n" % e)
        pprint(e.body)
        pprint(e.headers)
        pprint(e.status)
        pprint(e.reason)
        pprint(e.round_trip_time)


asyncio.run(main())
```


## Documentation for API Endpoints

All URIs are relative to *https://api.dojah.io*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AMLApi* | [**get_screening_info**](docs/apis/tags/AMLApi.md#get_screening_info) | **get** /v1/aml/screening/info | Get AML Info
*AMLApi* | [**screen_aml**](docs/apis/tags/AMLApi.md#screen_aml) | **post** /api/v1/aml/screening | AML Screening
*AuthenticationApi* | [**get_sender_id**](docs/apis/tags/AuthenticationApi.md#get_sender_id) | **get** /api/v1/messaging/sender_ids | Messaging - Get Sender IDs
*AuthenticationApi* | [**get_sms_status**](docs/apis/tags/AuthenticationApi.md#get_sms_status) | **get** /v1/messaging/sms/get_status | Messaging - Get SMS Status
*AuthenticationApi* | [**request_sender_id**](docs/apis/tags/AuthenticationApi.md#request_sender_id) | **post** /api/v1/messaging/sender_id | Messaging - Request Sender ID
*AuthenticationApi* | [**send_otp**](docs/apis/tags/AuthenticationApi.md#send_otp) | **post** /v1/messaging/otp | Messaging - Send OTP
*AuthenticationApi* | [**send_sms**](docs/apis/tags/AuthenticationApi.md#send_sms) | **post** /api/v1/messaging/sms | Messaging - Send SMS
*AuthenticationApi* | [**validate_otp**](docs/apis/tags/AuthenticationApi.md#validate_otp) | **get** /v1/messaging/otp/validate | Messaging - Validate OTP
*FinancialApi* | [**collect_status_from_pdf**](docs/apis/tags/FinancialApi.md#collect_status_from_pdf) | **post** /api/v1/financial/transactions/pdf | Collect Status via PDF Statement
*FinancialApi* | [**collect_transactions**](docs/apis/tags/FinancialApi.md#collect_transactions) | **post** /v1/financial/transactions | Collect Transactions
*FinancialApi* | [**get_account**](docs/apis/tags/FinancialApi.md#get_account) | **get** /api/v1/financial/account_information | Get Account Information
*FinancialApi* | [**get_account_analysis**](docs/apis/tags/FinancialApi.md#get_account_analysis) | **get** /api/v1/financial/analysis | Get Account Analysis
*FinancialApi* | [**get_account_subscriptions**](docs/apis/tags/FinancialApi.md#get_account_subscriptions) | **get** /v1/financial/account_subscription | Get Account Subscriptions
*FinancialApi* | [**get_account_transactions**](docs/apis/tags/FinancialApi.md#get_account_transactions) | **get** /api/v1/financial/account_transactions | Get Account Transactions
*FinancialApi* | [**get_basic_bvn**](docs/apis/tags/FinancialApi.md#get_basic_bvn) | **get** /v1/financial/bvn_information/basic | Get BVN Information Basic
*FinancialApi* | [**get_earning_structure**](docs/apis/tags/FinancialApi.md#get_earning_structure) | **get** /v1/financial/earning_structure | Get Earning Structure
*FinancialApi* | [**get_full_bvn**](docs/apis/tags/FinancialApi.md#get_full_bvn) | **get** /v1/financial/bvn_information/full | Get BVN Information Full
*FinancialApi* | [**get_spending_pattern**](docs/apis/tags/FinancialApi.md#get_spending_pattern) | **get** /v1/financial/spending_pattern | Get Spending Pattern
*GHKYCApi* | [**get_drivers_license**](docs/apis/tags/GHKYCApi.md#get_drivers_license) | **get** /api/v1/gh/kyc/dl | Driver&#x27;s License
*GHKYCApi* | [**get_passport**](docs/apis/tags/GHKYCApi.md#get_passport) | **get** /api/v1/gh/kyc/passport | Passport
*GHKYCApi* | [**get_ssnit**](docs/apis/tags/GHKYCApi.md#get_ssnit) | **get** /api/v1/gh/kyc/ssnit | SSNIT
*GeneralApi* | [**get_banks**](docs/apis/tags/GeneralApi.md#get_banks) | **get** /v1/general/banks | General - Get Banks
*GeneralApi* | [**get_bin**](docs/apis/tags/GeneralApi.md#get_bin) | **get** /v1/general/bin | General Resolve BIN
*GeneralApi* | [**get_data_plans**](docs/apis/tags/GeneralApi.md#get_data_plans) | **get** /v1/purchase/data/plans | Purchase - Get Data Plans
*GeneralApi* | [**get_nuban**](docs/apis/tags/GeneralApi.md#get_nuban) | **get** /v1/general/account | General Resolve NUBAN
*GeneralApi* | [**get_wallet_balance**](docs/apis/tags/GeneralApi.md#get_wallet_balance) | **get** /api/v1/balance | Get Dojah Wallet Balance
*GeneralApi* | [**purchase_airtime**](docs/apis/tags/GeneralApi.md#purchase_airtime) | **post** /v1/purchase/airtime | Purchase - Send Airtime
*GeneralApi* | [**purchase_data**](docs/apis/tags/GeneralApi.md#purchase_data) | **post** /v1/purchase/data | Purchase - Buy Data
*KEKYCApi* | [**get_national_id**](docs/apis/tags/KEKYCApi.md#get_national_id) | **get** /api/v1/ke/kyc/id | KYC - National ID
*KYBApi* | [**get_advanced_cac**](docs/apis/tags/KYBApi.md#get_advanced_cac) | **get** /v1/kyc/cac/advance | KYC - Get CAC Advanced
*KYBApi* | [**get_basic_cac**](docs/apis/tags/KYBApi.md#get_basic_cac) | **get** /v1/kyc/cac/basic | KYB - Get CAC 2
*KYBApi* | [**get_cac**](docs/apis/tags/KYBApi.md#get_cac) | **get** /v1/kyc/cac | KYC - Get CAC 
*KYBApi* | [**get_tin**](docs/apis/tags/KYBApi.md#get_tin) | **get** /v1/kyc/tin | KYC - Fetch Tin
*KYCApi* | [**analyze_document**](docs/apis/tags/KYCApi.md#analyze_document) | **post** /api/v1/document/analysis | KYC - Document Analysis
*KYCApi* | [**get_basic_bvn**](docs/apis/tags/KYCApi.md#get_basic_bvn) | **get** /api/v1/kyc/bvn/basic | KYC - Get Basic BVN Info
*KYCApi* | [**get_basic_phone_number**](docs/apis/tags/KYCApi.md#get_basic_phone_number) | **get** /v1/kyc/phone_number/basic | KYC Lookup Phone Number Basic
*KYCApi* | [**get_drivers_license**](docs/apis/tags/KYCApi.md#get_drivers_license) | **get** /api/v1/kyc/dl | KYC - Get Drivers License Info
*KYCApi* | [**get_email_reputation**](docs/apis/tags/KYCApi.md#get_email_reputation) | **get** /v1/kyc/email | KYC - Get Email Reputation
*KYCApi* | [**get_full_bvn**](docs/apis/tags/KYCApi.md#get_full_bvn) | **get** /api/v1/kyc/bvn/full | KYC - Lookup BVN Basic
*KYCApi* | [**get_nuban**](docs/apis/tags/KYCApi.md#get_nuban) | **get** /api/v1/kyc/nuban | KYC - Get NUBAN Information
*KYCApi* | [**get_passport**](docs/apis/tags/KYCApi.md#get_passport) | **get** /api/v1/kyc/passport | KYC - Passport
*KYCApi* | [**get_phone_number**](docs/apis/tags/KYCApi.md#get_phone_number) | **get** /api/v1/kyc/phone_number | KYC - Lookup Phone Number
*KYCApi* | [**get_premium_bvn**](docs/apis/tags/KYCApi.md#get_premium_bvn) | **get** /api/v1/kyc/bvn/advance | KYC - Lookup BVN Premium
*KYCApi* | [**get_vin**](docs/apis/tags/KYCApi.md#get_vin) | **get** /api/v1/kyc/vin | KYC - Get VIN
*KYCApi* | [**get_vnin**](docs/apis/tags/KYCApi.md#get_vnin) | **get** /api/v1/kyc/vnin | Lookup VNIN
*KYCApi* | [**validate_bvn**](docs/apis/tags/KYCApi.md#validate_bvn) | **get** /api/v1/kyc/bvn | KYC - Validate BVN
*KYCApi* | [**verify_age**](docs/apis/tags/KYCApi.md#verify_age) | **get** /v1/kyc/age_verification | KYC - Age Verification
*KYCApi* | [**verify_selfie_bvn**](docs/apis/tags/KYCApi.md#verify_selfie_bvn) | **post** /v1/kyc/bvn/verify | KYC - Selfie BVN Verificatoin
*KYCApi* | [**verify_selfie_nin**](docs/apis/tags/KYCApi.md#verify_selfie_nin) | **post** /v1/kyc/nin/verify | KYC - Selfie NIN Verification
*MLApi* | [**get_document_analysis**](docs/apis/tags/MLApi.md#get_document_analysis) | **post** /v1/document/analysis/dl | Document Analysis Drivers License
*MLApi* | [**get_generic_ocr_text**](docs/apis/tags/MLApi.md#get_generic_ocr_text) | **post** /v1/ml/ocr/generic | Generic OCR Service
*MLApi* | [**get_ocr_text**](docs/apis/tags/MLApi.md#get_ocr_text) | **post** /v1/ml/ocr | BVN Ocr
*MLApi* | [**verify_photo_id_with_selfie**](docs/apis/tags/MLApi.md#verify_photo_id_with_selfie) | **post** /v1/kyc/photoid/verify | KYC - Selfie Photo ID Verification
*ServicesApi* | [**categorize_transactions**](docs/apis/tags/ServicesApi.md#categorize_transactions) | **post** /v1/ml/categorize_transaction | Categorize Transactions
*UGKYCApi* | [**get_voter**](docs/apis/tags/UGKYCApi.md#get_voter) | **get** /api/v1/ug/kyc/voter | Voters ID
*WalletApi* | [**create_wallet**](docs/apis/tags/WalletApi.md#create_wallet) | **post** /v1/wallet/ngn/create | Create NGN Wallet
*WalletApi* | [**credit_subwallet**](docs/apis/tags/WalletApi.md#credit_subwallet) | **post** /v1/wallet/ngn/credit | Credit Sub-wallet
*WalletApi* | [**get_transaction**](docs/apis/tags/WalletApi.md#get_transaction) | **get** /v1/wallet/ngn/transaction | Retrieve Transaction Details
*WalletApi* | [**get_wallet**](docs/apis/tags/WalletApi.md#get_wallet) | **get** /v1/wallet/ngn/retrieve | Retrieve Wallet Details
*WalletApi* | [**get_wallets**](docs/apis/tags/WalletApi.md#get_wallets) | **get** /v1/wallet/ngn/accounts | Get Wallets
*WalletApi* | [**transfer_funds**](docs/apis/tags/WalletApi.md#transfer_funds) | **post** /v1/wallet/ngn/transfer | Transfer Funds
*WebHooksApi* | [**delete_webhook**](docs/apis/tags/WebHooksApi.md#delete_webhook) | **delete** /api/v1/webhook/delete | Delete Webhook
*WebHooksApi* | [**get_webhooks**](docs/apis/tags/WebHooksApi.md#get_webhooks) | **get** /api/v1/webhook/fetch | Fetch All Webhooks
*WebHooksApi* | [**notify_webhook**](docs/apis/tags/WebHooksApi.md#notify_webhook) | **post** /api/v1/webhook/notify | Post Hook
*WebHooksApi* | [**subscribe_service**](docs/apis/tags/WebHooksApi.md#subscribe_service) | **post** /api/v1/webhook/subscribe | Subscribe to service

## Documentation For Models

 - [AnalyzeDocumentResponse](docs/models/AnalyzeDocumentResponse.md)
 - [CategorizeTransactionsRequest](docs/models/CategorizeTransactionsRequest.md)
 - [CategorizeTransactionsResponse](docs/models/CategorizeTransactionsResponse.md)
 - [CollectStatusFromPdfRequest](docs/models/CollectStatusFromPdfRequest.md)
 - [CollectStatusFromPdfResponse](docs/models/CollectStatusFromPdfResponse.md)
 - [CollectTransactionsRequest](docs/models/CollectTransactionsRequest.md)
 - [CollectTransactionsResponse](docs/models/CollectTransactionsResponse.md)
 - [CreateWalletRequest](docs/models/CreateWalletRequest.md)
 - [CreateWalletResponse](docs/models/CreateWalletResponse.md)
 - [CreditSubwalletRequest](docs/models/CreditSubwalletRequest.md)
 - [CreditSubwalletResponse](docs/models/CreditSubwalletResponse.md)
 - [DeleteWebhookResponse](docs/models/DeleteWebhookResponse.md)
 - [FinancialGetBasicBvnResponse](docs/models/FinancialGetBasicBvnResponse.md)
 - [FinancialGetFullBvnResponse](docs/models/FinancialGetFullBvnResponse.md)
 - [GeneralGetNubanResponse](docs/models/GeneralGetNubanResponse.md)
 - [GeneralGetWalletBalanceResponse](docs/models/GeneralGetWalletBalanceResponse.md)
 - [GetAccountAnalysisResponse](docs/models/GetAccountAnalysisResponse.md)
 - [GetAccountResponse](docs/models/GetAccountResponse.md)
 - [GetAccountSubscriptionsResponse](docs/models/GetAccountSubscriptionsResponse.md)
 - [GetAccountTransactionsResponse](docs/models/GetAccountTransactionsResponse.md)
 - [GetAdvancedCacResponse](docs/models/GetAdvancedCacResponse.md)
 - [GetBanksResponse](docs/models/GetBanksResponse.md)
 - [GetBasicBvnResponse](docs/models/GetBasicBvnResponse.md)
 - [GetBasicCacResponse](docs/models/GetBasicCacResponse.md)
 - [GetBasicPhoneNumberResponse](docs/models/GetBasicPhoneNumberResponse.md)
 - [GetBinResponse](docs/models/GetBinResponse.md)
 - [GetCacResponse](docs/models/GetCacResponse.md)
 - [GetDataPlansResponse](docs/models/GetDataPlansResponse.md)
 - [GetDocumentAnalysisRequest](docs/models/GetDocumentAnalysisRequest.md)
 - [GetDocumentAnalysisResponse](docs/models/GetDocumentAnalysisResponse.md)
 - [GetDriversLicenseResponse](docs/models/GetDriversLicenseResponse.md)
 - [GetEarningStructureResponse](docs/models/GetEarningStructureResponse.md)
 - [GetEmailReputationResponse](docs/models/GetEmailReputationResponse.md)
 - [GetFullBvnResponse](docs/models/GetFullBvnResponse.md)
 - [GetGenericOcrTextRequest](docs/models/GetGenericOcrTextRequest.md)
 - [GetGenericOcrTextResponse](docs/models/GetGenericOcrTextResponse.md)
 - [GetKycDriversLicenseResponse](docs/models/GetKycDriversLicenseResponse.md)
 - [GetKycPassportResponse](docs/models/GetKycPassportResponse.md)
 - [GetNationalIdResponse](docs/models/GetNationalIdResponse.md)
 - [GetNubanResponse](docs/models/GetNubanResponse.md)
 - [GetOcrTextRequest](docs/models/GetOcrTextRequest.md)
 - [GetOcrTextResponse](docs/models/GetOcrTextResponse.md)
 - [GetPassportResponse](docs/models/GetPassportResponse.md)
 - [GetPhoneNumber404Response](docs/models/GetPhoneNumber404Response.md)
 - [GetPhoneNumberResponse](docs/models/GetPhoneNumberResponse.md)
 - [GetPremiumBvnResponse](docs/models/GetPremiumBvnResponse.md)
 - [GetScreeningInfoResponse](docs/models/GetScreeningInfoResponse.md)
 - [GetSenderIdResponse](docs/models/GetSenderIdResponse.md)
 - [GetSmsStatusResponse](docs/models/GetSmsStatusResponse.md)
 - [GetSpendingPatternResponse](docs/models/GetSpendingPatternResponse.md)
 - [GetSsnitResponse](docs/models/GetSsnitResponse.md)
 - [GetTinResponse](docs/models/GetTinResponse.md)
 - [GetTransactionResponse](docs/models/GetTransactionResponse.md)
 - [GetVinResponse](docs/models/GetVinResponse.md)
 - [GetVninResponse](docs/models/GetVninResponse.md)
 - [GetVoterResponse](docs/models/GetVoterResponse.md)
 - [GetWalletBalanceResponse](docs/models/GetWalletBalanceResponse.md)
 - [GetWalletResponse](docs/models/GetWalletResponse.md)
 - [GetWalletsResponse](docs/models/GetWalletsResponse.md)
 - [GetWebhooksResponse](docs/models/GetWebhooksResponse.md)
 - [NotifyWebhookRequest](docs/models/NotifyWebhookRequest.md)
 - [NotifyWebhookResponse](docs/models/NotifyWebhookResponse.md)
 - [PurchaseAirtimeRequest](docs/models/PurchaseAirtimeRequest.md)
 - [PurchaseAirtimeResponse](docs/models/PurchaseAirtimeResponse.md)
 - [PurchaseDataRequest](docs/models/PurchaseDataRequest.md)
 - [PurchaseDataResponse](docs/models/PurchaseDataResponse.md)
 - [RequestSenderIdRequest](docs/models/RequestSenderIdRequest.md)
 - [RequestSenderIdResponse](docs/models/RequestSenderIdResponse.md)
 - [ScreenAmlRequest](docs/models/ScreenAmlRequest.md)
 - [ScreenAmlResponse](docs/models/ScreenAmlResponse.md)
 - [SendOtpRequest](docs/models/SendOtpRequest.md)
 - [SendOtpResponse](docs/models/SendOtpResponse.md)
 - [SendSmsRequest](docs/models/SendSmsRequest.md)
 - [SendSmsResponse](docs/models/SendSmsResponse.md)
 - [SubscribeServiceRequest](docs/models/SubscribeServiceRequest.md)
 - [SubscribeServiceResponse](docs/models/SubscribeServiceResponse.md)
 - [TransferFundsRequest](docs/models/TransferFundsRequest.md)
 - [TransferFundsResponse](docs/models/TransferFundsResponse.md)
 - [ValidateBvnResponse](docs/models/ValidateBvnResponse.md)
 - [ValidateOtpResponse](docs/models/ValidateOtpResponse.md)
 - [VerifyAgeResponse](docs/models/VerifyAgeResponse.md)
 - [VerifyPhotoIdWithSelfieRequest](docs/models/VerifyPhotoIdWithSelfieRequest.md)
 - [VerifyPhotoIdWithSelfieResponse](docs/models/VerifyPhotoIdWithSelfieResponse.md)
 - [VerifySelfieBvnRequest](docs/models/VerifySelfieBvnRequest.md)
 - [VerifySelfieBvnResponse](docs/models/VerifySelfieBvnResponse.md)
 - [VerifySelfieNinRequest](docs/models/VerifySelfieNinRequest.md)
 - [VerifySelfieNinResponse](docs/models/VerifySelfieNinResponse.md)


## Author
This Python package is automatically generated by [Konfig](https://konfigthis.com)
