#!/usr/bin/env python3

from datetime import datetime, timezone
from pprint import pprint

import utils


class Astro:
  def __init__(self):
    self.apikey = utils.expand_env(var="$NASAKEY")

    self.datastore_url = "https://raw.githubusercontent.com/7h3rAm/datastore/master"
    self.datastore_path = "%s/datastore" % (utils.expand_env(var="$PROJECTSPATH"))
    self.downloads = {}

    self.data = {
      "last_update": None,
      "apod": {
        "todayurl": "https://apod.nasa.gov/apod/astropix.html",
        "archiveurl": "https://apod.nasa.gov/apod/archivepix.html",
        "title": None,
        "source": None,
        "datastore": None,
      },
      "neo": {
        "title": None,
        "date": None,
        "objects": [],
      },
      "eonet": {
        "date": None,
        "events": [],
      },
      "satview": {
        "dscovr_epic": {
          "message": "This image was taken by NASA's EPIC camera onboard the NOAA DSCOVR spacecraft on 2021-05-26 00:13:03.",
          "source": "https://epic.gsfc.nasa.gov/archive/natural/2021/05/26/jpg/epic_1b_20210526001752.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/dscovr_epic.jpg"
        },
        "himawari8_naturalcolor": {
          "source": "http://rammb.cira.colostate.edu/ramsdis/online/images/latest/himawari-8/full_disk_ahi_natural_color.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/himwari8-full_disk_ahi_natural_color.jpg"
        },
        "himawari8_truecolor": {
          "source": "http://rammb.cira.colostate.edu/ramsdis/online/images/latest/himawari-8/full_disk_ahi_true_color.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/himwari8-full_disk_ahi_true_color.jpg"
        },
        "goes16_geocolor": {
          "source": "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/1808x1808.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/goes16-1808x1808.jpg"
        },
        "goes17_geocolor": {
          "source": "https://cdn.star.nesdis.noaa.gov/GOES17/ABI/FD/GEOCOLOR/1808x1808.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/goes17-1808x1808.jpg"
        },
        "meteosat0_naturalcolor": {
          "source": "https://eumetview.eumetsat.int/static-images/latestImages/EUMETSAT_MSG_RGBNatColourEnhncd_LowResolution.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/EUMETSAT_MSG_RGBNatColourEnhncd_LowResolution.jpg"
        },
        "meteosat415_naturalcolor": {
          "source": "https://eumetview.eumetsat.int/static-images/latestImages/EUMETSAT_MSGIODC_RGBNatColourEnhncd_LowResolution.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/EUMETSAT_MSGIODC_RGBNatColourEnhncd_LowResolution.jpg"
        },
        "elektrol": {
          "source": "view-source:http://electro.ntsomz.ru/i/splash/20210529-2330.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/elektrol.jpg"
        },
        "insat_fd_ir": {
          "source": "https://mausam.imd.gov.in/Satellite/3Dglobe_ir1.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/insat-3Dglobe_ir1.jpg"
        },
        "insat_fd_vis": {
          "source": "https://mausam.imd.gov.in/Satellite/3Dglobe_vis.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/insat-3Dglobe_vis.jpg"
        },
        "insat_2d_ir": {
          "source": "https://mausam.imd.gov.in/Satellite/Converted/IR1.gif",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/insat-IR1.gif"
        },
        "insat_2d_vis": {
          "source": "https://mausam.imd.gov.in/Satellite/Converted/VIS.gif",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/insat-VIS.gif"
        },
        "sdo_0171": {
          "source": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0171.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/latest_1024_0171.jpg"
        },
        "sdo_0304": {
          "source": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0304.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/latest_1024_0304.jpg"
        },
        "sdo_HMID": {
          "source": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMID.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/latest_1024_HMID.jpg"
        },
        "sdo_HMIIC": {
          "source": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg",
          "datastore": "https://raw.githubusercontent.com/7h3rAm/datastore/master/latest_1024_HMIIC.jpg"
        },
      },
      "spacex": {},
    }
    self.datafile_path = "%s/datastore/astro.json" % (utils.expand_env(var="$PROJECTSPATH"))

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
    apodjson = utils.download_json("https://api.nasa.gov/planetary/apod?api_key=%s" % (self.apikey))
    self.data["apod"]["title"] = "%s (%s)" % (apodjson["title"], datetime.strptime(apodjson["date"], '%Y-%m-%d').strftime("%d/%b/%Y"))
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

  def eonet(self):
    self.data["eonet"] = {
      "date": datetime.now().astimezone(tz=None).strftime("%d/%b/%Y"),
      "events": [],
    }
    eonetjson = utils.download_json("https://eonet.sci.gsfc.nasa.gov/api/v3/events?status=open&days=30")
    for event in eonetjson["events"]:
      self.data["eonet"]["events"].append({
        "eid": event["id"],
        "name": event["title"],
        "url": event["link"],
        "location": "https://www.google.com/maps/dir/%s/@%s,%s,3z" % ("/".join([",".join([str(x["coordinates"][1]), str(x["coordinates"][0])]) for x in event["geometry"]]), event["geometry"][0]["coordinates"][1], event["geometry"][0]["coordinates"][0]),
        "category": [self.category_map[x["title"]] for x in event["categories"]],
        "source": [{"url": x["url"], "sid": x["id"]} for x in event["sources"]],
      })
    self.data["eonet"]["title"] = "%d events (%s)" % (len(self.data["eonet"]["events"]), self.data["eonet"]["date"])
    self.data["eonet"]["events"] = sorted(self.data["eonet"]["events"], key=lambda k: k["name"])
    self.data["eonet"]["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")

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
    self.data["spacex"]["launches"] = []
    launchesjson = utils.download_json("https://api.spacexdata.com/v4/launches")
    for launch in launchesjson:
      self.data["spacex"]["launches"].append({
        "name": launch["name"],
        "launch": datetime.fromtimestamp(launch["date_unix"], tz=timezone.utc).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z"),
        "upcoming": launch["upcoming"],
        "flight": launch["flight_number"],
        "description": launch["details"],
        "url": launch["links"]["webcast"],
      })
    self.data["spacex"]["launches"] = sorted(self.data["spacex"]["launches"], key=lambda k: k["flight"])

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

    # roadster
    # rockets
    # ships
    # starlink
    # history
    self.data["spacex"]["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")

  def update(self):
    self.data = utils.load_json(self.datafile_path)
    self.apod()
    self.neo()
    self.eonet()
    self.spacex()
    self.data["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.data, self.datafile_path)


if __name__ == "__main__":
  astro = Astro()
  astro.update()
