import json
import scrapy
import os
from datetime import datetime
from ..items import JobItem  # Use relative import
from ollama import chat
from pydantic import BaseModel

class JobDetails(BaseModel):
    salary: str
    skills: list[str]
    industry: str

class NetflixSpider(scrapy.Spider):
    name = "netflix"
    start_url = "https://explore.jobs.netflix.net/api/apply/v2/jobs?domain=netflix.com&start={}&num=10&exclude_pid=790299260100&pid=790299260100&Teams=Engineering%20Operations&Teams=Games&Teams=Product&Teams=Program%20Management&Teams=Promotional%20Content&Teams=Promotional%20Creative%20Production&Teams=Sales%20and%20Business%20Development&Teams=Supply%20Chain&Teams=Product%20%26%20Design&Teams=Data%20Science%20%26%20Analytics&Teams=Consumer%20Products&Teams=Engineering&Teams=Consumer%20Insights&Teams=Finance%2C%20Strategy%2C%20and%20Accounting&Teams=Legal%20%26%20Public%20Policy&Teams=Marketing%20%26%20Promotions&Teams=Public%20Relations&domain=netflix.com&sort_by=relevance"
    job_url = "https://explore.jobs.netflix.net/api/apply/v2/jobs/{}?domain=netflix.com&pid=790299260100&Teams=Engineering+Operations&Teams=Games&Teams=Product&Teams=Program+Management&Teams=Promotional+Content&Teams=Promotional+Creative+Production&Teams=Sales+and+Business+Development&Teams=Supply+Chain&Teams=Product+%26+Design&Teams=Data+Science+%26+Analytics&Teams=Consumer+Products&Teams=Engineering&Teams=Consumer+Insights&Teams=Finance%2C+Strategy%2C+and+Accounting&Teams=Legal+%26+Public+Policy&Teams=Marketing+%26+Promotions&Teams=Public+Relations&sort_by=relevance&triggerGoButton=false"
    log_dir = f"data/logs/{name}"
    os.makedirs(log_dir, exist_ok=True)
    remove_obsolete_jobs = False
    custom_settings = {
        "LOG_FILE": f'data/logs/{name}/{name}_jobs_{datetime.now().strftime("%Y%m%d%H%M%S")}.log',
        "LOG_LEVEL": "DEBUG",
        "LOG_ENABLED": True,
    }

    def start_requests(self):
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "referer": "https://explore.jobs.netflix.net/careers",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        }

        yield scrapy.Request(url=self.start_url.format(0), meta={"start": 0}, headers=headers)

    def parse(self, response, **kwargs):
        headers = response.request.headers
        item = JobItem()
        data = json.loads(response.text)
        total_jobs = data.get("count", 0)
        jobs = data.get("positions", [])
        for job in jobs[:5]:
            position_id = str(job.get("id"))
            item["title"] = job.get("name").strip()
            locations = job.get("locations", [])
            item["location"] = ", ".join(locations)
            item["company"] = "Netflix"
            item['category'] = job.get("department")
            item['apply_link'] = f"https://explore.jobs.netflix.net/careers?pid={job.get('id')}&domain=netflix.com&sort_by=relevance"
            item['type'] = 'Full-Time'
            timestamp = job.get('t_update')
            # Convert the timestamp to a datetime object and format it to 'YYYY-MM-DD'
            formatted_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            item['posted_date'] = formatted_date
            item['description'] = job.get('job_description', '')


            yield scrapy.Request(
                url=self.job_url.format(position_id),
                callback=self.parse_job,
                meta={"item": item}, headers=headers,
            )
        start = response.meta.get('start')
        if start < total_jobs:
            start = start + 10
            yield scrapy.Request(url=self.start_url.format(start), meta={"start": start}, headers=headers)

    def parse_job(self, response):
        item = response.meta.get("item")
        job = json.loads(response.text)
        item["more_description"] = job.get("job_description", "")

        user_prompt = f"Here is the job description:\n\n{item['more_description']}"

        response = chat(
            messages=[{"role": "user", "content": user_prompt}],
            model="jobAi",
            format=JobDetails.model_json_schema(),
        )

        try:
            job_details = JobDetails.model_validate_json(response.message.content)
            item.update(job_details.dict())  # Merge AI extracted details into item
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")

        yield item
