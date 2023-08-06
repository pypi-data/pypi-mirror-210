import typing_extensions

from dojah_client.paths import PathValues
from dojah_client.apis.paths.api_v1_gh_kyc_dl import ApiV1GhKycDl
from dojah_client.apis.paths.api_v1_gh_kyc_passport import ApiV1GhKycPassport
from dojah_client.apis.paths.api_v1_gh_kyc_ssnit import ApiV1GhKycSsnit
from dojah_client.apis.paths.api_v1_ug_kyc_voter import ApiV1UgKycVoter
from dojah_client.apis.paths.api_v1_ke_kyc_id import ApiV1KeKycId
from dojah_client.apis.paths.api_v1_kyc_dl import ApiV1KycDl
from dojah_client.apis.paths.api_v1_kyc_nuban import ApiV1KycNuban
from dojah_client.apis.paths.api_v1_kyc_bvn import ApiV1KycBvn
from dojah_client.apis.paths.api_v1_kyc_bvn_basic import ApiV1KycBvnBasic
from dojah_client.apis.paths.api_v1_kyc_bvn_full import ApiV1KycBvnFull
from dojah_client.apis.paths.api_v1_kyc_bvn_advance import ApiV1KycBvnAdvance
from dojah_client.apis.paths.api_v1_kyc_vnin import ApiV1KycVnin
from dojah_client.apis.paths.v1_kyc_phone_number_basic import V1KycPhoneNumberBasic
from dojah_client.apis.paths.api_v1_kyc_phone_number import ApiV1KycPhoneNumber
from dojah_client.apis.paths.v1_kyc_age_verification import V1KycAgeVerification
from dojah_client.apis.paths.v1_kyc_bvn_verify import V1KycBvnVerify
from dojah_client.apis.paths.v1_kyc_nin_verify import V1KycNinVerify
from dojah_client.apis.paths.api_v1_kyc_vin import ApiV1KycVin
from dojah_client.apis.paths.v1_kyc_email import V1KycEmail
from dojah_client.apis.paths.api_v1_kyc_passport import ApiV1KycPassport
from dojah_client.apis.paths.api_v1_document_analysis import ApiV1DocumentAnalysis
from dojah_client.apis.paths.v1_kyc_cac import V1KycCac
from dojah_client.apis.paths.v1_kyc_cac_basic import V1KycCacBasic
from dojah_client.apis.paths.v1_kyc_cac_advance import V1KycCacAdvance
from dojah_client.apis.paths.v1_kyc_tin import V1KycTin
from dojah_client.apis.paths.api_v1_messaging_sms import ApiV1MessagingSms
from dojah_client.apis.paths.v1_messaging_sms_get_status import V1MessagingSmsGetStatus
from dojah_client.apis.paths.v1_messaging_otp import V1MessagingOtp
from dojah_client.apis.paths.v1_messaging_otp_validate import V1MessagingOtpValidate
from dojah_client.apis.paths.api_v1_messaging_sender_ids import ApiV1MessagingSenderIds
from dojah_client.apis.paths.api_v1_messaging_sender_id import ApiV1MessagingSenderId
from dojah_client.apis.paths.v1_wallet_ngn_create import V1WalletNgnCreate
from dojah_client.apis.paths.v1_wallet_ngn_retrieve import V1WalletNgnRetrieve
from dojah_client.apis.paths.v1_wallet_ngn_accounts import V1WalletNgnAccounts
from dojah_client.apis.paths.v1_wallet_ngn_transaction import V1WalletNgnTransaction
from dojah_client.apis.paths.v1_wallet_ngn_transfer import V1WalletNgnTransfer
from dojah_client.apis.paths.v1_wallet_ngn_credit import V1WalletNgnCredit
from dojah_client.apis.paths.api_v1_financial_account_transactions import ApiV1FinancialAccountTransactions
from dojah_client.apis.paths.v1_financial_account_subscription import V1FinancialAccountSubscription
from dojah_client.apis.paths.v1_financial_bvn_information_basic import V1FinancialBvnInformationBasic
from dojah_client.apis.paths.v1_financial_bvn_information_full import V1FinancialBvnInformationFull
from dojah_client.apis.paths.v1_financial_spending_pattern import V1FinancialSpendingPattern
from dojah_client.apis.paths.v1_financial_earning_structure import V1FinancialEarningStructure
from dojah_client.apis.paths.v1_financial_transactions import V1FinancialTransactions
from dojah_client.apis.paths.api_v1_financial_transactions_pdf import ApiV1FinancialTransactionsPdf
from dojah_client.apis.paths.api_v1_financial_analysis import ApiV1FinancialAnalysis
from dojah_client.apis.paths.v1_kyc_photoid_verify import V1KycPhotoidVerify
from dojah_client.apis.paths.v1_ml_ocr import V1MlOcr
from dojah_client.apis.paths.v1_ml_ocr_generic import V1MlOcrGeneric
from dojah_client.apis.paths.v1_document_analysis_dl import V1DocumentAnalysisDl
from dojah_client.apis.paths.api_v1_aml_screening import ApiV1AmlScreening
from dojah_client.apis.paths.v1_aml_screening_info import V1AmlScreeningInfo
from dojah_client.apis.paths.api_v1_balance import ApiV1Balance
from dojah_client.apis.paths.v1_purchase_airtime import V1PurchaseAirtime
from dojah_client.apis.paths.v1_purchase_data import V1PurchaseData
from dojah_client.apis.paths.v1_purchase_data_plans import V1PurchaseDataPlans
from dojah_client.apis.paths.v1_general_banks import V1GeneralBanks
from dojah_client.apis.paths.v1_general_account import V1GeneralAccount
from dojah_client.apis.paths.v1_general_bin import V1GeneralBin
from dojah_client.apis.paths.v1_ml_categorize_transaction import V1MlCategorizeTransaction
from dojah_client.apis.paths.api_v1_webhook_subscribe import ApiV1WebhookSubscribe
from dojah_client.apis.paths.api_v1_webhook_delete import ApiV1WebhookDelete
from dojah_client.apis.paths.api_v1_webhook_fetch import ApiV1WebhookFetch
from dojah_client.apis.paths.api_v1_webhook_notify import ApiV1WebhookNotify
from dojah_client.apis.paths.api_v1_financial_account_information import ApiV1FinancialAccountInformation

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.API_V1_GH_KYC_DL: ApiV1GhKycDl,
        PathValues.API_V1_GH_KYC_PASSPORT: ApiV1GhKycPassport,
        PathValues.API_V1_GH_KYC_SSNIT: ApiV1GhKycSsnit,
        PathValues.API_V1_UG_KYC_VOTER: ApiV1UgKycVoter,
        PathValues.API_V1_KE_KYC_ID: ApiV1KeKycId,
        PathValues.API_V1_KYC_DL: ApiV1KycDl,
        PathValues.API_V1_KYC_NUBAN: ApiV1KycNuban,
        PathValues.API_V1_KYC_BVN: ApiV1KycBvn,
        PathValues.API_V1_KYC_BVN_BASIC: ApiV1KycBvnBasic,
        PathValues.API_V1_KYC_BVN_FULL: ApiV1KycBvnFull,
        PathValues.API_V1_KYC_BVN_ADVANCE: ApiV1KycBvnAdvance,
        PathValues.API_V1_KYC_VNIN: ApiV1KycVnin,
        PathValues.V1_KYC_PHONE_NUMBER_BASIC: V1KycPhoneNumberBasic,
        PathValues.API_V1_KYC_PHONE_NUMBER: ApiV1KycPhoneNumber,
        PathValues.V1_KYC_AGE_VERIFICATION: V1KycAgeVerification,
        PathValues.V1_KYC_BVN_VERIFY: V1KycBvnVerify,
        PathValues.V1_KYC_NIN_VERIFY: V1KycNinVerify,
        PathValues.API_V1_KYC_VIN: ApiV1KycVin,
        PathValues.V1_KYC_EMAIL: V1KycEmail,
        PathValues.API_V1_KYC_PASSPORT: ApiV1KycPassport,
        PathValues.API_V1_DOCUMENT_ANALYSIS: ApiV1DocumentAnalysis,
        PathValues.V1_KYC_CAC: V1KycCac,
        PathValues.V1_KYC_CAC_BASIC: V1KycCacBasic,
        PathValues.V1_KYC_CAC_ADVANCE: V1KycCacAdvance,
        PathValues.V1_KYC_TIN: V1KycTin,
        PathValues.API_V1_MESSAGING_SMS: ApiV1MessagingSms,
        PathValues.V1_MESSAGING_SMS_GET_STATUS: V1MessagingSmsGetStatus,
        PathValues.V1_MESSAGING_OTP: V1MessagingOtp,
        PathValues.V1_MESSAGING_OTP_VALIDATE: V1MessagingOtpValidate,
        PathValues.API_V1_MESSAGING_SENDER_IDS: ApiV1MessagingSenderIds,
        PathValues.API_V1_MESSAGING_SENDER_ID: ApiV1MessagingSenderId,
        PathValues.V1_WALLET_NGN_CREATE: V1WalletNgnCreate,
        PathValues.V1_WALLET_NGN_RETRIEVE: V1WalletNgnRetrieve,
        PathValues.V1_WALLET_NGN_ACCOUNTS: V1WalletNgnAccounts,
        PathValues.V1_WALLET_NGN_TRANSACTION: V1WalletNgnTransaction,
        PathValues.V1_WALLET_NGN_TRANSFER: V1WalletNgnTransfer,
        PathValues.V1_WALLET_NGN_CREDIT: V1WalletNgnCredit,
        PathValues.API_V1_FINANCIAL_ACCOUNT_TRANSACTIONS: ApiV1FinancialAccountTransactions,
        PathValues.V1_FINANCIAL_ACCOUNT_SUBSCRIPTION: V1FinancialAccountSubscription,
        PathValues.V1_FINANCIAL_BVN_INFORMATION_BASIC: V1FinancialBvnInformationBasic,
        PathValues.V1_FINANCIAL_BVN_INFORMATION_FULL: V1FinancialBvnInformationFull,
        PathValues.V1_FINANCIAL_SPENDING_PATTERN: V1FinancialSpendingPattern,
        PathValues.V1_FINANCIAL_EARNING_STRUCTURE: V1FinancialEarningStructure,
        PathValues.V1_FINANCIAL_TRANSACTIONS: V1FinancialTransactions,
        PathValues.API_V1_FINANCIAL_TRANSACTIONS_PDF: ApiV1FinancialTransactionsPdf,
        PathValues.API_V1_FINANCIAL_ANALYSIS: ApiV1FinancialAnalysis,
        PathValues.V1_KYC_PHOTOID_VERIFY: V1KycPhotoidVerify,
        PathValues.V1_ML_OCR: V1MlOcr,
        PathValues.V1_ML_OCR_GENERIC: V1MlOcrGeneric,
        PathValues.V1_DOCUMENT_ANALYSIS_DL: V1DocumentAnalysisDl,
        PathValues.API_V1_AML_SCREENING: ApiV1AmlScreening,
        PathValues.V1_AML_SCREENING_INFO: V1AmlScreeningInfo,
        PathValues.API_V1_BALANCE: ApiV1Balance,
        PathValues.V1_PURCHASE_AIRTIME: V1PurchaseAirtime,
        PathValues.V1_PURCHASE_DATA: V1PurchaseData,
        PathValues.V1_PURCHASE_DATA_PLANS: V1PurchaseDataPlans,
        PathValues.V1_GENERAL_BANKS: V1GeneralBanks,
        PathValues.V1_GENERAL_ACCOUNT: V1GeneralAccount,
        PathValues.V1_GENERAL_BIN: V1GeneralBin,
        PathValues.V1_ML_CATEGORIZE_TRANSACTION: V1MlCategorizeTransaction,
        PathValues.API_V1_WEBHOOK_SUBSCRIBE: ApiV1WebhookSubscribe,
        PathValues.API_V1_WEBHOOK_DELETE: ApiV1WebhookDelete,
        PathValues.API_V1_WEBHOOK_FETCH: ApiV1WebhookFetch,
        PathValues.API_V1_WEBHOOK_NOTIFY: ApiV1WebhookNotify,
        PathValues.API_V1_FINANCIAL_ACCOUNT_INFORMATION: ApiV1FinancialAccountInformation,
    }
)

path_to_api = PathToApi(
    {
        PathValues.API_V1_GH_KYC_DL: ApiV1GhKycDl,
        PathValues.API_V1_GH_KYC_PASSPORT: ApiV1GhKycPassport,
        PathValues.API_V1_GH_KYC_SSNIT: ApiV1GhKycSsnit,
        PathValues.API_V1_UG_KYC_VOTER: ApiV1UgKycVoter,
        PathValues.API_V1_KE_KYC_ID: ApiV1KeKycId,
        PathValues.API_V1_KYC_DL: ApiV1KycDl,
        PathValues.API_V1_KYC_NUBAN: ApiV1KycNuban,
        PathValues.API_V1_KYC_BVN: ApiV1KycBvn,
        PathValues.API_V1_KYC_BVN_BASIC: ApiV1KycBvnBasic,
        PathValues.API_V1_KYC_BVN_FULL: ApiV1KycBvnFull,
        PathValues.API_V1_KYC_BVN_ADVANCE: ApiV1KycBvnAdvance,
        PathValues.API_V1_KYC_VNIN: ApiV1KycVnin,
        PathValues.V1_KYC_PHONE_NUMBER_BASIC: V1KycPhoneNumberBasic,
        PathValues.API_V1_KYC_PHONE_NUMBER: ApiV1KycPhoneNumber,
        PathValues.V1_KYC_AGE_VERIFICATION: V1KycAgeVerification,
        PathValues.V1_KYC_BVN_VERIFY: V1KycBvnVerify,
        PathValues.V1_KYC_NIN_VERIFY: V1KycNinVerify,
        PathValues.API_V1_KYC_VIN: ApiV1KycVin,
        PathValues.V1_KYC_EMAIL: V1KycEmail,
        PathValues.API_V1_KYC_PASSPORT: ApiV1KycPassport,
        PathValues.API_V1_DOCUMENT_ANALYSIS: ApiV1DocumentAnalysis,
        PathValues.V1_KYC_CAC: V1KycCac,
        PathValues.V1_KYC_CAC_BASIC: V1KycCacBasic,
        PathValues.V1_KYC_CAC_ADVANCE: V1KycCacAdvance,
        PathValues.V1_KYC_TIN: V1KycTin,
        PathValues.API_V1_MESSAGING_SMS: ApiV1MessagingSms,
        PathValues.V1_MESSAGING_SMS_GET_STATUS: V1MessagingSmsGetStatus,
        PathValues.V1_MESSAGING_OTP: V1MessagingOtp,
        PathValues.V1_MESSAGING_OTP_VALIDATE: V1MessagingOtpValidate,
        PathValues.API_V1_MESSAGING_SENDER_IDS: ApiV1MessagingSenderIds,
        PathValues.API_V1_MESSAGING_SENDER_ID: ApiV1MessagingSenderId,
        PathValues.V1_WALLET_NGN_CREATE: V1WalletNgnCreate,
        PathValues.V1_WALLET_NGN_RETRIEVE: V1WalletNgnRetrieve,
        PathValues.V1_WALLET_NGN_ACCOUNTS: V1WalletNgnAccounts,
        PathValues.V1_WALLET_NGN_TRANSACTION: V1WalletNgnTransaction,
        PathValues.V1_WALLET_NGN_TRANSFER: V1WalletNgnTransfer,
        PathValues.V1_WALLET_NGN_CREDIT: V1WalletNgnCredit,
        PathValues.API_V1_FINANCIAL_ACCOUNT_TRANSACTIONS: ApiV1FinancialAccountTransactions,
        PathValues.V1_FINANCIAL_ACCOUNT_SUBSCRIPTION: V1FinancialAccountSubscription,
        PathValues.V1_FINANCIAL_BVN_INFORMATION_BASIC: V1FinancialBvnInformationBasic,
        PathValues.V1_FINANCIAL_BVN_INFORMATION_FULL: V1FinancialBvnInformationFull,
        PathValues.V1_FINANCIAL_SPENDING_PATTERN: V1FinancialSpendingPattern,
        PathValues.V1_FINANCIAL_EARNING_STRUCTURE: V1FinancialEarningStructure,
        PathValues.V1_FINANCIAL_TRANSACTIONS: V1FinancialTransactions,
        PathValues.API_V1_FINANCIAL_TRANSACTIONS_PDF: ApiV1FinancialTransactionsPdf,
        PathValues.API_V1_FINANCIAL_ANALYSIS: ApiV1FinancialAnalysis,
        PathValues.V1_KYC_PHOTOID_VERIFY: V1KycPhotoidVerify,
        PathValues.V1_ML_OCR: V1MlOcr,
        PathValues.V1_ML_OCR_GENERIC: V1MlOcrGeneric,
        PathValues.V1_DOCUMENT_ANALYSIS_DL: V1DocumentAnalysisDl,
        PathValues.API_V1_AML_SCREENING: ApiV1AmlScreening,
        PathValues.V1_AML_SCREENING_INFO: V1AmlScreeningInfo,
        PathValues.API_V1_BALANCE: ApiV1Balance,
        PathValues.V1_PURCHASE_AIRTIME: V1PurchaseAirtime,
        PathValues.V1_PURCHASE_DATA: V1PurchaseData,
        PathValues.V1_PURCHASE_DATA_PLANS: V1PurchaseDataPlans,
        PathValues.V1_GENERAL_BANKS: V1GeneralBanks,
        PathValues.V1_GENERAL_ACCOUNT: V1GeneralAccount,
        PathValues.V1_GENERAL_BIN: V1GeneralBin,
        PathValues.V1_ML_CATEGORIZE_TRANSACTION: V1MlCategorizeTransaction,
        PathValues.API_V1_WEBHOOK_SUBSCRIBE: ApiV1WebhookSubscribe,
        PathValues.API_V1_WEBHOOK_DELETE: ApiV1WebhookDelete,
        PathValues.API_V1_WEBHOOK_FETCH: ApiV1WebhookFetch,
        PathValues.API_V1_WEBHOOK_NOTIFY: ApiV1WebhookNotify,
        PathValues.API_V1_FINANCIAL_ACCOUNT_INFORMATION: ApiV1FinancialAccountInformation,
    }
)
