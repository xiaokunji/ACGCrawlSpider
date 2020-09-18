import re

import scrapy
from ACG.items import AcgItem
from scrapy import Selector
from scrapy.spiders import CrawlSpider

import os

from scrapy.utils.project import get_project_settings


class Cartoon(CrawlSpider):
    name = 'acg'  # 运行时这个爬虫的名字
    # https://18h.animezilla.com/
    urlTemplate = 'https://18h.animezilla.com/manga/{id}'
    # urlTemplate = 'https://18h.animezilla.com/doujinshi/original'
    qualify_reta = '4.25'
    start_urls = [
        'HIQ',
        # '590',
        # '3894',

    ]

    exist_id = []

    # rules = (
    #     # 当前页
    #     Rule(LinkExtractor(restrict_xpaths='//div[@id="page-current"]//img[@id="comic"]'), callback='parse_detial'),
    #     # 下一页
    #     # Rule(LinkExtractor(restrict_xpaths='//a[@class="nextpostslink"]'))
    # )

    def start_requests(self):

        # TODO 初始化已爬取的
        img_store = get_project_settings().get('IMAGES_STORE')

        for folder in os.listdir(img_store):
            self.exist_id.append(folder.split("-")[0])

        print("已爬取的漫画id:", self.exist_id)

        if 'HIQ' in self.start_urls:
            # 爬取高质量漫画
            # 先翻页程序里找合格的,再翻页,找到合格的后再爬具体页面
            print("爬取高质量漫画开始...")
            yield scrapy.Request(self.urlTemplate.format(id=''), callback=self.parse_page)
        else:
            for acg_id in self.start_urls:
                print("准备爬取id:", acg_id)
                url = self.urlTemplate.format(id=acg_id)
                yield scrapy.Request(url, callback=self.parse_title, meta={"id": acg_id})

    def parse_page(self, response):
        print("正在爬取页面: ", response.url)
        selector = Selector(response)
        # 合格条件
        curr_page_acg = response.xpath("//div[contains(@class,'pure-u-1-2')]")
        for acg in curr_page_acg:
            reta_score = \
            acg.xpath(".//div[@id='ratings_results']/small/em/strong[1]/text()").extract_first().split("/")[0]
            if reta_score > self.qualify_reta:
                url = acg.xpath('.//div[@class="entry-content"]/div/div[@class="pure-u-2-5"]/a/@href').extract_first()

                print("找到一篇符合条件的漫画: ", url)
                acg_id = url.split("/")[-1]
                yield scrapy.Request(url, callback=self.parse_title, meta={"id": acg_id})

        # 翻页
        next_page_url = response.xpath("//a[@class='nextpostslink']/@href").get()
        # print("下一页:", next_page_url)
        if next_page_url:
            yield scrapy.Request(next_page_url, callback=self.parse_page)
        else:
            print("页面爬取数: ", response.url.split("/")[1])

    def parse_title(self, response):
        if response.meta['id'] in self.exist_id:
            print("id:", response.meta['id'], " 已爬取,跳过该漫画")
            return

        selector = Selector(response)

        title = selector.xpath('//h1[@class="entry-title"]/text()').extract_first()
        if str(title).count("/") > 1:
            acg_name = str(title).split("/", 1)[1].split("[")[0].strip()
        else:
            acg_name = re.sub(u"\\[.*?\\]", "", str(title)).split("-")[0].strip()
        total_page = re.findall(re.compile(r'(?<=\[)\d+(?=P\])'), str(title))[0]
        print("acg名称:", acg_name, "总页数:", total_page)
        meta = {
            'acgName': acg_name,
            'totalPage': total_page,
            'id': response.meta['id']
        }
        yield scrapy.Request(response.url + "/1", callback=self.parse, meta=meta)

    def parse(self, response):
        selector = Selector(response)
        pic_url = selector.xpath('//img[@id="comic"]/@src').extract_first()
        item = AcgItem()
        item['pic'] = pic_url
        item['picName'] = response.url.split('/')[-1]
        item['acgName'] = response.meta['acgName']
        item['totalPage'] = response.meta['totalPage']
        item['id'] = response.meta['id']
        yield item

        next_page_url = response.xpath("//a[@class='nextpostslink']/@href").get()

        print("下一页:", next_page_url)
        if next_page_url:
            yield scrapy.Request(next_page_url, callback=self.parse, meta=item)
        else:
            print("页面爬取数: ", item['picName'], "完成,共计页面:", item['totalPage'])
