import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CblItem
from itemloaders.processors import TakeFirst
import datetime
pattern = r'(\xa0)?'

class CblSpider(scrapy.Spider):
	name = 'cbl'
	now = datetime.datetime.now()
	year = now.year
	start_urls = [f'https://www.cblgroup.com/et/media/press-releases/{year}/']


	def parse(self, response):
		post_links = response.xpath('//p[@class="title"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://www.cblgroup.com/et/media/press-releases/{self.year}/'
		if self.year >= 2012:
			self.year -= 1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//p[@class="publish-date"]/time/@datetime').get()
		date = re.findall(r'\d+\-\d+\-\d+',date)
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="richtext"]//text()').getall()

		if any('Kasutame oma veebilehel' in text for text in content):
			content = content[5::]
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CblItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
