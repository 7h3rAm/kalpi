#!/usr/bin/env python3

from datetime import datetime, timezone
from pprint import pprint
import time

import utils


class Astro:
  def __init__(self):
    self.apikey = utils.expand_env(var="$NASAKEY")

    self.datastore_url = "https://raw.githubusercontent.com/7h3rAm/datastore/master"
    self.datastore_path = "%s/datastore" % (utils.expand_env(var="$PROJECTSPATH"))
    self.datafile_path = "%s/datastore/astro.json" % (utils.expand_env(var="$PROJECTSPATH"))
    self.downloads = {}
    self.data = {
      "last_update": None,
      "apod": None,
      "neo": None,
      "earthevents": None,
      "satview": None,
      "spacex": None,
    }
    self.category_map = {
      "Drought": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/drought",
        "emoji": "💧",
      },
      "Dust and Haze": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/dustHaze",
        "emoji": "🌫️",
      },
      "Earthquakes": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/earthquakes",
        "emoji": "🌐",
      },
      "Earthquake": {
        "url": "https://earthquake.usgs.gov/earthquakes/",
        "emoji": "🔴",
      },
      "Floods": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/floods",
        "emoji": "🌊",
      },
      "Landslides": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/landslides",
        "emoji": "⛰️",
      },
      "Manmade": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/manmade",
        "emoji": "🧍",
      },
      "Sea and Lake Ice": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/seaLakeIce",
        "emoji": "🧊",
      },
      "Severe Storms": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/severeStorms",
        "emoji": "🌀",
      },
      "Snow": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/snow",
        "emoji": "🌨️",
      },
      "Temperature Extremes": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/tempExtremes",
        "emoji": "🌡️",
      },
      "Volcanoes": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/volcanoes",
        "emoji": "🌋",
      },
      "Water Color": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/waterColor",
        "emoji": "⛲",
      },
      "Wildfires": {
        "url": "https://eonet.sci.gsfc.nasa.gov/api/v3/categories/wildfires",
        "emoji": "🔥",
      }
    }

  def apod(self):
    self.data["apod"] = {
      "todayurl": "https://apod.nasa.gov/apod/astropix.html",
      "archiveurl": "https://apod.nasa.gov/apod/archivepix.html",
    }
    apodjson = utils.download_json("https://api.nasa.gov/planetary/apod?api_key=%s" % (self.apikey))
    self.data["apod"]["title"] = "%s (%s)" % (apodjson["title"], datetime.strptime(apodjson["date"], '%Y-%m-%d').astimezone(tz=None).strftime("%d/%b/%Y %Z"))
    self.data["apod"]["source"] = apodjson["url"]
    self.data["apod"]["datastore"] = "%s/apod.jpg" % (self.datastore_url)
    self.downloads[self.data["apod"]["source"]] = "%s/apod.jpg" % (self.datastore_path)
    utils.download(self.data["apod"]["source"], self.downloads[self.data["apod"]["source"]])
    self.data["apod"]["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")

  def neo(self):
    self.data["neo"] = {
      "date": None,
      "objects": [],
    }
    neojson = utils.download_json("https://api.nasa.gov/neo/rest/v1/feed/today?detailed=true&api_key=%s" % (self.apikey))
    datekey = list(neojson["near_earth_objects"].keys())[0]
    self.data["neo"]["date"] = datetime.strptime(datekey, "%Y-%m-%d").astimezone(tz=None).strftime("%d/%b/%Y %Z")
    for neo in neojson["near_earth_objects"][datekey]:
      self.data["neo"]["objects"].append({
        "cat": datetime.strptime(neo["close_approach_data"][0]["close_approach_date_full"], "%Y-%b-%d %H:%M").strftime("%d/%b/%Y @ %H:%M:%S %Z"),
        "diameter": "%s-%s miles" % ("{:,.2f}".format(float(neo["estimated_diameter"]["miles"]["estimated_diameter_min"])), "{:,.2f}".format(float(neo["estimated_diameter"]["miles"]["estimated_diameter_max"]))),
        "distance": "%s miles" % ("{:,.2f}".format(float(neo["close_approach_data"][0]["miss_distance"]["miles"]))),
        "velocity": "%s mph" % ("{:,.2f}".format(float(neo["close_approach_data"][0]["relative_velocity"]["miles_per_hour"]))),
        "hazardous": neo["is_potentially_hazardous_asteroid"],
        "name": "Asteroid %s" % (neo["name"]),
        "url": neo["nasa_jpl_url"],
      })
    self.data["neo"]["title"] = "%d objects making close approach (%s)" % (len(self.data["neo"]["objects"]), self.data["neo"]["date"])
    self.data["neo"]["objects"] = sorted(self.data["neo"]["objects"], key=lambda k: k["name"])
    self.data["neo"]["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")

  def earthevents(self):
    self.data["earthevents"] = {
      "date": datetime.now().astimezone(tz=None).strftime("%d/%b/%Y %Z"),
      "events": [],
    }
    eonetjson = utils.download_json("https://eonet.sci.gsfc.nasa.gov/api/v3/events?status=open&days=30")
    usgseqjson = utils.download_json("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson")
    self.data["earthevents"]["mapdata"] = {
      "Drought": [],
      "Dust and Haze": [],
      "Earthquakes": [],
      "Floods": [],
      "Landslides": [],
      "Manmade": [],
      "Sea and Lake Ice": [],
      "Severe Storms": [],
      "Snow": [],
      "Temperature Extremes": [],
      "Volcanoes": [],
      "Water Color": [],
      "Wildfires": [],
    }
    for event in eonetjson["events"]:
      self.data["earthevents"]["events"].append({
        "eid": event["id"],
        "name": event["title"],
        "url": event["link"],
        "location": "https://www.google.com/maps/dir/%s/@%s,%s,3z" % ("/".join([",".join([str(x["coordinates"][1]), str(x["coordinates"][0])]) for x in event["geometry"]]), event["geometry"][0]["coordinates"][1], event["geometry"][0]["coordinates"][0]),
        "category": [self.category_map[x["title"]] for x in event["categories"]],
        "source": [{"url": x["url"], "sid": x["id"]} for x in event["sources"]],
      })

      for cat in event["categories"]:

        if cat["title"] == "Drought":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Drought"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Dust and Haze":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Dust and Haze"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Earthquakes":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Earthquakes"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Floods":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Floods"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Landslides":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Landslides"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Manmade":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Manmade"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Sea and Lake Ice":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Sea and Lake Ice"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Severe Storms":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Severe Storms"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Snow":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Snow"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Temperature Extremes":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Temperature Extremes"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Volcanoes":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Volcanoes"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Water Color":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Water Color"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

        if cat["title"] == "Wildfires":
          for coord in event["geometry"]:
            self.data["earthevents"]["mapdata"]["Wildfires"].append(['<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: %s' % (coord["coordinates"][1], coord["coordinates"][0], event["title"], ", ".join(list(sorted([x["title"] for x in event["categories"]]))), ", ".join(list(sorted(['<a href="%s">%s</a>' % (x["url"], x["id"]) for x in event["sources"]])))), coord["coordinates"][1], coord["coordinates"][0]])

    for event in usgseqjson["features"]:
      if event["properties"]["type"] == "earthquake" and event["properties"]["mag"] >= 4:
        self.data["earthevents"]["events"].append({
          "eid": event["id"],
          "name": event["properties"]["title"],
          "url": event["properties"]["url"],
          "location": "http://maps.google.com/maps?q=%s,%s" % (event["geometry"]["coordinates"][1], event["geometry"]["coordinates"][0]),
          "category": [self.category_map[event["properties"]["type"].title()]],
          "source": [{"url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php", "sid": "USGS"}],
        })
        self.data["earthevents"]["mapdata"]["Earthquakes"].append([
          '<a href="http://maps.google.com/maps?q=%s,%s"><b>%s</b></a><br/>Category: %s<br/>Source: <a href="%s">USGS</a>' % (
            event["geometry"]["coordinates"][1],
            event["geometry"]["coordinates"][0],
            event["properties"]["title"],
            event["properties"]["type"].title(),
            event["properties"]["url"],
          ),
          event["geometry"]["coordinates"][1],
          event["geometry"]["coordinates"][0],
        ])

    self.data["earthevents"]["title"] = "%d events (%s)" % (len(self.data["earthevents"]["events"]), self.data["earthevents"]["date"])
    self.data["earthevents"]["events"] = sorted(self.data["earthevents"]["events"], key=lambda k: k["name"])
    self.data["earthevents"]["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")

  def spaceppl(self):
    self.data["spaceppl"] = {
      "title": None,
      "people": [],
    }
    spaceppljson = utils.download_json("http://api.open-notify.org/astros.json")
    for ppl in spaceppljson["people"]:
      self.data["spaceppl"]["people"].append({
        "name": ppl["name"],
        "url": "https://www.google.com/search?q=Astronaut+%s" % (ppl["name"].replace(" ", "+")),
        "spacecraft": ppl["craft"],
      })
    self.data["spaceppl"]["title"] = "%d people in space (%s)" % (len(self.data["spaceppl"]["people"]), datetime.now().astimezone(tz=None).strftime("%d/%b/%Y %Z"))
    self.data["spaceppl"]["people"] = sorted(self.data["spaceppl"]["people"], key=lambda k: k["name"])
    self.data["spaceppl"]["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")

  def spacex(self):
    self.data["spacex"]["capsules"] = []
    capsulesjson = utils.download_json("https://api.spacexdata.com/v4/capsules")
    for capsule in capsulesjson:
      self.data["spacex"]["capsules"].append({
       "name": "(%s) %s" % (capsule["serial"], capsule["type"]),
       "status": capsule["status"] if capsule["status"] else "",
       "status_emoji": utils.to_emoji(capsule["status"]) if capsule["status"] else "",
       "launches": len(capsule["launches"]) if capsule["launches"] else 0,
       "reuse_count": capsule["reuse_count"] if capsule["reuse_count"] else 0,
       "water_landings": capsule["water_landings"] if capsule["water_landings"] else 0,
       "land_landings": capsule["land_landings"] if capsule["land_landings"] else 0,
       "last_update": capsule["last_update"] if capsule["last_update"] else "Location and status unknown",
      })
    self.data["spacex"]["capsules"] = sorted(self.data["spacex"]["capsules"], key=lambda k: k["name"])

    companyjson = utils.download_json("https://api.spacexdata.com/v4/company")
    self.data["spacex"]["company"] = {
      "name": companyjson["name"],
      "url": companyjson["links"]["website"],
      "employees": companyjson["employees"],
      "vehicles": companyjson["vehicles"],
      "launch_sites": companyjson["launch_sites"],
      "test_sites": companyjson["test_sites"],
      "valuation": companyjson["valuation"],
      "valuation_human": utils.currency_human(companyjson["valuation"]),
      "summary": companyjson["summary"],
    }

    # cores
    self.data["spacex"]["cores"] = []
    coresjson = utils.download_json("https://api.spacexdata.com/v4/cores")
    for core in coresjson:
      self.data["spacex"]["cores"].append({
        "name": core["serial"],
        "status": core["status"] if core["status"] else "",
        "status_emoji": utils.to_emoji(core["status"]) if core["status"] else "",
        "last_update": core["last_update"] if core["last_update"] else "",
        "launches": len(core["launches"]) if core["launches"] else 0,
        "rtls_attempts": core["rtls_attempts"] if core["rtls_attempts"] else 0,
        "rtls_landings": core["rtls_landings"] if core["rtls_landings"] else 0,
        "asds_attempts": core["asds_attempts"] if core["asds_attempts"] else 0,
        "asds_landings": core["asds_landings"] if core["asds_landings"] else 0,
        "reuse_count": core["reuse_count"] if core["reuse_count"] else 0,
      })
    self.data["spacex"]["cores"] = sorted(self.data["spacex"]["cores"], key=lambda k: k["name"])

    # crew
    self.data["spacex"]["crew"] = []
    crewjson = utils.download_json("https://api.spacexdata.com/v4/crew")
    for crew in crewjson:
      self.data["spacex"]["crew"].append({
        "name": crew["name"],
        "agency": crew["agency"] if crew["agency"] else "",
        "url": crew["wikipedia"] if crew["wikipedia"] else "",
        "launches": len(crew["launches"]) if crew["launches"] else 0,
        "status": crew["status"] if crew["status"] else "",
        "status_emoji": utils.to_emoji(crew["status"]) if crew["status"] else "",
      })
    self.data["spacex"]["crew"] = sorted(self.data["spacex"]["crew"], key=lambda k: k["name"])

    # dragons
    self.data["spacex"]["dragons"] = []
    dragonsjson = utils.download_json("https://api.spacexdata.com/v4/dragons")
    for dragon in dragonsjson:
      self.data["spacex"]["dragons"].append({
        "name": dragon["name"],
        "description": dragon["description"],
        "first_flight": datetime.strptime(dragon["first_flight"], "%Y-%m-%d").astimezone(tz=None).strftime("%d/%b/%Y %Z"),
        "type": dragon["type"],
        "type_emoji": utils.to_emoji(dragon["type"]),
        "active": dragon["active"],
        "status_emoji": utils.to_emoji("active" if dragon["active"] else "retired"),
        "crew_capacity": dragon["crew_capacity"],
        "dry_mass": "%s lbs" % ("{:,.2f}".format(float(dragon["dry_mass_lb"]))),
        "url": dragon["wikipedia"],
      })
    self.data["spacex"]["dragons"] = sorted(self.data["spacex"]["dragons"], key=lambda k: k["name"])

    # landpads
    self.data["spacex"]["landpads"] = []
    landpadsjson = utils.download_json("https://api.spacexdata.com/v4/landpads")
    for landpad in landpadsjson:
      self.data["spacex"]["landpads"].append({
        "name": "%s (%s)" % (landpad["full_name"], landpad["name"]),
        "type": landpad["type"],
        "location": "%s, %s" % (landpad["locality"], landpad["region"]),
        "location_url": "https://www.google.com/maps/place/%s,%s" % (landpad["latitude"], landpad["longitude"]),
        "url": landpad["wikipedia"],
        "landing_attempts": landpad["landing_attempts"],
        "landing_successes": landpad["landing_successes"],
        "description": landpad["details"],
        "launches": len(landpad["launches"]),
        "status": landpad["status"],
        "status_emoji": utils.to_emoji(landpad["status"]),
      })
    self.data["spacex"]["landpads"] = sorted(self.data["spacex"]["landpads"], key=lambda k: k["name"])

    # launches
    self.data["spacex"]["launches"] = {
      "past": [],
      "future": [],
    }
    launchesjson = utils.download_json("https://api.spacexdata.com/v4/launches")
    for launch in launchesjson:
      launchdata = {
        "name": launch["name"],
        "launch": datetime.fromtimestamp(launch["date_unix"], tz=timezone.utc).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z"),
        "upcoming": launch["upcoming"],
        "flight": launch["flight_number"],
        "description": launch["details"],
        "url": launch["links"]["webcast"],
      }
      if launch["upcoming"]:
        self.data["spacex"]["launches"]["future"].append(launchdata)
      else:
        self.data["spacex"]["launches"]["past"].append(launchdata)
    self.data["spacex"]["launches"]["past"] = sorted(self.data["spacex"]["launches"]["past"], key=lambda k: k["flight"])
    self.data["spacex"]["launches"]["future"] = sorted(self.data["spacex"]["launches"]["future"], key=lambda k: k["flight"])

    # launchpads
    self.data["spacex"]["launchpads"] = []
    launchpadsjson = utils.download_json("https://api.spacexdata.com/v4/launchpads")
    for launchpad in launchpadsjson:
      self.data["spacex"]["launchpads"].append({
        "name": "%s (%s)" % (launchpad["full_name"], launchpad["name"]),
        "location": "%s, %s" % (launchpad["locality"], launchpad["region"]),
        "location_url": "https://www.google.com/maps/place/%s,%s" % (launchpad["latitude"], launchpad["longitude"]),
        "launch_attempts": launchpad["launch_attempts"],
        "launch_successes": launchpad["launch_successes"],
        "description": launchpad["details"],
        "status": launchpad["status"],
        "status_emoji": utils.to_emoji(launchpad["status"]),
      })
    self.data["spacex"]["launchpads"] = sorted(self.data["spacex"]["launchpads"], key=lambda k: k["name"])

    # payloads
    self.data["spacex"]["payloads"] = []
    payloadsjson = utils.download_json("https://api.spacexdata.com/v4/payloads")
    for payload in payloadsjson:
      self.data["spacex"]["payloads"].append({
        "name": payload["name"],
        "type": payload["type"],
        "type_emoji": utils.to_emoji(payload["type"]),
        "customer": ", ".join(payload["customers"]),
        "nationality": ", ".join(payload["nationalities"]),
        "manufacturer": ", ".join(payload["manufacturers"]),
        "orbit": payload["orbit"],
      })
    self.data["spacex"]["payloads"] = sorted(self.data["spacex"]["payloads"], key=lambda k: k["name"])

    # roadster
    self.data["spacex"]["roadster"] = {}
    roadsterjson = utils.download_json("https://api.spacexdata.com/v4/roadster")
    self.data["spacex"]["roadster"]["name"] = roadsterjson["name"]
    self.data["spacex"]["roadster"]["url"] = roadsterjson["video"]
    self.data["spacex"]["roadster"]["date"] = datetime.fromtimestamp(roadsterjson["launch_date_unix"], tz=timezone.utc).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    self.data["spacex"]["roadster"]["description"] = roadsterjson["details"]
    self.data["spacex"]["roadster"]["launch_mass"] = "%s lbs" % ("{:,.2f}".format(float(roadsterjson["launch_mass_lbs"])))
    self.data["spacex"]["roadster"]["orbit"] = roadsterjson["orbit_type"].title()
    self.data["spacex"]["roadster"]["speed"] = "%s mph" % ("{:,.2f}".format(float(roadsterjson["speed_mph"])))
    self.data["spacex"]["roadster"]["earth_distance"] = "%s miles" % ("{:,.2f}".format(float(roadsterjson["earth_distance_mi"])))
    self.data["spacex"]["roadster"]["mars_distance"] = "%s miles" % ("{:,.2f}".format(float(roadsterjson["mars_distance_mi"])))

    # rockets
    self.data["spacex"]["rockets"] = []
    rocketsjson = utils.download_json("https://api.spacexdata.com/v4/rockets")
    for rocket in rocketsjson:

      payload_weights_leo, payload_weights_gto, payload_weights_moon, payload_weights_mars = "", "", "", ""
      for item in rocket["payload_weights"]:
        if item["id"] == "leo":
          payload_weights_leo = "%s lbs" % ("{:,}".format(int(item["lb"])))
        elif item["id"] == "gto":
          payload_weights_gto = "%s lbs" % ("{:,}".format(int(item["lb"])))
        elif item["id"] == "moon":
          payload_weights_moon = "%s lbs" % ("{:,}".format(int(item["lb"])))
        elif item["id"] == "mars":
          payload_weights_mars = "%s lbs" % ("{:,}".format(int(item["lb"])))

      self.data["spacex"]["rockets"].append({
        "name": rocket["name"],
        "stage": rocket["stages"],
        "booster": rocket["boosters"],
        "landing_leg": "%d (%s)" % (rocket["landing_legs"]["number"], rocket["landing_legs"]["material"]),
        "height": "%s feet" % ("{:,}".format(int(rocket["height"]["feet"]))),
        "diameter": "%s feet" % ("{:,}".format(int(rocket["diameter"]["feet"]))),
        "mass": "%s lbs" % ("{:,}".format(int(rocket["mass"]["lb"]))),
        "launch_cost": "$%s" % ("{:,}".format(int(rocket["cost_per_launch"]))),
        "success_rate": "%s%%" % (rocket["success_rate_pct"]),
        "first_flight": datetime.strptime(rocket["first_flight"], "%Y-%m-%d").astimezone(tz=None).strftime("%d/%b/%Y %Z"),
        "description": rocket["description"],
        "url": rocket["wikipedia"],

        "first_stage_reusable": rocket["first_stage"]["reusable"],
        "first_stage_reusable_emoji": utils.to_emoji("good") if rocket["first_stage"]["reusable"] else utils.to_emoji("bad"),
        "first_stage_engine": rocket["first_stage"]["engines"],
        "first_stage_fuel": "%s tons" % (rocket["first_stage"]["fuel_amount_tons"]),
        "first_stage_burn_time": "{:,.2f} sec".format(int(rocket["first_stage"]["burn_time_sec"])) if rocket["first_stage"]["burn_time_sec"] else "",

        "second_stage_reusable": rocket["second_stage"]["reusable"],
        "second_stage_reusable_emoji": utils.to_emoji("good") if rocket["second_stage"]["reusable"] else utils.to_emoji("bad"),
        "second_stage_engine": rocket["second_stage"]["engines"],
        "second_stage_fuel": "%s tons" % (rocket["second_stage"]["fuel_amount_tons"]),
        "second_stage_burn_time": "{:,.2f} sec".format(int(rocket["second_stage"]["burn_time_sec"])) if rocket["second_stage"]["burn_time_sec"] else "",

        "engine": "%s (%d)" % (rocket["engines"]["type"].title(), rocket["engines"]["number"]),
        "engine_propellant": "%s, %s" % (rocket["engines"]["propellant_1"], rocket["engines"]["propellant_2"]),
        "engine_thrust_to_weight": rocket["engines"]["thrust_to_weight"],

        "payload_weights_leo": payload_weights_leo,
        "payload_weights_gto": payload_weights_gto,
        "payload_weights_mars": payload_weights_mars,
        "payload_weights_moon": payload_weights_moon,

        "type": "%d/%d/%s/%s feet/%s feet/%s lbs" % (rocket["stages"], rocket["boosters"], "%d (%s)" % (rocket["landing_legs"]["number"], rocket["landing_legs"]["material"]) if rocket["landing_legs"]["number"] else 0, "{:,}".format(int(rocket["height"]["feet"])), "{:,}".format(int(rocket["diameter"]["feet"])), "{:,}".format(int(rocket["mass"]["lb"]))),
        "first_stage": "%d/%s tons/%s/%s" % (rocket["first_stage"]["engines"], rocket["first_stage"]["fuel_amount_tons"], "{:,.2f} sec".format(int(rocket["first_stage"]["burn_time_sec"])) if rocket["first_stage"]["burn_time_sec"] else "", utils.to_emoji("good") if rocket["first_stage"]["reusable"] else utils.to_emoji("bad")),
        "second_stage": "%d/%s tons/%s/%s" % (rocket["second_stage"]["engines"], rocket["second_stage"]["fuel_amount_tons"], "{:,.2f} sec".format(int(rocket["second_stage"]["burn_time_sec"])) if rocket["second_stage"]["burn_time_sec"] else "", utils.to_emoji("good") if rocket["second_stage"]["reusable"] else utils.to_emoji("bad")),
        "engine": "%d %s engine(s) w/ %s+%s propellants and a thrust-to-weight ratio of %d" % (rocket["engines"]["number"], rocket["engines"]["type"].title(), rocket["engines"]["propellant_1"], rocket["engines"]["propellant_2"], rocket["engines"]["thrust_to_weight"]),
        "payload": "/%s/%s/%s/%s" % (payload_weights_leo, payload_weights_gto, payload_weights_moon, payload_weights_mars),

      })
    self.data["spacex"]["rockets"] = sorted(self.data["spacex"]["rockets"], key=lambda k: k["name"])

    # ships
    self.data["spacex"]["ships"] = []
    shipsjson = utils.download_json("https://api.spacexdata.com/v4/ships")
    for ship in shipsjson:
      self.data["spacex"]["ships"].append({
        "name": ship["name"],
        "status_emoji": utils.to_emoji("good") if ship["active"] else utils.to_emoji("bad"),
        "url": ship["link"],
        "port": ship["home_port"],
        "mass": "%s lbs" % ("{:,.2f}".format(float(item["lb"]))),
        "launches": len(ship["launches"]),
        "type": ship["type"],
        "roles": ", ".join(ship["roles"]),
      })
    self.data["spacex"]["ships"] = sorted(self.data["spacex"]["ships"], key=lambda k: k["name"])

    # starlink
    self.data["spacex"]["starlink"] = {
      "satellites": [],
      "mapdata": [],
      "stats": {
        "inorbit": 0,
        "decayed": 0,
        "total": 0,
        "firstlaunch": None,
        "latestlaunch": None,
      },
    }
    starlinkjson = utils.download_json("https://api.spacexdata.com/v4/starlink")
    locs, epochs = [], []
    for starlink in starlinkjson:
      self.data["spacex"]["starlink"]["stats"]["total"] += 1
      epochs.append(datetime.strptime(starlink["spaceTrack"]["LAUNCH_DATE"], "%Y-%m-%d").timestamp())
      if starlink["latitude"] and starlink["longitude"]:
        self.data["spacex"]["starlink"]["stats"]["inorbit"] += 1
        locs.append("%s,%s" % ("{:,.2f}".format(float(starlink["latitude"])), "{:,.2f}".format(float(starlink["longitude"]))))
        self.data["spacex"]["starlink"]["mapdata"].append([
          '<a href="https://www.n2yo.com/satellite/?s=%s"><b>%s</b></a><br/>Launch: %s<br/>Height: %s<br/>Velocity: %s' % (
              starlink["spaceTrack"]["NORAD_CAT_ID"],
              starlink["spaceTrack"]["OBJECT_NAME"],
              datetime.strptime(starlink["spaceTrack"]["LAUNCH_DATE"], "%Y-%m-%d").astimezone(tz=None).strftime("%d/%b/%Y %Z"),
              "%s miles" % ("{:,.2f}".format(float(starlink["height_km"])*0.62137)) if starlink["height_km"] else "",
              "%s mph" % ("{:,.2f}".format(float(starlink["velocity_kms"])*0.62137*60*60)) if starlink["velocity_kms"] else "",
            ),
          starlink["latitude"],
          starlink["longitude"],
        ])
      else:
        self.data["spacex"]["starlink"]["stats"]["decayed"] += 1
      self.data["spacex"]["starlink"]["satellites"].append({
        "name": starlink["spaceTrack"]["OBJECT_NAME"],
        "url": "https://www.n2yo.com/satellite/?s=%s" % (starlink["spaceTrack"]["NORAD_CAT_ID"]),
        "launch": datetime.strptime(starlink["spaceTrack"]["LAUNCH_DATE"], "%Y-%m-%d").astimezone(tz=None).strftime("%d/%b/%Y %Z"),
        "epoch": datetime.strptime(starlink["spaceTrack"]["LAUNCH_DATE"], "%Y-%m-%d").timestamp(),
        "latitude": starlink["latitude"] if starlink["latitude"] else None,
        "longitude": starlink["longitude"] if starlink["longitude"] else None,
        "location": "http://maps.google.com/maps?q=%s,%s" % (starlink["latitude"], starlink["longitude"]) if starlink["latitude"] and starlink["longitude"] else None,
        "height": "%s miles" % ("{:,.2f}".format(float(starlink["height_km"])*0.62137)) if starlink["height_km"] else None,
        "velocity": "%s mph" % ("{:,.2f}".format(float(starlink["velocity_kms"])*0.62137*60*60)) if starlink["velocity_kms"] else None,
      })
    self.data["spacex"]["starlink"]["satellites"] = sorted(self.data["spacex"]["starlink"]["satellites"], key=lambda k: k["epoch"])
    self.data["spacex"]["starlink"]["stats"]["firstlaunch"] = time.strftime("%d/%b/%Y %Z", time.localtime(min(epochs)))
    self.data["spacex"]["starlink"]["stats"]["latestlaunch"] = time.strftime("%d/%b/%Y %Z", time.localtime(max(epochs)))

    # history
    self.data["spacex"]["history"] = []
    historyjson = utils.download_json("https://api.spacexdata.com/v4/history")
    for history in historyjson:
      self.data["spacex"]["history"].append({
        "title": history["title"],
        "url": history["links"]["article"] if history["links"]["article"] else None,
        "date": datetime.fromtimestamp(history["event_date_unix"], tz=timezone.utc).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%d/%b/%Y %Z"),
        "description": history["details"],
        "epoch": history["event_date_unix"],
      })
    self.data["spacex"]["history"] = sorted(self.data["spacex"]["history"], key=lambda k: k["epoch"])

    self.data["spacex"]["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")

  def satview(self):
    self.data["satview"] = {
      "date": datetime.now().astimezone(tz=None).strftime("%d/%b/%Y %Z"),
      "fullday": {
        "datastore_hstack": "https://raw.githubusercontent.com/7h3rAm/datastore/master/earthview_hstack.gif",
        "datastore_vstack": "https://raw.githubusercontent.com/7h3rAm/datastore/master/earthview_vstack.gif",
        "url": "https://twitter.com/7h3rAm/status/1401555983373987842",
        "title_hstack": "Earth Full Day: 07/JUN/2021 (Horizontally Stacked)",
        "title_vstack": "Earth Full Day: 07/JUN/2021 (Vertically Stacked)",
      },
      "himawari8_naturalcolor": {
        "source": "http://rammb.cira.colostate.edu/ramsdis/online/images/latest/himawari-8/full_disk_ahi_natural_color.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/himwari8_naturalcolor.jpg"
      },
      "himawari8_truecolor": {
        "source": "http://rammb.cira.colostate.edu/ramsdis/online/images/latest/himawari-8/full_disk_ahi_true_color.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/himwari8_truecolor.jpg"
      },
      "goes16_geocolor": {
        "source": "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/1808x1808.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/goes16.jpg"
      },
      "goes17_geocolor": {
        "source": "https://cdn.star.nesdis.noaa.gov/GOES17/ABI/FD/GEOCOLOR/1808x1808.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/goes17.jpg"
      },
      "meteosat0_naturalcolor": {
        "source": "https://eumetview.eumetsat.int/static-images/latestImages/EUMETSAT_MSG_RGBNatColourEnhncd_LowResolution.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/meteosat0.jpg"
      },
      "meteosat415_naturalcolor": {
        "source": "https://eumetview.eumetsat.int/static-images/latestImages/EUMETSAT_MSGIODC_RGBNatColourEnhncd_LowResolution.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/meteosat415.jpg"
      },
      "elektrol": {
        "source": "http://electro.ntsomz.ru/i/splash/20210529-2330.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/elektrol.jpg"
      },
      "insat_fd_ir": {
        "source": "https://mausam.imd.gov.in/Satellite/3Dglobe_ir1.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/insat_ir1.jpg"
      },
      "insat_fd_vis": {
        "source": "https://mausam.imd.gov.in/Satellite/3Dglobe_vis.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/insat_vis.jpg"
      },
      "sdo_0171": {
        "source": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0171.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/sdo_0171.jpg"
      },
      "sdo_0304": {
        "source": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0304.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/sdo_0304.jpg"
      },
      "sdo_hmid": {
        "source": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMID.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/sdo_hmid.jpg"
      },
      "sdo_hmiic": {
        "source": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg",
        "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/sdo_hmiic.jpg"
      },
    }

    epicjson = utils.download_json("https://epic.gsfc.nasa.gov/api/natural")
    ids = []
    for epic in epicjson:
      ids.append(int(epic["identifier"]))
    latest_id = max(ids)
    for epic in epicjson:
      if int(epic["identifier"]) == latest_id:
        date_obj = datetime.strptime("%s GMT" % (epic["date"].replace(" ", "T")), "%Y-%m-%dT%H:%M:%S GMT").replace(tzinfo=timezone.utc)
        self.data["satview"]["dscovr_epic"] = {
          "message": "%s on %s." % (epic["caption"], date_obj.astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")),
          "source": "https://epic.gsfc.nasa.gov/archive/natural/%s/%s/%s/jpg/%s.jpg" % (epic["identifier"][0:4], epic["identifier"][4:6], epic["identifier"][6:8], epic["image"]),
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/dscovr_epic.jpg",
        }

    sats = ["dscovr_epic", "himawari8_naturalcolor", "himawari8_truecolor", "goes16_geocolor", "goes17_geocolor", "meteosat0_naturalcolor", "meteosat415_naturalcolor", "elektrol", "insat_fd_ir", "insat_fd_vis", "sdo_0171", "sdo_0304", "sdo_hmid", "sdo_hmiic"]
    total = len(sats)
    for idx, sat in enumerate(sats):
      destination_filepath = "%s/%s" % (self.datastore_path, self.data["satview"][sat]["datastore"].split("/")[-1])
      print("[%d/%d] %s" % (idx+1, total, self.data["satview"][sat]["source"]))
      try:
        utils.download(self.data["satview"][sat]["source"], destination_filepath)
      except:
        print("[!] could not download from %s" % (self.data["satview"][sat]["source"]))

  def marsphotos(self):
    # https://github.com/chrisccerami/mars-photo-api
    return

  def dsn(self):
    # https://twitter.com/dsn_status
    # https://github.com/russss/pydsn/blob/master/parser.py
    return

  def mrn(self):
    # https://twitter.com/mrn_status
    # https://github.com/russss/mrn_status/blob/main/mrn.py
    # https://mars.nasa.gov/rss/api/?feed=marsrelay&category=all&feedtype=json
    # https://mars.nasa.gov/rss/api/?feed=marsrelay_db&category=all&feedtype=json
    # https://mars.nasa.gov/rss/api/?feed=marsrelay_oe&category=all&feedtype=json
    return

  def solarbody(self):
    self.data["spacex"]["solarbody"] = []
    solarbodyjson = utils.download_json("https://api.le-systeme-solaire.net/rest/bodies/")
    for solarbody in solarbodyjson:
      self.data["spacex"]["solarbody"].append({
        "title": solarbody["title"],
        "url": solarbody["links"]["article"] if solarbody["links"]["article"] else None,
        "date": datetime.fromtimestamp(solarbody["event_date_unix"], tz=timezone.utc).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%d/%b/%Y %Z"),
        "description": solarbody["details"],
        "epoch": solarbody["event_date_unix"],
      })
    self.data["spacex"]["solarbody"] = sorted(self.data["spacex"]["solarbody"], key=lambda k: k["epoch"])

  def spaceprobes(self):
    # https://github.com/spacehackers/api.spaceprob.es
    # http://murmuring-anchorage-8062.herokuapp.com/distances.json
    return

  def update(self):
    self.data = utils.load_json(self.datafile_path)

    self.apod()
    self.data["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.data, self.datafile_path)
    self.earthevents()
    self.data["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.data, self.datafile_path)
    self.neo()
    self.data["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.data, self.datafile_path)
    self.spaceppl()
    self.data["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.data, self.datafile_path)
    self.spacex()
    self.data["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.data, self.datafile_path)
    self.satview()
    self.data["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.data, self.datafile_path)


if __name__ == "__main__":
  astro = Astro()
  astro.update()
