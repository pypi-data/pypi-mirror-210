#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_image
   Description:
   Author:          dingyong.cui
   date：           2023/5/11
-------------------------------------------------
   Change Activity:
                    2023/5/11
-------------------------------------------------
"""


class TestImage:

    def setup(self):
        from visual_compare.doc.image.image import MatchImg
        self.cls = MatchImg
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_parse_mask(self):
        img1 = self.get_path('123.png')
        img11 = self.get_path('000.png')
        img2 = self.get_path('124.png')
        res = self.cls().parse_mask(img1, img11)
        print(res)

    def test_parse_mask_old(self):
        img1 = self.get_path('123.png')
        img11 = self.get_path('000.png')
        img2 = self.get_path('124.png')
        res = self.cls().parse_mask(img1, img11)
        print(res)

    def test_parse_mask1(self):
        from visual_compare.doc.image.compare_image import CompareImage
        img = self.get_path('111.pdf')
        img1 = CompareImage(img).opencv_images
        img11 = self.get_path('333.png')
        res = self.cls().parse_mask(img1, img11)
        print(res)

    def test_ocr_image_equal(self):
        from visual_compare.doc.image.image import OcrImage
        from visual_compare.doc.models import Contour
        ct1 = Contour(text='w ア イ ア ル\n', x=1317, y=932, width=30, height=18)
        ct2 = Contour(text='w アイ アル\n', x=1318, y=933, width=30, height=18)
        oi = OcrImage(**ct1.dict())
        assert oi.equal(ct2) is True

    def test_ocr_image_not_equal(self):
        from visual_compare.doc.image.image import OcrImage
        from visual_compare.doc.models import Contour
        ct1 = Contour(text='w ア イ ア ル\n', x=1317, y=932, width=30, height=18)
        ct2 = Contour(text='w アイ アル\n', x=1318, y=933, width=30, height=18)
        oi = OcrImage(**ct1.dict())
        assert oi.equal(ct2, coordinate_eq=True) is False
