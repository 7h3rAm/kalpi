#!/usr/bin/env python3

import os
import re
import time
import random
import htmlmin
import argparse
import markdown
import dateutil.relativedelta
from datetime import datetime
from jinja2 import Environment, BaseLoader, FileSystemLoader

import utils


class Kalpi:
  def __init__(self):
    self.datadict = {}

    self.datadict["themes"] = {
      "rainbow": "style.rainbow.css",
      "plaintext": "style.plaintext.css",
      "invisibletree": "style.invisibletree.css",
    }
    self.datadict["theme"] = "invisibletree"
    self.datadict["themefile"] = self.datadict["themes"][self.datadict["theme"]]

    self.datadict["bgcolors"] = {
      "index": "#fff5ee",
      "archive": "#eef8f1",
      "tags": "#fff0f5",
      "stats": "#f3f3fd",
      "posts": "#ffffff",
      "pages": "#ffffff",
    }
    self.datadict["bgcolor"] = self.datadict["bgcolors"]["posts"]

    self.datadict["tags"] = {}
    self.datadict["posts"] = {}
    self.datadict["recent_count"] = 5
    self.basedir = "%s/toolbox/repos/7h3rAm.github.io" % (utils.expand_env(var="$HOME"))
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
    self.datadict["startpage"] = utils.load_yaml("%s/startpage.yml" % (self.templatesdir))
    self.datadict["oscp"] = utils.load_yaml("%s/oscp.yml" % (self.templatesdir))
    self.datadict["fitness"] = utils.load_yaml("%s/fitness.yml" % (self.templatesdir))
    self.datadict["life"] = utils.load_yaml("%s/life.yml" % (self.templatesdir))

    self.templatemapping = {
      "index.html": "%s/index.html" % (self.outputdir),
      "archive.html": "%s/archive.html" % (self.outputdir),
      "tags.html": "%s/tags.html" % (self.outputdir),
      "stats.html": "%s/stats.html" % (self.outputdir),

      "cv.html": "%s/pages/cv.html" % (self.outputdir),
      "fitness.html": "%s/pages/fitness.html" % (self.outputdir),
      "life.html": "%s/pages/life.html" % (self.outputdir),
      "oscp.html": "%s/pages/oscp.html" % (self.outputdir),
      "research.html": "%s/pages/research.html" % (self.outputdir),
      "satview.html": "%s/pages/satview.html" % (self.outputdir),
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
    return "".join([text[:self.trimlength], "..."])

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
      utils.info("rendered '%s' (%s)" % (utils.cyan(self.templatemapping[templatefile]), utils.blue(utils.sizeof_fmt(len(html)))))
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
        tagcloud[tag] = "font-size:1.0em; color:%s; padding:20px 5px 20px 5px;" % (colors[0])
      elif percent <= 20:
        tagcloud[tag] = "font-size:1.5em; font-weight:bold; color:%s; padding:20px 5px 20px 5px;" % (colors[1])
      elif percent <= 30:
        tagcloud[tag] = "font-size:2.0em; color:%s; padding:20px 5px 20px 5px;" % (colors[2])
      elif percent <= 40:
        tagcloud[tag] = "font-size:2.5em; font-weight:bold; color:%s; padding:20px 5px 20px 5px;" % (colors[3])
      elif percent <= 50:
        tagcloud[tag] = "font-size:3.0em; color:%s; padding:20px 5px 20px 5px;" % (colors[4])
      elif percent <= 60:
        tagcloud[tag] = "font-size:3.5em; font-weight:bold; color:%s; padding:0px 5px 0px 5px;" % (colors[5])
      elif percent <= 70:
        tagcloud[tag] = "font-size:4.0em; color:%s; padding:0px 5px 0px 5px;" % (colors[6])
      elif percent <= 80:
        tagcloud[tag] = "font-size:4.5em; font-weight:bold; color:%s; padding:0px 5px 0px 5px;" % (colors[7])
      elif percent <= 90:
        tagcloud[tag] = "font-size:5.0em; color:%s; padding:0px 5px 0px 5px;" % (colors[8])
      elif percent <= 100:
        tagcloud[tag] = "font-size:5.5em; font-weight:bold; color:%s; padding:0px 5px 0px 5px;" % (colors[0])

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
        summary = "".join(line.split(":")[1:]).strip()
      if line.startswith("tags:"):
        tags = []
        for tag in "".join(line.split(":")[1:]).strip().split(", "):
          tags.append(tag.replace(" ", "_"))
      if line == "\n":
        content = self.md2html("".join(lines[idx+1:]))
        break
    return date, summary, tags, content

  def get_tree(self, source):
    posts = []
    self.datadict["tags"] = dict()
    for root, ds, fs in os.walk(source):
      for name in fs:
        if name[0] == ".": continue
        if not re.match(r"^.+\.(md|mdown|markdown)$", name): continue
        path = os.path.join(root, name)
        with open(path, "r") as f:
          title = f.readline()[:-1].strip("\n..")
          contentmd = f.readlines()
          date, summary, tags, content = self.parse(contentmd)
          year, month, day = date[:3]
          pretty_date = time.strftime(self.postdateformat, date)
          epoch = time.mktime(date)
          url = "/posts/%d%02d%02d_%s.html" % (year, month, day, os.path.splitext(name)[0])
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
            "previous": None,
            "next": None,
          }
          posts.append(post)
          for tag in tags:
            if tag not in self.datadict["tags"].keys():
              self.datadict["tags"][tag] = [{
                "title": title,
                "url": url,
                "pretty_date": pretty_date,
                "year": year,
                "month": month,
                "day": day,
              }]
            else:
              self.datadict["tags"][tag].append({
                "title": title,
                "url": url,
                "pretty_date": pretty_date,
                "year": year,
                "month": month,
                "day": day,
              })
    return posts

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

    for post in self.datadict["posts"]:
      if post["year"] < stats["duration"]["start_year"]:
        stats["duration"]["start_year"] = post["year"]
      if post["year"] > stats["duration"]["end_year"]:
        stats["duration"]["end_year"] = post["year"]

      stats["dates"].append("%04d%02d%02d" % (post["year"], post["month"], post["day"]))

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

    stats["summary"] = []
    stats["summary"].append("There are a total of `%d` posts with `%d` tags, written over a period of `%dy%dm%dd` (from `%s` till `%s`)" % (stats["count_posts"], stats["count_tags"], rd1.years, rd1.months, rd1.days, datetime.strftime(mindate, "%d/%b/%Y"), datetime.strftime(maxdate, "%d/%b/%Y")))
    stats["summary"].append("From the most recent update (on `%s`), it's been `%dy%dm%dd` when the last post was published and `%dy%dm%dd` since the first post" % (datetime.strftime(curdate, "%d/%b/%Y"), rd2.years, rd2.months, rd2.days, rd3.years, rd3.months, rd3.days))
    stats["summary"].append("The year `%s` has highest number of posts with a count of `%d`, while the year `%s` has lowest number of posts with a count of `%d`" % (stats["max_posts_yyyy"], stats["groups"]["per_yyyy"][stats["max_posts_yyyy"]]["posts"], stats["min_posts_yyyy"], stats["groups"]["per_yyyy"][stats["min_posts_yyyy"]]["posts"]))
    stats["summary"].append("The year `%s` has highest number of tags with a count of `%d`, while the year `%s` has lowest number of tags with a count of `%d`" % (stats["max_tags_yyyy"], len(stats["groups"]["per_yyyy"][stats["max_tags_yyyy"]]["tagslist"]), stats["min_tags_yyyy"], len(stats["groups"]["per_yyyy"][stats["min_tags_yyyy"]]["tagslist"])))
    stats["summary"].append("The most widely used of all `%d` tags across `%d` posts is `%s` while the least used is `%s`" % (stats["count_tags"], stats["count_posts"], stats["most_used_tag"], stats["least_used_tag"]))
    stats["summary"].append("On an average, there are `%d` posts per tag and `%d` posts, `%d` tags per year" % (sum([stats["groups"]["per_tag"][x]["posts"] for x in stats["groups"]["per_tag"]])/len(stats["groups"]["per_tag"].keys()), sum([stats["groups"]["per_yyyy"][x]["posts"] for x in stats["groups"]["per_yyyy"]])/len(stats["groups"]["per_yyyy"].keys()), sum([len(stats["groups"]["per_yyyy"][x]["tagslist"]) for x in stats["groups"]["per_yyyy"]])/len(stats["groups"]["per_yyyy"].keys())))
    stats["summary"] = [self.md2html(x).replace("<p>", "").replace("</p>", "") for x in stats["summary"]]

    ppt = {tag:stats["groups"]["per_tag"][tag]["posts"] for tag in stats["groups"]["per_tag"]}
    utils.to_xkcd(ppt, "%s/posts_per_tag.png" % (self.statsdir), "")

    ppy = {yyyy:stats["groups"]["per_yyyy"][yyyy]["posts"] for yyyy in stats["groups"]["per_yyyy"]}
    utils.to_xkcd(ppy, "%s/posts_per_year.png" % (self.statsdir), "")

    tpy = {yyyy:len(stats["groups"]["per_yyyy"][yyyy]["tagslist"]) for yyyy in stats["groups"]["per_yyyy"]}
    utils.to_xkcd(tpy, "%s/tags_per_year.png" % (self.statsdir), "")

    return stats

  def make(self, args, postprocess=[]):
    if args.theme:
      args.theme = args.theme.lower().strip()
      if args.theme in ["rainbow", "plaintext"]:
        self.datadict["theme"] = args.theme
        self.datadict["themefile"] = self.datadict["themes"][self.datadict["theme"]]
      else:
        utils.warn("theme '%s' not found" % (args.theme))
    utils.info("using '%s (%s)' for blog theme" % (self.datadict["theme"], self.datadict["themefile"]))

    # pages
    self.render_template("cv.html", postprocess=postprocess)
    self.render_template("fitness.html", postprocess=postprocess)
    self.render_template("life.html", postprocess=postprocess)
    self.render_template("oscp.html", postprocess=postprocess)
    self.render_template("research.html", postprocess=postprocess)
    self.render_template("satview.html", postprocess=postprocess)
    self.render_template("startpage.html", postprocess=postprocess)

    # posts
    posts = sorted(self.get_tree(self.postsdir), key=lambda post: post["epoch"], reverse=False)
    self.datadict["posts"] = sorted(posts, key=lambda post: post["epoch"], reverse=True)
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
      self.datadict["bgcolor"] = self.datadict["bgcolors"]["posts"]
      output = self.get_template("post.html", datadict={"metadata": self.datadict["metadata"], "post": post, "themefile": self.datadict["themefile"], "bgcolor": self.datadict["bgcolor"]})
      output = output.replace('<h1>', '<h1 class="h1 collapsible" onclick="toggle(this);">').replace('<h2>', '<h2 class="h2 collapsible" onclick="toggle(this);">').replace('<h3>', '<h3 class="h3 collapsible" onclick="toggle(this);">').replace('<h4>', '<h4 class="h4 collapsible" onclick="toggle(this);">').replace('<ul>', '<ul class="nested">').replace('<ol>', '<ol class="nested">').replace('<p>', '<p class="nested">').replace('<pre><code>', '<pre class="nested"><code>').replace('<pre><code class="','<pre class="nested"><code class="').replace('<p class="nested"><a href="/posts/', '<p><a href="/posts/').replace('<p class="nested">📅 published on ', '<p>📅 published on ')
      html = htmlmin.minify(output, remove_comments=True, remove_empty_space=True) if "minify" in postprocess else output
      utils.file_save(filename, html)
      utils.info("rendered '%s' (%s)" % (utils.magenta(filename), utils.blue(utils.sizeof_fmt(len(html)))))
      self.totalsize += len(output)
      self.minsize += len(html)

    # default
    self.render_template("index.html", postprocess=postprocess)
    self.render_template("archive.html", postprocess=postprocess)
    self.datadict["tagcloud"] = self.tag_cloud()
    self.render_template("tags.html", postprocess=postprocess)
    self.datadict["stats"] = self.gen_stats()
    self.render_template("stats.html", postprocess=postprocess)

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
  parser.add_argument('-t', '--theme', required=False, action='store', help='override default theme file (allowed values: rainbow, plaintext)')
  args = parser.parse_args()

  klp = Kalpi()
  klp.make(args)
