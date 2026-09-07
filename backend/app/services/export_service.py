import csv
import io
import json

def campaign_json(campaign: dict, strategy: dict, assets: list[dict]) -> str:
 return json.dumps({"campaign":campaign,"strategy":strategy,"assets":assets},indent=2,default=str)
def campaign_markdown(campaign: dict, strategy: dict, assets: list[dict]) -> str:
 lines=[f"# {campaign['name']}","","## 7-day campaign"]
 for day,asset in zip(strategy["days"],[item for item in assets if item["platform"]!="seo"]): lines.extend(["",f"## Day {day['day']} — {asset['platform'].title()}","",f"### {asset['title']}","",asset["content"],"",asset.get("cta","")])
 return "\n".join(lines).strip()+"\n"
def campaign_csv(strategy: dict, assets: list[dict]) -> str:
 output=io.StringIO();writer=csv.DictWriter(output,fieldnames=["day","platform","content_type","title","content","status","scheduled_for"]);writer.writeheader()
 for day,asset in zip(strategy["days"],[item for item in assets if item["platform"]!="seo"]):writer.writerow({"day":day["day"],"platform":asset["platform"],"content_type":asset["content_type"],"title":asset["title"],"content":asset["content"],"status":asset["status"],"scheduled_for":asset.get("scheduled_for","")})
 return output.getvalue()
