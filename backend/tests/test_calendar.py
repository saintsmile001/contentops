import asyncio
import unittest
from app.services.calendar_service import CalendarService
class Campaigns:
 async def get(self,*_):return {"id":"c"}
 async def get_strategy(self,*_):return {"days":[{"day":i,"platform":"linkedin"} for i in range(1,8)]}
class Assets:
 def __init__(self):self.items=[{"id":str(i),"platform":"linkedin","content_type":"post","title":f"Post {i}","status":"READY"} for i in range(1,8)]
 async def list(self,*_):return self.items
 async def schedule(self,id,when):
  item=next(x for x in self.items if x["id"]==id);return {**item,"scheduled_for":when}
class QA:
 async def list_for_assets(self,*_):return []
class CalendarTests(unittest.TestCase):
 def test_calendar_has_one_event_per_day(self):
  events=asyncio.run(CalendarService(Campaigns(),Assets(),QA()).build("c","u"));self.assertEqual(len(events),7);self.assertEqual([e["day"] for e in events],list(range(1,8)))
