# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


# class JobspiderPipeline:
#     def process_item(self, item, spider):
#         return item
import psycopg2
from scrapy.exceptions import DropItem
from core.models import Job  # Your Django model
from asgiref.sync import sync_to_async

class SaveToDatabasePipeline:
    @sync_to_async
    def save_job(self, item):
        job = Job(
            title=item['title'],
            location=item['location'],
            company=item['company'],
            category=item['category'],
            apply_link=item['apply_link'],
            type=item['type'],
            posted_date=item['posted_date'],
            description=item.get('description', ''), # Optional
            more_description=item.get('more_description', ''),  # Optional
            salary=item.get('salary', None),  # Optional
            benefits=item.get('benefits', []),  # Optional
            requirements=item.get('requirements', []),  # Optional
            responsibilities=item.get('responsibilities', []),  # Optional
            skills=item.get('skills', []),  # Optional
        )
        job.save()  # Save the job into the database

    async def process_item(self, item, spider):
        await self.save_job(item)  # Save the job asynchronously
        return item

