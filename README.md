# demo.scraping.trademark
Web crawling for logos

$ pip install -r requirements.txt


Structure recommended by Kenneth Reitz:
http://docs.python-guide.org/en/latest/writing/structure/

Reference
https://github.com/valignatev/ddd-dynamic
https://pypi.org/project/python-ddd/
http://blog.thedigitalcatonline.com/blog/2016/11/14/clean-architectures-in-python-a-step-by-step-example/

from prj.domain import models as m
from prj.shared.domain import DomainModel
from prj.shared import response_object as ro
from prj.shared import response_object as ro, request_object as req
from prj.repository import UserRepository
from prj.settings import DevConfig
