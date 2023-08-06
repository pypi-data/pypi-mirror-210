from thaiqr import MerchantPromptpayQRGenerate
from promptpay_type import PromptpayType
from transaction_uasge_type import TransactionUsageType
import unittest

class TestMerchantPromptpayQRGenerate(unittest.TestCase):
    def test_mobile_number(self):
        promptpay_type = PromptpayType.MOBILE_NUMBER
        receive = "0987654321"
        amount = "1000.00"
        transaction_usage = TransactionUsageType.ONETIME
        
        expectedResult = ""
        
        result = MerchantPromptpayQRGenerate(promptpayType=promptpay_type, receiveId=receive, amount=amount, transactionUsage=transaction_usage)

        self.assertEqual(result, expectedResult)
        
if __name__ == '__main__':
    unittest.main()
    