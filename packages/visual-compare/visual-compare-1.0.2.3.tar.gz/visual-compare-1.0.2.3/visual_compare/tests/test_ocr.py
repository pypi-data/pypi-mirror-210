#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_ocr
   Description:
   Author:          dingyong.cui
   date：           2023/5/12
-------------------------------------------------
   Change Activity:
                    2023/5/12
-------------------------------------------------
"""
import cv2
import numpy
from pytesseract import pytesseract

from visual_compare.doc.image.compare_image import CompareImage
from visual_compare.doc.image.ocr import EastTextExtractor


class TestOcr:

    def setup(self):
        # from visual_compare.doc.visual_test import VisualTest
        # self.cls = VisualTest
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_xxx(self):
        img = self.get_path('1.jpg')
        # ci = cv2.imread(img)
        # gray_image = cv2.cvtColor(ci, cv2.COLOR_BGR2GRAY)
        # threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        #
        ocr_config = '--psm 11' + f' -l eng+jpn'
        # pytesseract.get_languages()
        d = pytesseract.image_to_data(CompareImage(img).opencv_images[0], output_type='dict', config=ocr_config)
        n_boxes = len(d['text'])
        text_list = []
        left_list = []
        top_list = []
        width_list = []
        height_list = []
        conf_list = []
        text_content = []
        # For each detected part
        for j in range(n_boxes):

            # If the prediction accuracy greater than %50
            if int(float(d['conf'][j])) > 20:
                text_list.append(d['text'][j])
                left_list.append(d['left'][j])
                top_list.append(d['top'][j])
                width_list.append(d['width'][j])
                height_list.append(d['height'][j])
                conf_list.append(d['conf'][j])
        text_content.append(
            {'text': text_list, 'left': left_list, 'top': top_list, 'width': width_list, 'height': height_list,
             'conf': conf_list})
        print(text_content)

    def test_torch(self):
        import torch
        pth_file = r'C:\Users\dingyong.cui\.EasyOCR\model\japanese_g2.pth'
        net = torch.load(pth_file, map_location=torch.device('cpu'))
        for k, v in dict(net).items():
            print(k)
            print(v)

    def test_x(self):
        import easyocr
        # img1 = self.get_path('1.jpg')
        img1 = self.get_path('y11.png')
        img2 = self.get_path('y11.png')
        img_np = cv2.imread(img1)
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        # 阈值二进制 - > 127 设置为255(白)，否则0(黑) -> 淡白得更白,淡黑更黑
        _, img_thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # img = cv2.rectangle(img_np, (20, 8), (96, 36), (0, 0, 255), 4)
        # cv2.imshow('test', img)
        # cv2.waitKey(0)

        # 图像 OCR 识别 paragraph-是否返回匹配度
        # reader = easyocr.Reader(['en', 'ja'], detector=True, recognizer=True)
        reader = easyocr.Reader(['en', 'ja'], detector=True, recognizer=True)
        text1 = reader.readtext(img_thresh, detail=1, batch_size=1, paragraph=False, contrast_ths=0.5,
                                adjust_contrast=0.8)

        img_np2 = cv2.imread(img2)
        img_gray2 = cv2.cvtColor(img_np2, cv2.COLOR_BGR2GRAY)
        # 阈值二进制 - > 127 设置为255(白)，否则0(黑) -> 淡白得更白,淡黑更黑
        _, img_thresh2 = cv2.threshold(img_gray2, 170, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        text2 = reader.readtext(img_thresh2, detail=1, batch_size=1, paragraph=True)
        print(text1)
        print(text2)

    def test_1(self):
        img1 = self.get_path('y11.png')
        oi = CompareImage(img1).opencv_images[0]
        x = EastTextExtractor().get_image_text_and_coordinate(oi)
        print(x)

    def test_0(self):
        cnt = numpy.array([[53, 89], [281, 89], [281, 109], [53, 109]])
        cv2.boundingRect(cnt)
