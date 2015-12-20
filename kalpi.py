#!/usr/bin/env python
# encoding: utf-8
# Chisel by David Zhou, github.com/dz
# Fork and mod by Chyetanya Kunte, github.com/ckunte
# Forked and more mods by Ankur Tyagi (@7h3rAm)

import os
import re
import sys
import time
import errno
import random
import shutil
import datetime
import StringIO
from pprint import pprint

try:
  import jinja2
  import ho.pisa as pisa
  import markdown2 as markdown
except ImportError as error:
  print "ImportError:", str(error)
  exit(1)


class utils:
  def __init__(self):
    self.months = {
      1: "January",
      2: "February",
      3: "March",
      4: "April",
      5: "May",
      6: "June",
      7: "July",
      8: "August",
      9: "September",
      10: "October",
      11: "November",
      12: "December"
    }

  def get_current_date(self, timeformat="%B %-d, %Y"):
    return time.strftime(timeformat)

  def copy_dir(self, src, dest):
    if os.path.exists(dest):
      shutil.rmtree(dest)
    try:
      shutil.copytree(src, dest)
    except OSError as e:
      if e.errno == errno.ENOTDIR:
        shutil.copy(src, dest)
      else:
        print e

  def get_month_name(self, monthint):
    if monthint >= 1 and monthint <= 12:
      return self.months[monthint]
    else:
      return None

  def join_list_and(self, inlist, url="/tags.html#"):
    outlist = []
    for item in inlist:
      outlist.append("<a href=%s%s>%s</a>" % (url, item, item))
    set1 = ", ".join(outlist[:-2])
    set2 = " and ".join(outlist[-2:])
    if set1:
      return ", ".join([set1, set2])
    else:
      return set2


class kalpi:
  # todo
  # 1. qr code
  # 2. tags count
  # 3. tags styling
  # 4. move static templates to yaml
  # 5. blog dashboard

  def __init__(self):
    self.baseurl = "http://7h3ram.github.io/"
    #self.baseurl = "/"
    self.basepath = "/home/shiv/toolbox/7h3rAm.github.com"
    self.blogdir = "%s/" % (self.basepath)
    self.postsdir = "%s/_posts/" % (self.basepath)
    self.templatedir = "%s/_templates/" % (self.basepath)
    self.staticdir = "%s/_static/" % (self.basepath)
    self.homepostscount = 5
    self.relatedpostscount = 3
    self.relatedpostsstrategy = "tags_date"
    self.relatedpostsstrategy = "tags_random"
    self.templateopts = dict()
    self.pdf = False
    self.mdbaseurl = "https://raw.githubusercontent.com/7h3rAm/7h3rAm.github.io/master/_posts/"

    self.urlextension = ".html"
    if self.urlextension == ".html":
      self.pathextension = ""
      pass
    if self.urlextension == "":
      self.pathextension = ".html"
      pass

    self.timeformat = "%B %-d, %Y"
    self.stimeformat = "%b %d"
    self.rssdateformat = "%a, %d %b %Y %H:%M:%S %z"
    self.postdateformat = "%d/%b/%Y"

    self.format = lambda text: markdown.markdown(text, extras=["fenced-code-blocks","footnotes", "metadata", "smarty-pants", "tables"])

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
        content = self.format("".join(lines[idx+1:]).decode("UTF-8"))
        break
    return date, summary, tags, content

  def get_tree(self, source):
    files = list()
    self.tagsinfo = dict()
    for root, ds, fs in os.walk(source):
      for name in fs:
        if name[0] == ".": continue
        if not re.match(r"^.+\.(md|mdown|markdown)$", name): continue
        path = os.path.join(root, name)
        with open(path, "rU") as f:
          title = f.readline().decode("UTF-8")[:-1].strip("\n..")
          date, summary, tags, content = self.parse(f.readlines())
          year, month, day = date[:3]
          pretty_date = time.strftime(self.timeformat, date)
          epoch = time.mktime(date)
          url = "/".join([str(year), os.path.splitext(name)[0] + self.urlextension])
          files.append({
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
            "filename": name})

          for tag in tags:
            if self.relatedpostsstrategy == "tags_date":
              if tag not in self.tagsinfo.keys():
                self.tagsinfo[tag] = dict({
                  epoch: [(title, url, pretty_date)]
                })
              elif epoch not in self.tagsinfo[tag].keys():
                self.tagsinfo[tag][epoch] = [(title, url, pretty_date)]
              else:
                self.tagsinfo[tag][epoch].append((title, url, pretty_date))

            elif self.relatedpostsstrategy == "tags_random":
              if tag not in self.tagsinfo.keys():
                self.tagsinfo[tag] = list([(title, url, pretty_date)])
              else:
                self.tagsinfo[tag].append((title, url, pretty_date))

            else:
              pass

    return files

  def write_file(self, url, data, pdfdata=None):
    path = self.blogdir + url + self.pathextension
    dirs = os.path.dirname(path)
    if not os.path.isdir(dirs): os.makedirs(dirs)
    with open(path, "w") as file:
      file.write(data.encode("UTF-8"))

    if self.pdf and pdfdata:
      pisa.pisaDocument(StringIO.StringIO(pdfdata.encode("UTF-8")), open("%s%s" % (self.blogdir, url.replace(self.urlextension, ".pdf")), "wb"))

  def write_feed(self, url, data):
    path = self.blogdir + url
    with open(path, "w") as file:
      file.write(data.encode("UTF-8"))

  def write_sitemap(self, url, data):
    path = self.blogdir + url
    with open(path, "wb") as file:
      file.write(data.encode("UTF-8"))

  def do_static(self):
    utils().copy_dir(self.staticdir, "%s/static/" % (self.blogdir))

  def gen_posts(self):
    for f in self.files:
      related_posts = list()
      if self.relatedpostsstrategy == "tags_date":
        rlposts = dict()
        for tag in f["tags"]:
          for epoch in self.tagsinfo[tag]:
            if self.tagsinfo[tag][epoch][0][0] == f["title"]:
              continue
            rlposts[epoch] = self.tagsinfo[tag][epoch][0]

        for epoch in sorted(rlposts, reverse=True):
          related_posts.append(rlposts[epoch])

      elif self.relatedpostsstrategy == "tags_random":
        rlposts = list()
        for tag in f["tags"]:
          for tag in self.tagsinfo[tag]:
            rlposts.append(tag)

        random.shuffle(rlposts)
        for tag in rlposts:
          if tag[0] == f["title"]:
            continue
          if tag not in related_posts:
            related_posts.append(tag)

      self.write_file(url=f["url"], data=self.env.get_template("post.html").render(post=f, posts=self.files, mdbaseurl=self.mdbaseurl, related_posts=related_posts[:self.relatedpostscount], baseurl=self.baseurl, date=self.date), pdfdata=self.env.get_template("post_pdf.html").render(post=f, posts=self.files, mdbaseurl=self.mdbaseurl, related_posts=related_posts[:self.relatedpostscount], baseurl=self.baseurl, date=self.date))

  def gen_index(self):
    self.write_file("index%s" % self.urlextension, self.env.get_template("index.html").render(posts=self.files[:self.homepostscount], baseurl=self.baseurl, date=self.date))

  def gen_archive(self):
    self.write_file("archive%s" % self.urlextension, self.env.get_template("archive.html").render(posts=self.files, baseurl=self.baseurl, date=self.date))

  def gen_tags(self):
    self.tags = dict({})
    for file in self.files:
      for tag in file["tags"]:
        if tag not in self.tags.keys():
          self.tags[tag] = dict({
            "count": 0,
            "files": [file]
          })
        else:
          self.tags[tag]["count"] += 1
          self.tags[tag]["files"].append(file)
    self.write_file("tags%s" % self.urlextension, self.env.get_template("tags.html").render(tags=self.tags, baseurl=self.baseurl, date=self.date))

  def gen_code(self):
    self.write_file("code%s" % self.urlextension, self.env.get_template("code.html").render(posts=self.files, baseurl=self.baseurl, date=self.date))

  def gen_talks(self):
    self.write_file("talks%s" % self.urlextension, self.env.get_template("talks.html").render(posts=self.files, baseurl=self.baseurl, date=self.date))

  def gen_cv(self):
    self.write_file("cv%s" % self.urlextension, self.env.get_template("cv.html").render(posts=self.files, baseurl=self.baseurl, date=self.date))

  def gen_about(self):
    self.write_file("about%s" % self.urlextension, self.env.get_template("about.html").render(baseurl=self.baseurl, date=self.date))

  def gen_rss(self):
    self.write_feed("rss.xml", self.env.get_template("rss.html").render(posts=self.files[:self.homepostscount], baseurl=self.baseurl, date=self.date))

  def gen_sitemap(self):
    self.write_sitemap("sitemap.xml", self.env.get_template("sitemap.html").render(posts=self.files, baseurl=self.baseurl, date=self.date))

  def create(self):
    self.date = utils().get_current_date()
    self.files = sorted(self.get_tree(self.postsdir), key=lambda post: post["epoch"], reverse=True)
    self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templatedir), extensions=["jinja2_markdown.MarkdownExtension"], **self.templateopts)
    self.env.filters["monthname"] = utils().get_month_name
    self.env.filters["joinlistand"] = utils().join_list_and

    self.do_static()
    self.gen_posts()
    self.gen_index()
    self.gen_archive()
    self.gen_tags()
    self.gen_code()
    self.gen_talks()
    self.gen_cv()
    self.gen_about()
    self.gen_rss()
    self.gen_sitemap()


if __name__ == "__main__":
  sys.exit(kalpi().create())
