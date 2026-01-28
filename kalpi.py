#!/usr/bin/env python3

import os
import re
import time
import random
import hashlib
import htmlmin
import argparse
import markdown
import sparkline
import dateutil.relativedelta
import yaml
import requests
from datetime import datetime
from jinja2 import Environment, BaseLoader, FileSystemLoader
from bs4 import BeautifulSoup

import utils


class Kalpi:
  def __init__(self):
    self.datadict = {}

    self.datadict["tags"] = {}
    self.datadict["posts"] = {}
    self.datadict["recent_count"] = 10
    self.basedir = "%s/7h3rAm.github.io" % (utils.expand_env(var="$PROJECTSDIR"))
    self.outputdir = self.basedir
    self.postsdir = "%s/_posts" % (self.basedir)
    self.templatesdir = "%s/_templates" % (self.basedir)
    self.statsdir = "%s/static/files/pages_stats" % (self.outputdir)

    self.pages = {}
    self.pages["research"] = "%s/research.md" % (self.templatesdir)
    self.pages["cv"] = "%s/cv.md" % (self.templatesdir)
    self.pages["life"] = "%s/life.md" % (self.templatesdir)
    self.pages["fitness"] = "%s/fitness.md" % (self.templatesdir)

    self.datadict["pages"] = {}
    self.datadict["metadata"] = utils.load_yaml("%s/toolbox/bootstrap/self.yml" % (utils.expand_env(var="$HOME")))["metadata"]
    # Load CV YAML - handle multi-document format (---...---)
    with open("%s/cv/AnkurTyagi.yml" % (utils.expand_env(var="$PROJECTSDIR"))) as f:
      self.datadict["cv"] = list(yaml.safe_load_all(f))[0]
    self.datadict["fitness"] = utils.load_yaml("%s/fitness.yml" % (self.templatesdir))
    self.datadict["life"] = utils.load_yaml("%s/life.yml" % (self.templatesdir))
    self.datadict["oscp"] = utils.load_yaml("%s/oscp.yml" % (self.templatesdir))
    self.datadict["read"] = utils.load_yaml("%s/read.yml" % (self.templatesdir))
    self.datadict["startpage"] = utils.load_yaml("%s/startpage.yml" % (self.templatesdir))

    self.templatemapping = {
      "index.html": "%s/index.html" % (self.outputdir),
      "archive.html": "%s/archive.html" % (self.outputdir),
      "tags.html": "%s/tags.html" % (self.outputdir),
      "stats.html": "%s/stats.html" % (self.outputdir),
      "feed.xml": "%s/feed.xml" % (self.outputdir),

      "cv.html": "%s/pages/cv.html" % (self.outputdir),
      "fitness.html": "%s/pages/fitness.html" % (self.outputdir),
      "life.html": "%s/pages/life.html" % (self.outputdir),
      "oscp.html": "%s/pages/oscp.html" % (self.outputdir),
      "read.html": "%s/pages/read.html" % (self.outputdir),
      "research.html": "%s/pages/research.html" % (self.outputdir),
      "satview.html": "%s/pages/satview.html" % (self.outputdir),
      "astro.html": "%s/pages/astro.html" % (self.outputdir),
      "startpage.html": "%s/pages/startpage.html" % (self.outputdir),
    }

    self.timeformat = "%B %-d, %Y"
    self.timeformat = "%Y %b %d"
    self.stimeformat = "%b %d"
    self.postdateformat = "%d/%b/%Y"

    self.trimlength = 30
    self.totalsize = 0
    self.minsize = 0

  def join_list(self, inlist, url="/tags.html#"):
    outlist = []
    for item in sorted(inlist):
      outlist.append("<a href=%s%s>%s</a>" % (url, item, item))
    return ", ".join(outlist)

  def join_list_and(self, inlist, url="/tags.html#"):
    outlist = []
    for item in sorted(inlist):
      outlist.append("<a href=%s%s>%s</a>" % (url, item, item))
    set1 = ", ".join(outlist[:-2])
    set2 = " and ".join(outlist[-2:])
    if set1:
      return ", ".join([set1, set2])
    else:
      return set2

  def trim_length(self, text):
    return "".join([text[:self.trimlength], "..."]) if len(text) > self.trimlength else text

  def preprocess_text(self, mdtext):
    return mdtext.replace('\n```\n', '\n```c\n') if "\n```\n" in mdtext else mdtext

  def md2html(self, mdtext):
    return markdown.markdown(mdtext, extensions=["fenced_code", "footnotes", "tables"])

  def clean_text(self, rgx_list, text, subtext=""):
    # https://stackoverflow.com/a/37192727/1079836
    new_text = text
    for rgx_match in rgx_list:
      new_text = re.sub(rgx_match, subtext, new_text)
    return new_text

  def remove_para(self, htmltext):
    return self.clean_text([r"<p>", r"</p>"], text=htmltext)

  def remove_empty_ul(self, htmltext):
    return self.clean_text([r"</li>\s*</ul>\s*<ul>\s*<li>"], text=self.clean_text([r"<p>\s*</p>"], text=htmltext), subtext="</li><li>")

  def get_template(self, templatefile, datadict):
    env = Environment(loader=FileSystemLoader(self.templatesdir), extensions=["jinja2_markdown.MarkdownExtension"], autoescape=False)
    env.trim_blocks = True
    env.lsrtip_blocks = True
    env.filters["md2html"] = self.md2html
    env.filters["removepara"] = self.remove_para
    env.filters["removeemptyul"] = self.remove_empty_ul
    env.filters["joinlist"] = self.join_list
    env.filters["joinlistand"] = self.join_list_and
    env.filters["trimlength"] = self.trim_length
    return env.get_template(templatefile).render(datadict=datadict)

  def render_template(self, templatefile, postprocess=[]):
    if templatefile in self.templatemapping:
      output = self.get_template(templatefile, datadict=self.datadict)
      output = output.replace('<div class="footer"></div>', '<div class="footer footercenter"><span><a href="https://creativecommons.org/licenses/by-sa/4.0/" class="footspan">  </a></span></div>')
      html = output
      if "minify" in postprocess:
        html = htmlmin.minify(output, remove_comments=True, remove_empty_space=True)
      utils.file_save(self.templatemapping[templatefile], html)
      #utils.info("rendered '%s' (%s)" % (utils.cyan(self.templatemapping[templatefile]), utils.blue(utils.sizeof_fmt(len(html)))))
      self.totalsize += len(output)
      self.minsize += len(html)
    else:
      utils.warn("could not find mapping for file '%s'" % (utils.red(templatefile)))

  def render_template_string(self, templatestr):
    env = Environment(loader=BaseLoader, extensions=["jinja2_markdown.MarkdownExtension"], autoescape=False)
    env.trim_blocks = True
    env.lsrtip_blocks = True
    env.filters["md2html"] = self.md2html
    env.filters["removepara"] = self.remove_para
    env.filters["removeemptyul"] = self.remove_empty_ul
    env.filters["joinlist"] = self.join_list
    env.filters["joinlistand"] = self.join_list_and
    env.filters["trimlength"] = self.trim_length
    return env.from_string(htmlmin.minify(templatestr, remove_comments=True, remove_empty_space=True)).render(datadict=self.datadict)

  def tag_cloud(self):
    colors = ["#20b2aa", "#99cc99", "#0c9", "#5b92e5", "#ffcc66", "#00b7eb", "#69359c", "#fe4164", "#a50b5e"]
    random.shuffle(colors)
    maxtagcount = 0
    tags, tagcloud = {}, {}
    for tag in self.datadict["tags"]:
      tagcloud[tag] = None
      tags[tag] = len(self.datadict["tags"][tag])
      if tags[tag] > maxtagcount:
        maxtagcount = tags[tag]
    for tag in tags:
      percent = (tags[tag]*100/maxtagcount)
      if percent <= 10:
        tagcloud[tag] = "font-size:0.9em; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[0])
      elif percent <= 20:
        tagcloud[tag] = "font-size:1.1em; font-weight:bold; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[1])
      elif percent <= 30:
        tagcloud[tag] = "font-size:1.3em; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[2])
      elif percent <= 40:
        tagcloud[tag] = "font-size:1.5em; font-weight:bold; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[3])
      elif percent <= 50:
        tagcloud[tag] = "font-size:1.7em; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[4])
      elif percent <= 60:
        tagcloud[tag] = "font-size:1.9em; font-weight:bold; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[5])
      elif percent <= 70:
        tagcloud[tag] = "font-size:2.1em; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[6])
      elif percent <= 80:
        tagcloud[tag] = "font-size:2.3em; font-weight:bold; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[7])
      elif percent <= 90:
        tagcloud[tag] = "font-size:2.5em; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[8])
      elif percent <= 100:
        tagcloud[tag] = "font-size:2.7em; font-weight:bold; color:%s; margin:0.1em 0.3em; line-height:2;" % (colors[0])

    keys = list(tagcloud.keys())
    random.shuffle(keys)
    tagcloud = {key: tagcloud[key] for key in keys}

    return tagcloud

  def parse(self, lines):
    date, summary, tags, content = None, None, None, None
    for idx, line in enumerate(lines):
      if line.startswith("date:"):
        date = time.strptime("".join(line.split(":")[1:]).strip(), self.postdateformat)
      if line.startswith("summary:"):
        summary = ":".join(line.split(":")[1:]).strip()
        summary = None if summary in ["", "This is the summary for an awesome post."] else summary
      if line.startswith("tags:"):
        tags = []
        for tag in "".join(line.split(":")[1:]).strip().split(", "):
          tags.append(tag.replace(" ", "_"))
      if line == "\n":
        content = self.md2html("".join(lines[idx+1:]))
        break
    return date, summary, tags, content

  def reading_time_bar(self, minutes, maxsize=10):
    """Generate a Unicode block bar for reading time"""
    # max reading time we'll show is 30 minutes
    max_minutes = 30
    filled = min(maxsize, int((minutes / max_minutes) * maxsize))
    bar = "█" * filled + "░" * (maxsize - filled)
    return '<span style="color:var(--muted); font-family:monospace;" title="%d min read">%s</span>' % (minutes, bar)

  def sparkify(self, content, maxsize=10, unique=True, sparkmode=True):
    sparkid = hashlib.sha256(content.encode("utf-8")).hexdigest()
    spark = "".join(sparkline.sparkify([int(x, base=16) for x in sparkid]))
    colors = ["#007bff", "#00bcd4", "#17a2b8", "#20c997", "#2196f3", "#28a745", "#4caf50", "#6610f2", "#6c757d", "#6f42c1", "#8357ff", "#dc3545", "#e83e8c", "#f44336", "#fd7e14", "#ffc107", "#20b2aa", "#99cc99", "#0c9", "#5b92e5", "#ffcc66", "#00b7eb", "#69359c", "#fe4164", "#a50b5e"]
    charmap = {
      "▁": "◐",
      "▂": "■",
      "▃": "◩",
      "▄": "◆",
      "▅": "◢",
      "▆": "◨",
      "▇": "●",
      "█": "▲",
    }
    if unique:
      sparkcolored = "".join(['<span style="color:%s;">%s</span>' % (random.choice(colors), ch if sparkmode else charmap[ch]) for ch in spark[:maxsize]])
      sparkcoloredlong = "".join(['<span style="color:%s;">%s</span>' % (random.choice(colors), ch if sparkmode else charmap[ch]) for ch in spark])
    else:
      chars = ["▣", "►", "◐", "◧", "▤", "▼", "◑", "◨", "▥", "◀", "◒", "◩", "▦", "◆", "◕", "◪", "▧", "◈", "◢", "■", "▨", "◉", "◣", "▩", "◎", "◤", "▲", "●", "◥"]
      sparkcolored = "".join(['<span style="color:%s;">%s</span>' % (random.choice(colors), random.choice(chars)) for _ in range(len(sparkid[:maxsize]))])
      sparkcoloredlong = "".join(['<span style="color:%s;">%s</span>' % (random.choice(colors), random.choice(chars)) for _ in range(len(sparkid))])
    return ('<span class="sparklines" title="%s">%s</span>' % (sparkid, sparkcolored), '<span class="sparklines" title="%s">%s</span>' % (sparkid, sparkcoloredlong))

  def get_tree(self, source):
    posts = []
    self.datadict["tags"] = dict()
    for root, ds, fs in os.walk(source):
      for name in fs:
        if name[0] == ".": continue
        if not re.match(r"^.+\.(md|mdown|markdown)$", name): continue
        path = os.path.join(root, name)
        with open(path, "r") as f:
          title = f.readline()[:-1].strip("\n..").rstrip(":")
          contentmd = self.preprocess_text(f.readlines())
          date, summary, tags, content = self.parse(contentmd)
          year, month, day = date[:3]
          pretty_date = time.strftime(self.postdateformat, date)
          epoch = time.mktime(date)
          url = "/posts/%d%02d%02d_%s.html" % (year, month, day, os.path.splitext(name)[0])
          sparkcolored, sparkcoloredlong = self.sparkify("\n".join(contentmd))

          # calculate word count and reading time early
          content_text = "".join(contentmd)
          code_blocks_count = len(re.findall(r'```', content_text)) // 2
          text_without_code = re.sub(r'```.*?```', '', content_text, flags=re.DOTALL)
          word_count = len(text_without_code.split())
          reading_time = max(1, int(word_count / 200))
          reading_bar = self.reading_time_bar(reading_time)

          # RFC 822 date format for RSS
          rss_date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", date)

          post = {
            "title": title,
            "epoch": epoch,
            "content": content,
            "contentmd": contentmd,
            "url": url,
            "pretty_date": pretty_date,
            "sdate": time.strftime(self.stimeformat, date),
            "date": date,
            "year": year,
            "month": month,
            "day": day,
            "tags": tags,
            "summary": summary,
            "filename": name,
            "sparkline": sparkcolored,
            "sparklinelong": sparkcoloredlong,
            "reading_time": reading_time,
            "reading_bar": reading_bar,
            "word_count": word_count,
            "rss_date": rss_date,
            "previous": None,
            "next": None,
          }
          posts.append(post)
          for tag in tags:
            if tag not in self.datadict["tags"].keys():
              self.datadict["tags"][tag] = [{
                "title": title,
                "tags": tags,
                "sparkline": sparkcolored,
                "sparklinelong": sparkcoloredlong,
                "summary": summary,
                "url": url,
                "pretty_date": pretty_date,
                "year": year,
                "month": month,
                "day": day,
              }]
            else:
              self.datadict["tags"][tag].append({
                "title": title,
                "tags": tags,
                "sparkline": sparkcolored,
                "sparklinelong": sparkcoloredlong,
                "summary": summary,
                "url": url,
                "pretty_date": pretty_date,
                "year": year,
                "month": month,
                "day": day,
              })
    return posts

  def gen_activity_heatmap(self, stats):
    """Generate activity heat map using Unicode blocks"""
    # get all dates
    post_dates = {}
    for date_str in stats["dates"]:
      post_dates[date_str] = post_dates.get(date_str, 0) + 1

    # group by year-month
    months = {}
    for date_str in stats["dates"]:
      ym = date_str[:6]  # YYYYMM
      months[ym] = months.get(ym, 0) + 1

    # create heat map
    heatmap = []
    years = sorted(set(d[:4] for d in stats["dates"]))

    for year in years:
      year_line = year + " "
      for month in range(1, 13):
        ym = "%s%02d" % (year, month)
        count = months.get(ym, 0)
        if count == 0:
          char = "░"
        elif count == 1:
          char = "▒"
        elif count <= 3:
          char = "▓"
        else:
          char = "█"
        year_line += char
      heatmap.append(year_line)

    heatmap.append("      JFMAMJJASOND")
    return "\n".join(heatmap)

  def gen_tag_distribution(self, stats):
    """Generate tag distribution bar chart using Unicode blocks"""
    bars = []
    max_count = max(stats["groups"]["per_tag"][tag]["posts"] for tag in stats["groups"]["per_tag"])

    for tag in sorted(stats["groups"]["per_tag"].keys(), key=lambda t: stats["groups"]["per_tag"][t]["posts"], reverse=True)[:10]:
      count = stats["groups"]["per_tag"][tag]["posts"]
      bar_length = int((count / max_count) * 20)
      bar = "█" * bar_length
      bars.append("%10s %s" % (tag[:10], bar))

    return "\n".join(bars)

  def gen_stats(self):
    stats = {}
    stats["count_posts"] = len(self.datadict["posts"])
    stats["count_tags"] = len(self.datadict["tags"])
    stats["groups"] = {
      "per_yyyymm": {},
      "per_yyyy": {},
      "per_tag": {},
    }
    stats["duration"] = {
      "start_year": 2100,
      "end_year": 2000,
    }
    stats["dates"] = []
    stats["word_counts"] = []
    stats["code_blocks"] = []
    stats["post_details"] = []

    for post in self.datadict["posts"]:
      if post["year"] < stats["duration"]["start_year"]:
        stats["duration"]["start_year"] = post["year"]
      if post["year"] > stats["duration"]["end_year"]:
        stats["duration"]["end_year"] = post["year"]

      stats["dates"].append("%04d%02d%02d" % (post["year"], post["month"], post["day"]))

      # calculate word count (excluding code blocks)
      content_text = "".join(post["contentmd"])
      code_blocks = len(re.findall(r'```', content_text)) // 2
      text_without_code = re.sub(r'```.*?```', '', content_text, flags=re.DOTALL)
      word_count = len(text_without_code.split())

      # calculate reading time (avg 200 words per minute)
      reading_time = max(1, int(word_count / 200))

      stats["word_counts"].append(word_count)
      stats["code_blocks"].append(code_blocks)
      stats["post_details"].append({
        "title": post["title"],
        "url": post["url"],
        "words": word_count,
        "code_blocks": code_blocks,
        "tags_count": len(post["tags"]),
        "date": "%04d-%02d-%02d" % (post["year"], post["month"], post["day"]),
        "reading_time": reading_time
      })

      # add reading time to post
      post["reading_time"] = reading_time
      post["word_count"] = word_count

      key = "%04d%02d" % (post["year"], post["month"])
      if key not in stats["groups"]["per_yyyymm"]:
        stats["groups"]["per_yyyymm"][key] = {
          "posts": 1,
          "tagslist": [],
          "tags": len(post["tags"]),
        }
      else:
        stats["groups"]["per_yyyymm"][key]
        stats["groups"]["per_yyyymm"][key]["posts"] += 1
        stats["groups"]["per_yyyymm"][key]["tags"] += len(post["tags"])
        stats["groups"]["per_yyyymm"][key]["tagslist"] += post["tags"]
        stats["groups"]["per_yyyymm"][key]["tagslist"] = list(set(stats["groups"]["per_yyyymm"][key]["tagslist"]))

      key = "%04d" % (post["year"])
      if key not in stats["groups"]["per_yyyy"]:
        stats["groups"]["per_yyyy"][key] = {
          "posts": 1,
          "tagslist": [],
          "tags": len(post["tags"]),
        }
      else:
        stats["groups"]["per_yyyy"][key]
        stats["groups"]["per_yyyy"][key]["posts"] += 1
        stats["groups"]["per_yyyy"][key]["tags"] += len(post["tags"])
        stats["groups"]["per_yyyy"][key]["tagslist"] += post["tags"]
        stats["groups"]["per_yyyy"][key]["tagslist"] = list(set(stats["groups"]["per_yyyy"][key]["tagslist"]))

      for tag in post["tags"]:
        if tag not in stats["groups"]["per_tag"]:
          stats["groups"]["per_tag"][tag] = {
            "posts": 1,
          }
        else:
          stats["groups"]["per_tag"][tag]["posts"] += 1

    stats["most_used_tag"] = max(stats["groups"]["per_tag"].keys(), key=(lambda key: stats["groups"]["per_tag"][key]["posts"]))
    stats["least_used_tag"] = min(stats["groups"]["per_tag"].keys(), key=(lambda key: stats["groups"]["per_tag"][key]["posts"]))

    stats["max_posts_yyyy"] = max(stats["groups"]["per_yyyy"].keys(), key=(lambda key: stats["groups"]["per_yyyy"][key]["posts"]))
    stats["min_posts_yyyy"] = min(stats["groups"]["per_yyyy"].keys(), key=(lambda key: stats["groups"]["per_yyyy"][key]["posts"]))

    stats["max_tags_yyyy"] = max(stats["groups"]["per_yyyy"].keys(), key=(lambda key: len(stats["groups"]["per_yyyy"][key]["tagslist"])))
    stats["min_tags_yyyy"] = min(stats["groups"]["per_yyyy"].keys(), key=(lambda key: len(stats["groups"]["per_yyyy"][key]["tagslist"])))

    curdate = datetime.now()
    maxdate = datetime.strptime(max(stats["dates"]), "%Y%m%d")
    mindate = datetime.strptime(min(stats["dates"]), "%Y%m%d")
    rd1 = dateutil.relativedelta.relativedelta (maxdate, mindate)
    rd2 = dateutil.relativedelta.relativedelta (curdate, maxdate)
    rd3 = dateutil.relativedelta.relativedelta (curdate, mindate)

    # word count statistics
    total_words = sum(stats["word_counts"])
    avg_words = int(total_words / len(stats["word_counts"])) if stats["word_counts"] else 0
    min_words = min(stats["word_counts"]) if stats["word_counts"] else 0
    max_words = max(stats["word_counts"]) if stats["word_counts"] else 0
    total_code_blocks = sum(stats["code_blocks"])

    # find longest and shortest posts
    longest_post = max(stats["post_details"], key=lambda x: x["words"])
    shortest_post = min(stats["post_details"], key=lambda x: x["words"])

    # store simplified stats for template
    stats["writing_period"] = "%dy%dm%dd" % (rd1.years, rd1.months, rd1.days)
    stats["first_post_date"] = datetime.strftime(mindate, "%d/%b/%Y")
    stats["last_post_date"] = datetime.strftime(maxdate, "%d/%b/%Y")
    stats["days_since_last"] = (curdate - maxdate).days
    stats["avg_posts_per_year"] = int(sum([stats["groups"]["per_yyyy"][x]["posts"] for x in stats["groups"]["per_yyyy"]])/len(stats["groups"]["per_yyyy"].keys()))
    stats["avg_posts_per_tag"] = int(sum([stats["groups"]["per_tag"][x]["posts"] for x in stats["groups"]["per_tag"]])/len(stats["groups"]["per_tag"].keys()))

    # generate visualizations
    stats["activity_heatmap"] = self.gen_activity_heatmap(stats)
    stats["tag_distribution"] = self.gen_tag_distribution(stats)

    # generate content metrics
    stats["content_metrics"] = {
      "total_words": total_words,
      "avg_words": avg_words,
      "min_words": min_words,
      "max_words": max_words,
      "total_code_blocks": total_code_blocks,
      "longest_post": longest_post,
      "shortest_post": shortest_post,
      "top_10_longest": sorted(stats["post_details"], key=lambda x: x["words"], reverse=True)[:10],
      "top_10_shortest": sorted(stats["post_details"], key=lambda x: x["words"])[:10],
    }

    ppt = {tag:stats["groups"]["per_tag"][tag]["posts"] for tag in stats["groups"]["per_tag"]}
    utils.to_xkcd(ppt, "%s/posts_per_tag.png" % (self.statsdir), "")

    ppy = {yyyy:stats["groups"]["per_yyyy"][yyyy]["posts"] for yyyy in stats["groups"]["per_yyyy"]}
    utils.to_xkcd(ppy, "%s/posts_per_year.png" % (self.statsdir), "")

    tpy = {yyyy:len(stats["groups"]["per_yyyy"][yyyy]["tagslist"]) for yyyy in stats["groups"]["per_yyyy"]}
    utils.to_xkcd(tpy, "%s/tags_per_year.png" % (self.statsdir), "")

    return stats

  def fetch_github_stats(self, username):
    """Fetch GitHub statistics using the API"""
    stats = {}
    github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_API_KEY")

    # 1. Fetch rank from github-readme-stats
    try:
      readme_url = f"https://github-readme-stats.vercel.app/api?username={username}"
      response = requests.get(readme_url, timeout=10)
      if response.status_code == 200:
        # Parse SVG to extract rank
        import re
        rank_match = re.search(r'Rank:\s*([A-Z][+-]?)', response.text)
        if rank_match:
          stats["rank"] = f"{rank_match.group(1)} (top 25%)"
    except Exception as e:
      utils.warn(f"Could not fetch GitHub rank: {e}")

    # 2. Fetch all-time commits via GraphQL API (requires token)
    if github_token:
      try:
        graphql_url = "https://api.github.com/graphql"
        headers = {
          "Authorization": f"Bearer {github_token}",
          "Content-Type": "application/json"
        }

        # Get current year to query contribution calendar
        current_year = datetime.now().year

        # Query for contributions over multiple years (go back 10 years)
        total_contributions = 0
        for year in range(current_year - 9, current_year + 1):
          query = """
          query($username: String!, $from: DateTime!, $to: DateTime!) {
            user(login: $username) {
              contributionsCollection(from: $from, to: $to) {
                contributionCalendar {
                  totalContributions
                }
              }
            }
          }
          """

          variables = {
            "username": username,
            "from": f"{year}-01-01T00:00:00Z",
            "to": f"{year}-12-31T23:59:59Z"
          }

          payload = {"query": query, "variables": variables}
          response = requests.post(graphql_url, json=payload, headers=headers, timeout=10)

          if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]["user"]:
              year_contributions = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
              total_contributions += year_contributions

        # Format number (e.g., 16400 -> "16.4k")
        if total_contributions >= 1000:
          stats["total_commits"] = f"{total_contributions/1000:.1f}k"
        else:
          stats["total_commits"] = str(total_contributions)
        utils.info(f"Fetched {total_contributions} total commits via GraphQL")
      except Exception as e:
        utils.warn(f"Could not fetch commits via GraphQL: {e}")
    else:
      # Fallback: Use github-readme-stats for last year only
      try:
        readme_url = f"https://github-readme-stats.vercel.app/api?username={username}"
        response = requests.get(readme_url, timeout=10)
        if response.status_code == 200:
          import re
          commits_match = re.search(r'Total Commits[^:]*:\s*([0-9.]+[kM]?)', response.text)
          if commits_match:
            stats["total_commits"] = f"{commits_match.group(1)} (last year)"
      except Exception as e:
        utils.warn(f"Could not fetch commits from github-readme-stats: {e}")

    # 2. REST API: Followers
    try:
      user_resp = requests.get(f"https://api.github.com/users/{username}", timeout=10)
      if user_resp.status_code == 200:
        stats["followers"] = user_resp.json().get("followers", 0)
    except Exception as e:
      utils.warn(f"Error fetching followers: {e}")

    # 3. REST API: Total PRs
    try:
      pr_resp = requests.get(
        f"https://api.github.com/search/issues?q=author:{username}+type:pr",
        timeout=10
      )
      if pr_resp.status_code == 200:
        stats["total_prs"] = pr_resp.json().get("total_count", 0)
    except Exception as e:
      utils.warn(f"Error fetching PRs: {e}")

    # 4. REST API: Stars and Languages (aggregate from repos)
    try:
      repos_resp = requests.get(
        f"https://api.github.com/users/{username}/repos?per_page=100&sort=stars",
        timeout=10
      )
      if repos_resp.status_code == 200:
        repos = repos_resp.json()

        # Total stars
        stats["total_stars"] = sum(repo.get("stargazers_count", 0) for repo in repos)

        # Aggregate languages (limit to top 30 repos to reduce API calls)
        language_bytes = {}
        for repo in repos[:30]:
          try:
            lang_resp = requests.get(repo["languages_url"], timeout=5)
            if lang_resp.status_code == 200:
              for lang, bytes_count in lang_resp.json().items():
                language_bytes[lang] = language_bytes.get(lang, 0) + bytes_count
          except:
            continue

        # Top 5 languages by usage
        if language_bytes:
          top_langs = sorted(language_bytes.items(), key=lambda x: x[1], reverse=True)[:5]
          stats["languages"] = "/".join([lang.lower() for lang, _ in top_langs])
    except Exception as e:
      utils.warn(f"Error fetching repos/stars/languages: {e}")

    return stats if stats else None

  def fetch_stackoverflow_stats(self, user_id):
    """Fetch StackOverflow statistics using the API and web scraping"""
    stats = {}

    # 1. API call for reputation and badges
    try:
      api_url = f"https://api.stackexchange.com/2.3/users/{user_id}?site=stackoverflow"
      response = requests.get(api_url, timeout=10)
      if response.status_code == 200:
        user = response.json()["items"][0]
        stats["reputation"] = user.get("reputation", 0)
        stats["badges"] = {
          "gold": user.get("badge_counts", {}).get("gold", 0),
          "silver": user.get("badge_counts", {}).get("silver", 0),
          "bronze": user.get("badge_counts", {}).get("bronze", 0),
        }
    except Exception as e:
      utils.warn(f"Error fetching SO API: {e}")

    # 2. Scrape profile page for "People Reached"
    try:
      profile_url = f"https://stackoverflow.com/users/{user_id}"
      headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
      response = requests.get(profile_url, headers=headers, timeout=10)

      if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find impact metric: look for fs-body3 div followed by "reached" text
        stat_divs = soup.find_all('div', class_='fs-body3')
        for div in stat_divs:
          # Check next sibling for "reached" text
          siblings = list(div.next_siblings)
          for sib in siblings[:3]:  # Check first 3 siblings
            if hasattr(sib, 'get_text'):
              sib_text = sib.get_text().strip().lower()
              if 'reached' in sib_text:
                impact_value = div.get_text().strip()
                stats["impact"] = f"~{impact_value} people reached"
                break
          if "impact" in stats:
            break
    except Exception as e:
      utils.warn(f"Error scraping SO profile: {e}")

    return stats if stats else None

  def fetch_google_scholar_stats(self, scholar_id):
    """Fetch Google Scholar statistics by scraping the profile page"""
    try:
      url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en"
      headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
      response = requests.get(url, headers=headers, timeout=10)
      if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        stats = {}

        # Find the table with statistics
        table = soup.find('table', {'id': 'gsc_rsb_st'})
        if table:
          rows = table.find_all('tr')
          for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
              label = cells[0].get_text().strip()
              value = cells[1].get_text().strip()
              if label == "Citations":
                stats["citations"] = value
              elif label == "h-index":
                stats["h_index"] = value
              elif label == "i10-index":
                stats["i10_index"] = value

        return stats if stats else None
      else:
        utils.warn(f"Failed to fetch Google Scholar stats: {response.status_code}")
        return None
    except Exception as e:
      utils.warn(f"Error fetching Google Scholar stats: {e}")
      return None

  def fetch_dscovr_epic_images(self, count=4):
    """Fetch latest DSCOVR EPIC natural color images"""
    try:
      url = "https://epic.gsfc.nasa.gov/api/natural"
      response = requests.get(url, timeout=10)
      if response.status_code == 200:
        data = response.json()
        images = []
        for i, entry in enumerate(data[:count]):
          date_str = entry["date"]
          actual_date = date_str.split(" ")[0]
          year, month, day = actual_date.split("-")
          image_name = entry["image"]

          img_url = f"https://epic.gsfc.nasa.gov/archive/natural/{year}/{month}/{day}/jpg/{image_name}.jpg"
          images.append({
            "url": img_url,
            "caption": entry.get("caption", ""),
            "date": date_str
          })

        return images
      else:
        utils.warn(f"Failed to fetch DSCOVR EPIC data: {response.status_code}")
        return []
    except Exception as e:
      utils.warn(f"Error fetching DSCOVR EPIC data: {e}")
      return []

  def calculate_duration(self, start_date, end_date=None):
    """Calculate duration between two dates in 'X yrs Y mos' format"""
    try:
      # Parse dates in format "Mon/YYYY"
      start = datetime.strptime(start_date, "%b/%Y")
      end = datetime.now() if end_date == "Present" or end_date is None else datetime.strptime(end_date, "%b/%Y")

      delta = dateutil.relativedelta.relativedelta(end, start)
      years = delta.years
      months = delta.months

      if years > 0 and months > 0:
        return f"{years} yr{'s' if years > 1 else ''} {months} mo{'s' if months > 1 else ''}"
      elif years > 0:
        return f"{years} yr{'s' if years > 1 else ''}"
      else:
        return f"{months} mo{'s' if months > 1 else ''}"
    except Exception as e:
      utils.warn(f"Error calculating duration: {e}")
      return "0 mos"

  def update_cv_data(self):
    """Update CV YAML file with latest portfolio stats and calculated durations"""
    cv_path = "%s/cv/AnkurTyagi.yml" % (utils.expand_env(var="$PROJECTSDIR"))

    try:
      # Load CV YAML
      with open(cv_path, 'r') as f:
        cv_data = list(yaml.safe_load_all(f))[0]

      utils.info("Updating CV data...")

      # Update last updated timestamp
      if "trailer" in cv_data and cv_data["trailer"]:
        cv_data["trailer"][0]["lastupdated"] = datetime.now().strftime("%d/%b/%Y")
        utils.info("Updated last updated timestamp")

      # Calculate and update experience durations
      if "experience" in cv_data:
        for exp in cv_data["experience"]:
          if "years" in exp:
            start_end = exp["years"].split(" - ")
            if len(start_end) == 2:
              exp["duration"] = self.calculate_duration(start_end[0], start_end[1])

          if "positions" in exp:
            for pos in exp["positions"]:
              if "years" in pos:
                start_end = pos["years"].split(" - ")
                if len(start_end) == 2:
                  pos["duration"] = self.calculate_duration(start_end[0], start_end[1])
        utils.info("Updated experience durations")

      # Fetch and update GitHub stats
      if "contact" in cv_data and "github" in cv_data["contact"]:
        github_username = cv_data["contact"]["github"]["text"]
        github_stats = self.fetch_github_stats(github_username)
        if github_stats and "portfoliogh" in cv_data:
          # Update metrics while preserving formatting
          for i, metric in enumerate(cv_data["portfoliogh"]["metrics"]):
            if "Rank:" in metric:
              rank = github_stats.get("rank", "S (top 25%)")
              cv_data["portfoliogh"]["metrics"][i] = f"Rank: {rank}"
            elif "Commits:" in metric:
              commits = github_stats.get("total_commits", "16.4k")
              cv_data["portfoliogh"]["metrics"][i] = f"Commits: {commits}"
            elif "Followers:" in metric:
              followers = github_stats.get("followers", 179)
              cv_data["portfoliogh"]["metrics"][i] = f"Followers:     {followers}"
            elif "Pull Requests:" in metric:
              prs = github_stats.get("total_prs", 16)
              cv_data["portfoliogh"]["metrics"][i] = f"Pull Requests: {prs}"
            elif "Stars:" in metric:
              stars = github_stats.get("total_stars", 395)
              cv_data["portfoliogh"]["metrics"][i] = f"Stars: {stars}"
            elif "Languages:" in metric:
              langs = github_stats.get("languages", "python/c/assembly/shell/tex")
              cv_data["portfoliogh"]["metrics"][i] = f"Languages: {langs}"

          # Log what was updated
          updated_fields = []
          if "rank" in github_stats:
            updated_fields.append(f"rank: {github_stats['rank']}")
          if "total_commits" in github_stats:
            updated_fields.append(f"commits: {github_stats['total_commits']}")
          if "followers" in github_stats:
            updated_fields.append(f"followers: {github_stats['followers']}")
          if "total_prs" in github_stats:
            updated_fields.append(f"PRs: {github_stats['total_prs']}")
          if "total_stars" in github_stats:
            updated_fields.append(f"stars: {github_stats['total_stars']}")
          if "languages" in github_stats:
            updated_fields.append(f"languages: {github_stats['languages']}")

          utils.info(f"Updated GitHub stats ({', '.join(updated_fields)})")

      # Fetch and update StackOverflow stats
      if "portfolioso" in cv_data:
        # Extract user ID from URL
        so_url = cv_data["portfolioso"]["url"]
        user_id = so_url.split("/")[-2] if "/" in so_url else None
        if user_id:
          so_stats = self.fetch_stackoverflow_stats(user_id)
          if so_stats:
            for i, metric in enumerate(cv_data["portfolioso"]["metrics"]):
              if "Reputation:" in metric:
                reputation = so_stats.get("reputation", 1915)
                cv_data["portfolioso"]["metrics"][i] = f"Reputation: {reputation}"
              elif "Impact:" in metric:
                impact = so_stats.get("impact", "~634k people reached")
                cv_data["portfolioso"]["metrics"][i] = f"Impact: {impact}"
              elif "Badges:" in metric:
                badges = so_stats.get("badges", {"gold": 2, "silver": 16, "bronze": 18})
                cv_data["portfolioso"]["metrics"][i] = f"Badges:     gold:{badges['gold']}/silver:{badges['silver']}/bronze:{badges['bronze']}"

            # Log what was updated
            updated_fields = []
            if "reputation" in so_stats:
              updated_fields.append(f"reputation: {so_stats['reputation']}")
            if "impact" in so_stats:
              updated_fields.append(f"impact: {so_stats['impact']}")
            if "badges" in so_stats:
              updated_fields.append(f"badges: {so_stats['badges']}")

            utils.info(f"Updated StackOverflow stats ({', '.join(updated_fields)})")

      # Fetch and update Google Scholar stats
      if "portfoliogs" in cv_data:
        # Extract scholar ID from URL
        scholar_url = cv_data["portfoliogs"]["url"]
        if "user=" in scholar_url:
          scholar_id = scholar_url.split("user=")[1].split("&")[0]
          scholar_stats = self.fetch_google_scholar_stats(scholar_id)
          if scholar_stats:
            for i, metric in enumerate(cv_data["portfoliogs"]["metrics"]):
              if "Citations:" in metric:
                cv_data["portfoliogs"]["metrics"][i] = f"Citations: {scholar_stats['citations']}"
              elif "h-index:" in metric:
                cv_data["portfoliogs"]["metrics"][i] = f"h-index:   {scholar_stats['h_index']}"
              elif "i10-index:" in metric:
                cv_data["portfoliogs"]["metrics"][i] = f"i10-index: {scholar_stats['i10_index']}"
            utils.info(f"Updated Google Scholar stats (citations: {scholar_stats['citations']})")

      # Save updated YAML
      with open(cv_path, 'w') as f:
        yaml.safe_dump(cv_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        f.write("\n---\n")

      utils.info("CV data updated successfully")

    except Exception as e:
      utils.warn(f"Error updating CV data: {e}")

  def make(self, args, postprocess=[]):
    # Update CV data with latest stats before building
    self.update_cv_data()

    # Reload CV data after update
    with open("%s/cv/AnkurTyagi.yml" % (utils.expand_env(var="$PROJECTSDIR"))) as f:
      self.datadict["cv"] = list(yaml.safe_load_all(f))[0]

    # posts
    calist = [x.replace(self.basedir, "") for x in utils.search_files_all("%s/static/images/clipart" % (self.basedir))]
    posts = sorted(self.get_tree(self.postsdir), key=lambda post: post["epoch"], reverse=False)
    self.datadict["posts"] = sorted(posts, key=lambda post: post["epoch"], reverse=True)

    # build date for RSS
    self.datadict["build_date"] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    total = len(posts)
    for idx, post in enumerate(posts):
      if idx == 0:
        post["next"] = {}
        post["next"]["title"] = posts[idx+1]["title"]
        post["next"]["url"] = posts[idx+1]["url"]
      elif idx == total-1:
        post["previous"] = {}
        post["previous"]["title"] = posts[idx-1]["title"]
        post["previous"]["url"] = posts[idx-1]["url"]
      else:
        post["previous"] = {}
        post["previous"]["title"] = posts[idx-1]["title"]
        post["previous"]["url"] = posts[idx-1]["url"]
        post["next"] = {}
        post["next"]["title"] = posts[idx+1]["title"]
        post["next"]["url"] = posts[idx+1]["url"]
      filename = "%s%s" % (self.outputdir, post["url"])
      output = self.get_template("post.html", datadict={"metadata": self.datadict["metadata"], "post": post, "tags": self.datadict["tags"]})
      output = output.replace('<h1>', '<h1 class="h1 collapsible" onclick="toggle(this);">').replace('<h2>', '<h2 class="h2 collapsible" onclick="toggle(this);">').replace('<h3>', '<h3 class="h3 collapsible" onclick="toggle(this);">').replace('<h4>', '<h4 class="h4 collapsible" onclick="toggle(this);">').replace('<h5>', '<h5 class="h5 collapsible" onclick="toggle(this);">').replace('<h6>', '<h6 class="h6 collapsible" onclick="toggle(this);">').replace('<ul>', '<ul class="nested active">').replace('<ol>', '<ol class="nested active">').replace('<p>', '<p class="nested active">').replace('<pre><code>', '<pre class="nested active"><code>').replace('<pre><code class="','<pre class="nested active"><code class="').replace('<p class="nested active"><a href="/posts/', '<p><a href="/posts/').replace('<p class="nested active">published on ', '<p>published on ').replace('<p class="nested active">tagged ', '<p>tagged ')
      output = output.replace('](https://7h3ram.github.io/posts/', '](/posts/').replace('href="https://7h3ram.github.io/posts/', 'href="/posts/')
      #output = output.replace('BG_CLIPART_STYLE_HERE', 'class="bgclipart_sq" style="background-image: url(%s);"' % (random.choice(calist)))
      html = htmlmin.minify(output, remove_comments=True, remove_empty_space=True) if "minify" in postprocess else output
      utils.file_save(filename, html)
      #utils.info("rendered '%s' (%s)" % (utils.magenta(filename), utils.blue(utils.sizeof_fmt(len(html)))))
      self.totalsize += len(output)
      self.minsize += len(html)

    # pages
    self.render_template("cv.html", postprocess=postprocess)
    self.render_template("fitness.html", postprocess=postprocess)
    self.render_template("life.html", postprocess=postprocess)
    self.render_template("read.html", postprocess=postprocess)

    # Enrich OSCP writeups with sparkline and tags from posts
    for writeup in self.datadict["oscp"]["resources"]["notes"]["writeups"]:
      for post in self.datadict["posts"]:
        if post["url"] == writeup["url"]:
          writeup["sparkline"] = post["sparkline"]
          writeup["tags"] = post["tags"]
          break

    self.render_template("oscp.html", postprocess=postprocess)
    self.render_template("research.html", postprocess=postprocess)

    # Fetch satellite data before rendering satview
    self.datadict["dscovr_epic_images"] = self.fetch_dscovr_epic_images(count=4)
    self.render_template("satview.html", postprocess=postprocess)
    self.render_template("startpage.html", postprocess=postprocess)

    # default
    self.datadict["stats"] = self.gen_stats()
    self.datadict["tagcloud"] = self.tag_cloud()
    self.render_template("index.html", postprocess=postprocess)
    self.render_template("archive.html", postprocess=postprocess)
    self.render_template("tags.html", postprocess=postprocess)
    self.render_template("stats.html", postprocess=postprocess)
    self.render_template("feed.xml", postprocess=[])

    utils.info("size: total:%s (%d), minified:%s (%d), delta:%s (%d)" % (
      utils.sizeof_fmt(self.totalsize),
      self.totalsize,
      utils.sizeof_fmt(self.minsize),
      self.minsize,
      utils.sizeof_fmt(self.totalsize-self.minsize),
      self.totalsize-self.minsize
    ))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="%s (v%s)" % (utils.blue_bold("kalpi"), utils.green_bold("0.1")))
  args = parser.parse_args()

  klp = Kalpi()
  klp.make(args)
