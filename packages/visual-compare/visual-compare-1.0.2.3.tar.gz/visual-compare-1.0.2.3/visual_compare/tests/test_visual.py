#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_visual
   Description:
   Author:          dingyong.cui
   date：           2023/5/12
-------------------------------------------------
   Change Activity:
                    2023/5/12
-------------------------------------------------
"""


class TestVisual:

    def setup(self):
        from visual_compare.doc.visual import Visual
        self.cls = Visual
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_generate_mask(self):
        reference_image = self.get_path('123.png')
        mask_images = self.get_path('000.png')
        res = self.cls().generate_mask(reference_image, mask_images)
        print(res)

    def test_generate_mask_pages(self):
        reference_image = self.get_path('111.pdf')
        mask_images = self.get_path('333.png')
        res = self.cls().generate_mask(reference_image, mask_images)
        print(res)

    def test_compare_images(self):
        img1 = self.get_path('123.png')
        img2 = self.get_path('124.png')
        cls = self.cls()
        is_diff, res = cls.compare_images(img1, img2)
        print(res)
        assert is_diff is True

    def test_compare_images_with_mask(self):
        img1 = self.get_path('123.png')
        mask_images = self.get_path('000.png')
        img2 = self.get_path('124.png')
        cls = self.cls()
        mask = cls.generate_mask(img1, mask_images)
        is_diff, res = cls.compare_images(img1, img2, mask=mask)
        print(res)
        assert is_diff is True

    def test_compare_images_with_mask1(self):
        img1 = self.get_path('008.jpg')
        mask_images = self.get_path('007.png')
        img2 = self.get_path('009.jpg')
        cls = self.cls()
        mask = cls.generate_mask(img1, mask_images)
        is_diff, res = cls.compare_images(img1, img2, mask=mask)
        print(res)
        assert is_diff is True

    def test_compare_images_with_force_ocr(self):
        img1 = self.get_path('y1.png')
        img2 = self.get_path('y2.png')
        cls = self.cls()
        is_diff, res = cls.compare_images(img1, img2, force_ocr=True, lang=['ja', 'en'])
        print(res)
        assert is_diff is True

    def test_compare_images_with_force_ocr_and_ch(self):
        img1 = self.get_path('c10b.png')
        img2 = self.get_path('c10a.png')
        cls = self.cls()
        is_diff, res = cls.compare_images(img1, img2, force_ocr=True, lang=['ch_sim', 'en'])
        print(res)
        assert is_diff is True

    def test_compare_images_with_force_ocr_and_default_lang(self):
        img1 = self.get_path('c10a.png')
        img2 = self.get_path('c10b.png')
        cls = self.cls()
        is_diff, res = cls.compare_images(img1, img2, force_ocr=True)
        print(res)
        assert is_diff is True
