# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import shutil

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings


class AcgPipeline(object):

    def process_item(self, item, spider):
        return item


class ImagesPipeline(ImagesPipeline):

    # 从项目设置文件中导入图片下载路径
    img_store = get_project_settings().get('IMAGES_STORE')

    def get_media_requests(self, item, info):
        yield Request(item["pic"], meta={"item": item})

    def file_path(self, request, response=None, info=None):
        return request.meta["item"]['picName'] + "-" + request.meta["item"]['id'] + ".jpg"

    # 自定义存储文件夹 from https://www.jianshu.com/p/0ea820236e16
    def item_completed(self, results, item, info):
        image_path = [x["path"] for ok, x in results if ok]  # 图片名称及后缀
        # 定义分类保存的路径
        # 目录不存在则创建目录
        img_path = item['acgName']
        img_store_path = self.img_store + item['id'] + "-" + img_path
        if not os.path.exists(img_store_path):
            os.mkdir(img_store_path)

        # 将文件从默认下路路径移动到指定路径下
        shutil.move(self.img_store + image_path[0], img_store_path + "/" + item["picName"] + '.jpg')

        # item["img_path"] = img_path + "\\" + item["picName"] + '.jpg'
        return item
