"""Generate a public-only activity snapshot without credentials.

No private data, account-wide listing, user contribution counts, or raw
issue/PR text are requested. Failed collection leaves the last snapshot intact.
"""
import json
import re
import urllib.request
from pathlib import Path

REPO = "pooriamn/pooriamn"
API = "https://api.github.com/repos/" + REPO
ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r"v?[0-9]+\.[0-9]+\.[0-9]+(?:[-.][A-Za-z0-9.-]+)?\Z")

def get(path):
    # Do not send a token; public visibility is checked independently.
    request = urllib.request.Request(API+path, headers={
        "Accept":"application/vnd.github+json",
        "User-Agent":"public-engineering-portfolio",
        "X-GitHub-Api-Version":"2022-11-28"})
    with urllib.request.urlopen(request,timeout=15) as response:
        return json.load(response)

def pages(getter,path):
    rows=[]
    for page in range(1,11):
        delimiter="&" if "?" in path else "?"
        batch=getter(path+delimiter+"per_page=100&page="+str(page))
        if not isinstance(batch,list) or any(not isinstance(row,dict) for row in batch):
            raise ValueError("Unexpected public API collection")
        rows.extend(batch)
        if len(batch)<100:
            return rows
    raise ValueError("Collection exceeds snapshot limit; refusing partial counts")

def collect(getter=get):
    metadata=getter("")
    if metadata.get("full_name")!=REPO or metadata.get("private") is not False or metadata.get("visibility")!="public":
        raise ValueError("Repository is not explicitly public")
    pulls=pages(getter,"/pulls?state=all")
    issues=pages(getter,"/issues?state=open")
    releases=pages(getter,"/releases")
    published=[r for r in releases if r.get("draft") is False and r.get("prerelease") is False and r.get("published_at")]
    published.sort(key=lambda r:r["published_at"],reverse=True)
    latest=published[0].get("tag_name") if published else None
    if latest is not None and not TAG.fullmatch(latest):
        raise ValueError("Unexpected release tag")
    return {"repository":REPO,"open_issues":sum("pull_request" not in i for i in issues),
            "merged_pull_requests":sum(bool(p.get("merged_at")) for p in pulls),
            "published_releases":len(published),"latest_release":latest}

def render(snapshot):
    cards=[("Open issues",snapshot["open_issues"]),("Merged pull requests",snapshot["merged_pull_requests"]),("Published releases",snapshot["published_releases"])]
    for _,value in cards:
        if type(value) is not int or value<0:
            raise ValueError("Invalid count")
    latest=snapshot["latest_release"]
    if latest is not None and not TAG.fullmatch(latest):
        raise ValueError("Invalid tag")
    panels="".join(f'<rect x="{32+i*304}" y="99" width="280" height="116" rx="8" fill="#fff" stroke="#d9e4e7"/><text x="{50+i*304}" y="133" fill="#4b6270" font-size="16">{label}</text><text x="{50+i*304}" y="187" fill="#142c3a" font-size="38" font-weight="700">{value}</text>' for i,(label,value) in enumerate(cards))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="280" viewBox="0 0 960 280" role="img"><title>Public repository activity</title><rect width="960" height="280" rx="12" fill="#f4f7f8"/><g font-family="Arial,Helvetica,sans-serif"><text x="32" y="42" fill="#087e83" font-size="15" font-weight="700" letter-spacing="2">PUBLIC DEVELOPMENT</text><text x="32" y="75" fill="#142c3a" font-size="25" font-weight="700">Engineering toolkit · GitHub activity</text>{panels}<text x="32" y="251" fill="#4b6270" font-size="14">Latest stable release: {latest or "not published"} · Public repository only; not account-wide activity.</text></g></svg>'

def publish(snapshot,root=ROOT):
    svg=render(snapshot)
    payload=json.dumps(snapshot,indent=2,sort_keys=True)+"\n"
    # Collection and rendering complete before any output is touched.
    for path,content in [("activity/snapshot.json",payload),("assets/public-activity.svg",svg),("docs/assets/public-activity.svg",svg)]:
        target=root/path
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists() or target.read_text(encoding="utf-8")!=content:
            target.write_text(content,encoding="utf-8")

if __name__=="__main__":
    publish(collect())
