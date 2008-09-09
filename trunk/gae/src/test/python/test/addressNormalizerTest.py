# -*- coding: utf-8 -*-

from address.services import AddressNormalizer
from test import BaseTestCase

class AddressNormalizerTest(BaseTestCase):
    def testNormalize(self):
        self.assertEquals([u'\u6d59\u6c5f\u7701\u676d\u5dde\u5e02\u897f\u6e56\u533a\u6559\u5de5\u8def', 
                          u'\u6d59\u6c5f\u7701\u676d\u5dde\u5e02\u62f1\u5885\u533a\u6559\u5de5\u8def', 
                          u'\u6d59\u6c5f\u7701\u676d\u5dde\u5e02\u6c5f\u5e72\u533a\u6559\u5de5\u8def', 
                          u'\u6d59\u6c5f\u7701\u676d\u5dde\u5e02\u4e0b\u57ce\u533a\u6559\u5de5\u8def'], 
                          AddressNormalizer.normalize("教工路"))
        self.assertEquals([u'\u65b0\u7586\u7ef4\u543e\u5c14\u81ea\u6cbb\u533a\u4e4c\u9c81\u6728\u9f50\u5e02\u7c73\u4e1c\u533a'],
                          AddressNormalizer.normalize("米东区"))
    
    def testPrint(self):   
        print AddressNormalizer.normalize("清华大学")
        