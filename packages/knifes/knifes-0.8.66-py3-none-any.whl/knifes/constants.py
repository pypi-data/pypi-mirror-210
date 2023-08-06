from enum import Enum


class AreaEnum(Enum):
    DOMESTIC = 1
    OVERSEAS = 2

    def __str__(self):
        return self.name.lower()


APPLE_VERIFY_RECEIPT_PROD = 'https://buy.itunes.apple.com/verifyReceipt'
APPLE_VERIFY_RECEIPT_SANDBOX = 'https://sandbox.itunes.apple.com/verifyReceipt'
ALIPAY_SERVER_URL = 'https://openapi.alipay.com/gateway.do'
