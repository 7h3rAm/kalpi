#!/usr/bin/env python3

import os
import re
import time
import random
import markdown
from jinja2 import Environment, FileSystemLoader

import utils


class Kalpi:
  def __init__(self):
    self.datadict = {}
    self.datadict["tags"] = {}
    self.datadict["posts"] = {}
    self.basedir = "%s/toolbox/repos/7h3rAm.github.io" % (utils.expand_env(var="$HOME"))
    self.datadict["metadata"] = utils.load_yaml("%s/static/files/self.yml" % (self.basedir))["metadata"]

    self.postsdir = "%s/_posts" % (self.basedir)
    self.templatesdir = "%s/_templates" % (self.basedir)
    self.outputdir = self.basedir

    self.templatemapping = {
      "index.html": "%s/index.html" % (self.outputdir),
      "archive.html": "%s/archive.html" % (self.outputdir),
      "tags.html": "%s/tags.html" % (self.outputdir),
      "research.html": "%s/research.html" % (self.outputdir),
      "earthview.html": "%s/earthview.html" % (self.outputdir),
    }
    self.stats = dict({
      "count_posts": 0,
      "count_tags": 0,
      "count_words": 0,
      "count_readtime": 0,
    })

    self.timeformat = "%B %-d, %Y"
    self.timeformat = "%Y %b %d"
    self.stimeformat = "%b %d"
    self.postdateformat = "%d/%b/%Y"
    self.rssdateformat = "%a, %d %b %Y %H:%M:%S %z"

    self.trimlength = 30
    self.relatedpostscount = 3
    self.relatedpostsstrategy = "tags_date"
    self.relatedpostsstrategy = "tags_random"

    self.prep_datadict()

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

  def prep_datadict(self):
    self.datadict["metadata"]["blog"]["intro"] = self.md2html(self.datadict["metadata"]["blog"]["intro"])

  def get_template(self, templatefile, datadict):
    env = Environment(loader=FileSystemLoader(self.templatesdir), extensions=["jinja2_markdown.MarkdownExtension"])
    env.trim_blocks = True
    env.lsrtip_blocks = True
    env.filters["joinlist"] = self.join_list
    env.filters["joinlistand"] = self.join_list_and
    env.filters["trimlength"] = self.trim_length
    return env.get_template(templatefile).render(datadict=datadict)

  def render_template(self, templatefile):
    if templatefile in self.templatemapping:
      output = self.get_template(templatefile, datadict=self.datadict)
      utils.file_save(self.templatemapping[templatefile], output)
      utils.info("rendered '%s' (%sB)" % (utils.cyan(self.templatemapping[templatefile]), utils.blue(len(output))))
    else:
      utils.warn("could not find mapping for file '%s'" % (utils.red(templatefile)))

  def poststats(self, title, date, summary, tags, content, wpm=240, avgwordlen=5.1):
    wps = wpm/60
    poststats = dict({
      "title": title,
      "year": date[:3][0],
      "month": date[:3][1],
      "day": date[:3][2],
      "words": 0,
      "characters": 0,
      "images": 0,
      "readtime": 0,
      "readtimestr": None,
    })
    for word in content.split(" "):
      poststats["characters"] += len(word)
    poststats["words"] = poststats["characters"]//avgwordlen
    self.stats["count_words"] += poststats["words"]
    t = content.split(" ")
    l = len(t)
    poststats["readtime"] = poststats["words"]/wps
    poststats["readtime"] += 1 if poststats["words"]%wps else 0
    poststats["readtimestr"] = utils.sec_to_human(poststats["readtime"])
    self.stats["count_readtime"] += poststats["readtime"]
    poststats["images"] = len(re.findall(r"<img src=", content))
    return poststats

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
          date, summary, tags, content = self.parse(f.readlines())
          year, month, day = date[:3]
          pretty_date = time.strftime(self.postdateformat, date)
          epoch = time.mktime(date)
          url = "/posts/%d%02d%02d_%s.html" % (year, month, day, os.path.splitext(name)[0])
          post = {
            "title": title,
            "epoch": epoch,
            "content": content,
            "url": url,
            "pretty_date": pretty_date,
            "sdate": time.strftime(self.stimeformat, date),
            "rssdate": time.strftime(self.rssdateformat, date),
            "date": date,
            "year": year,
            "month": month,
            "day": day,
            "tags": tags,
            "summary": summary,
            "filename": name,
            "stats": self.poststats(title, date, summary, tags, content),
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
              }]
            else:
              self.datadict["tags"][tag].append({
                "title": title,
                "url": url,
                "pretty_date": pretty_date,
              })
    return posts

  def tag_cloud(self):
    colors = ["#20b2aa", "#99cc99", "#f2777a", "#bc8f8f", "#d27b53", "#f90", "#ffcc66", "#08f", "#6699cc", "#671d9d", "#cc99cc"]
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
    return tagcloud

  def make(self):
    posts = sorted(self.get_tree(self.postsdir), key=lambda post: post["epoch"], reverse=False)
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
      output = self.get_template("post.html", datadict={"metadata": self.datadict["metadata"], "post": post})
      utils.file_save(filename, output)
      utils.info("rendered '%s' (%sB)" % (utils.magenta(filename), utils.blue(len(output))))

    self.datadict["posts"] = sorted(posts, key=lambda post: post["epoch"], reverse=True)
    self.render_template("index.html")
    self.render_template("archive.html")
    self.render_template("research.html")
    self.render_template("earthview.html")
    self.datadict["tagcloud"] = self.tag_cloud()
    self.render_template("tags.html")


if __name__ == "__main__":
  klp = Kalpi()
  klp.make()
