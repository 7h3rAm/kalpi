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
import shutil
import datetime
from pprint import pprint

try:
  import jinja2
  import markdown2 as markdown
except ImportError as error:
  print 'ImportError:', str(error)
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
  # 4. pandoc: md->tex->pdf
  # 5. related posts (top 3 by tags)
  # 6. move static templates to yaml
  # 7. latex cv; last updated; typeset: xelatex

  def __init__(self):
    self.baseurl = "http://7h3ram.github.io/"

    self.basepath = os.path.dirname(os.path.realpath(__file__))
    self.basepath = "/home/shiv/toolbox/7h3rAm.github.com"

    self.blogdir = "%s/" % (self.basepath)
    self.postsdir = "%s/_posts/" % (self.basepath)
    self.templatedir = "%s/_templates/" % (self.basepath)
    self.staticdir = "%s/_static/" % (self.basepath)
    self.homepostscount = 5
    self.templateopts = dict()

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

    self.format = lambda text: markdown.markdown(text, extras=['fenced-code-blocks','footnotes', 'metadata', 'smarty-pants', 'tables'])

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
        content = self.format(''.join(lines[idx+1:]).decode('UTF-8'))
        break
    return date, summary, tags, content

  def get_tree(self, source):
    files = list()
    for root, ds, fs in os.walk(source):
      for name in fs:
        if name[0] == ".": continue
        if not re.match(r'^.+\.(md|mdown|markdown)$', name): continue
        path = os.path.join(root, name)
        with open(path, "rU") as f:
          title = f.readline().decode('UTF-8')[:-1].strip('\n..')
          date, summary, tags, content = self.parse(f.readlines())
          year, month, day = date[:3]
          url = '/'.join([str(year), os.path.splitext(name)[0] + self.urlextension])
          files.append({
            'title': title,
            'epoch': time.mktime(date),
            'content': content,
            'url': url,
            'pretty_date': time.strftime(self.timeformat, date),
            'sdate': time.strftime(self.stimeformat, date),
            'rssdate': time.strftime(self.rssdateformat, date),
            'date': date,
            'year': year,
            'month': month,
            'day': day,
            'tags': tags,
            'summary': summary,
            'filename': name})
    return files

  def write_file(self, url, data):
    path = self.blogdir + url + self.pathextension
    dirs = os.path.dirname(path)
    if not os.path.isdir(dirs): os.makedirs(dirs)
    with open(path, "w") as file:
      file.write(data.encode('UTF-8'))

  def write_feed(self, url, data):
    path = self.blogdir + url
    with open(path, "w") as file:
      file.write(data.encode('UTF-8'))

  def write_sitemap(self, url, data):
    path = self.blogdir + url
    with open(path, "wb") as file:
      file.write(data.encode('UTF-8'))

  def do_static(self):
    utils().copy_dir(self.staticdir, "%s/static/" % (self.blogdir))

  def gen_posts(self, f, e, d):
    for file in f:
      self.write_file(file['url'], e.get_template('post.html').render(post=file, posts=f, baseurl=self.baseurl, date=d))

  def gen_index(self, f, e, d):
    self.write_file('index' + self.urlextension, e.get_template('index.html').render(posts=f[:self.homepostscount], baseurl=self.baseurl, date=d))

  def gen_archive(self, f, e, d):
    self.write_file('archive' + self.urlextension, e.get_template('archive.html').render(posts=f, baseurl=self.baseurl, date=d))

  def gen_tags(self, f, e, d):
    tags = dict({})
    for file in f:
      for tag in file["tags"]:
        if tag not in tags.keys():
          tags[tag] = dict({
            "count": 0,
            "files": [file]
          })
        else:
          tags[tag]["count"] += 1
          tags[tag]["files"].append(file)
    self.write_file('tags' + self.urlextension, e.get_template('tags.html').render(tags=tags, baseurl=self.baseurl, date=d))

  def gen_code(self, f, e, d):
    self.write_file('code' + self.urlextension, e.get_template('code.html').render(posts=f, baseurl=self.baseurl, date=d))

  def gen_talks(self, f, e, d):
    self.write_file('talks' + self.urlextension, e.get_template('talks.html').render(posts=f, baseurl=self.baseurl, date=d))

  def gen_cv(self, f, e, d):
    self.write_file('cv' + self.urlextension, e.get_template('cv.html').render(posts=f, baseurl=self.baseurl, date=d))

  def gen_about(self, f, e, d):
    self.write_file('about' + self.urlextension, e.get_template('about.html').render(post=file, baseurl=self.baseurl, date=d))

  def gen_rss(self, f, e, d):
    self.write_feed('rss.xml', e.get_template('rss.html').render(posts=f[:self.homepostscount], baseurl=self.baseurl, date=d))

  def gen_sitemap(self, f, e, d):
    self.write_sitemap('sitemap.xml', e.get_template('sitemap.html').render(posts=f, baseurl=self.baseurl, date=d))

  def create(self):
    date = utils().get_current_date()
    self.do_static()

    files = sorted(self.get_tree(self.postsdir), key=lambda post: post['epoch'], reverse=True)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templatedir), extensions=['jinja2_markdown.MarkdownExtension'], **self.templateopts)
    env.filters['monthname'] = utils().get_month_name
    env.filters['joinlistand'] = utils().join_list_and

    self.gen_posts(files, env, date)
    self.gen_index(files, env, date)
    self.gen_archive(files, env, date)
    self.gen_tags(files, env, date)
    self.gen_code(files, env, date)
    self.gen_talks(files, env, date)
    self.gen_cv(files, env, date)
    self.gen_about(files, env, date)
    self.gen_rss(files, env, date)
    self.gen_sitemap(files, env, date)


if __name__ == "__main__":
  sys.exit(kalpi().create())
