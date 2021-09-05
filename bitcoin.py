#!/usr/bin/env python3

from datetime import datetime, timezone
from pprint import pprint
import sparkline
import hashlib
import random
import time
import csv

import utils

"""
http://172.16.1.48:3006/api/v1/blocks/tip/height
http://172.16.1.48:3006/api/v1/block-height/695148
http://172.16.1.48:3006/api/v1/block/000000000000000015dc777b3ff2611091336355d3f0ee9766a2cf3be8e4b1ce
http://172.16.1.48:3006/api/v1/block/000000000000000015dc777b3ff2611091336355d3f0ee9766a2cf3be8e4b1ce/txids
http://172.16.1.48:3006/api/v1/block/000000000000000015dc777b3ff2611091336355d3f0ee9766a2cf3be8e4b1ce/txs
http://172.16.1.48:3006/api/v1/blocks
http://172.16.1.48:3006/api/v1/difficulty-adjustment
http://172.16.1.48:3006/api/v1/fees/mempool-blocks
http://172.16.1.48:3006/api/v1/fees/recommended
http://172.16.1.48:3006/api/v1/mempool/txids
http://172.16.1.48:3006/api/v1/mempool/recent
http://172.16.1.48:3006/api/v1/tx/15e10745f15593a899cef391191bdd3d7c12412cc4696b7bcb669d0feadc8521
http://172.16.1.48:3006/api/v1/tx/15e10745f15593a899cef391191bdd3d7c12412cc4696b7bcb669d0feadc8521/status

https://api.coinpaprika.com/v1/tickers/btc-bitcoin
https://chain.so/api/v2/get_address_balance
https://chain.so/api/v2/get_tx_received

https://api.github.com/repos/7h3rAm/writeups
https://check.torproject.org/api/ip
https://ifconfig.me/all.json
http://ip-api.com/json/108.193.5.5
"""


class Bitcoin:
  def __init__(self):
    self.datastore_url = "https://raw.githubusercontent.com/7h3rAm/datastore/master"
    self.datastorepath = "%s/datastore" % (utils.expand_env(var="$PROJECTSPATH"))
    self.statsfilepath = "%s/datastore/bitcoin.json" % (utils.expand_env(var="$PROJECTSPATH"))
    self.addressesfilepath = "%s/toolbox/bootstrap/btctxsmon-addresses.json" % (utils.expand_env(var="$HOME"))
    self.addresses = utils.load_json(self.addressesfilepath)
    try:
      self.bitcoin = utils.load_json(self.statsfilepath)
    except:
      self.bitcoin = {
        "category": {
          "donation": {},
          "popular": {},
          "ransom": {}
        },
        "graph": {},
        "last_update": None,
        "nodes": [],
        "nodessummary": {},
        "stats": {
          "count_address": 0,
          "count_wallet": 0,
          "count_received": 0,
          "count_sent": 0,
          "count_balance": 0,
          "count_txs": 0,
          "donation": {
            "count_wallet": 0,
            "count_address": 0,
            "count_received": 0,
            "count_sent": 0,
            "count_balance": 0,
            "count_txs": 0,
          },
          "popular": {
            "count_wallet": 0,
            "count_address": 0,
            "count_received": 0,
            "count_sent": 0,
            "count_balance": 0,
            "count_txs": 0,
          },
          "ransom": {
            "count_wallet": 0,
            "count_address": 0,
            "count_received": 0,
            "count_sent": 0,
            "count_balance": 0,
            "count_txs": 0,
          },
        }
      }

  def sparkify(self, content, maxsize=10, unique=True, sparkmode=True, skiphashing=True):
    sparkid = content if skiphashing else hashlib.sha256(content.encode("utf-8")).hexdigest()
    spark = "".join(sparkline.sparkify([int(x, base=16) for x in sparkid]))
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
      sparkshort = "".join(['%s' % (ch if sparkmode else charmap[ch]) for ch in spark[:maxsize]])
    else:
      chars = ["▣", "►", "◐", "◧", "▤", "▼", "◑", "◨", "▥", "◀", "◒", "◩", "▦", "◆", "◕", "◪", "▧", "◈", "◢", "■", "▨", "◉", "◣", "▩", "◎", "◤", "▲", "●", "◥"]
      sparkshort = "".join(['%s' % (random.choice(chars)) for _ in range(len(sparkid[:maxsize]))])
    return sparkshort

  def load_from_csv(self):
    with open("%s/toolbox/bootstrap/btcpaymon.csv" % (utils.expand_env(var="$HOME"))) as csvfile:
      rows = csv.reader(csvfile, delimiter=",")
      header = next(rows)
      newaddresses = 0
      for row in rows:
        address = row[0]
        wallet = row[1].replace("_", " ")
        tag = row[2]
        category = row[3].lower()
        source = row[4].split(";") if row[4] and row[4] != "" else None
        if category not in ["donation", "popular", "ransom"]:
          continue
        if address not in self.addresses["category"][category]:
          newaddresses += 1
          self.addresses["category"][category][address] = {
            "wallet": wallet,
            "tag": tag,
            "source": source,
            "received": 0,
            "sent": 0,
            "balance": 0,
            "transaction": 0,
            "lastseen": None,
            "lasttxepoch": 0,
          }
    if newaddresses:
      print("added %d new addresses from %s file" % (newaddresses, "%s/toolbox/bootstrap/btcpaymon.csv" % (utils.expand_env(var="$HOME"))))

  def query_address(self, address, explorer="blockchaininfomulti"):
    if explorer == "chainso":
      content = utils.get_http("https://chain.so/api/v2/address/BTC/%s" % (address))
      if "data" in content and len(content["data"]["txs"]):
        return {
          "balance": int(float(content["data"]["balance"]) * (10**8)),
          "received": int(float(content["data"]["received_value"]) * (10**8)),
          "sent": int((float(content["data"]["received_value"])-float(content["data"]["balance"])) * (10**8)),
          "transaction": int(content["data"]["total_txs"]),
          "lasttxepoch": content["data"]["txs"][0]["time"],
          "lastseen": time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(content["data"]["txs"][0]["time"])),
        }
    elif explorer == "blockchaininfo":
      content = utils.get_http("https://blockchain.info/rawaddr/%s" % (address))
      if "n_tx" in content:
        return {
          "transaction": content["n_tx"],
          "received": content["total_received"],
          "sent": content["total_sent"],
          "balance": content["final_balance"],
          "lasttxepoch": content["txs"][0]["time"] if len(content["txs"]) else None,
          "lastseen": time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(content["txs"][0]["time"])) if len(content["txs"]) else "",
        }
    elif explorer == "blockchaininfomulti":
      content = utils.get_http("https://blockchain.info/multiaddr?active=%s" % (address))
      if "addresses" in content and content["addresses"][0]["address"] == address:
        return {
          "transaction": content["addresses"][0]["n_tx"],
          "received": content["addresses"][0]["total_received"],
          "sent": content["addresses"][0]["total_sent"],
          "balance": content["addresses"][0]["final_balance"],
          "lasttxepoch": content["txs"][0]["time"] if len(content["txs"]) else None,
          "lastseen": time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(content["txs"][0]["time"])) if len(content["txs"]) else "",
        }

  def update_category(self, category, force=False):
    updated, foundaddresses = [], []
    chunks = list(utils.chunkify(list(self.addresses["category"][category].keys()), 50))
    print("performing lookup for %d chunks of %d %s addresses" % (len(chunks), len(list(self.addresses["category"][category].keys())), category))
    for chunk in chunks:
      stats = utils.get_http("https://blockchain.info/multiaddr?active=%s" % ("|".join(chunk)))
      if "addresses" in stats:
        for entry in stats["addresses"]:
          foundaddresses.append(entry["address"])
          if force or entry["n_tx"] != self.addresses["category"][category][entry["address"]]["transaction"] or not self.addresses["category"][category][entry["address"]]["lastseen"]:
            # new txs since we last updated this address, update with new lasttx
            self.addresses["category"][category][entry["address"]]["transaction"] = entry["n_tx"]
            self.addresses["category"][category][entry["address"]]["balance"] = entry["final_balance"]
            self.addresses["category"][category][entry["address"]]["received"] = entry["total_received"]
            self.addresses["category"][category][entry["address"]]["sent"] = entry["total_sent"]
            self.addresses["category"][category][entry["address"]]["lastseen"] = None
            self.addresses["category"][category][entry["address"]]["lasttxepoch"] = None
            self.addresses["category"][category][entry["address"]]["retired"] = False
            updated.append(entry["address"])
    alladdresses = list(self.addresses["category"][category].keys())
    updated.extend(list(set(alladdresses)-set(foundaddresses)))
    updated = list(set(updated))
    print("updating stats for %d %s addresses" % (len(updated), category))
    for address in updated:
      stats = self.query_address(address)
      if stats:
        self.addresses["category"][category][address]["transaction"] = stats["transaction"]
        self.addresses["category"][category][address]["received"] = stats["received"]
        self.addresses["category"][category][address]["sent"] = stats["sent"]
        self.addresses["category"][category][address]["balance"] = stats["balance"]
        self.addresses["category"][category][address]["lasttxepoch"] = stats["lasttxepoch"]
        self.addresses["category"][category][address]["lastseen"] = stats["lastseen"]
        self.addresses["category"][category][address]["retired"] = False
      else:
        if self.addresses["category"][category][address]["transaction"] == 0:
          # this address has no txs and we could not find stats via 2 public apis; mark it retired
          self.addresses["category"][category][address]["retired"] = True
        else:
          self.addresses["category"][category][address]["retired"] = False

  def group_wallet(self):
    self.bitcoin["category"]["donation"] = {}
    self.bitcoin["category"]["popular"] = {}
    self.bitcoin["category"]["ransom"] = {}
    self.bitcoin["stats"] = {
      "count_address": 0,
      "count_wallet": 0,
      "count_received": 0,
      "count_sent": 0,
      "count_balance": 0,
      "count_txs": 0,
      "donation": {
        "count_wallet": 0,
        "count_address": 0,
        "count_received": 0,
        "count_sent": 0,
        "count_balance": 0,
        "count_txs": 0,
      },
      "popular": {
        "count_wallet": 0,
        "count_address": 0,
        "count_received": 0,
        "count_sent": 0,
        "count_balance": 0,
        "count_txs": 0,
      },
      "ransom": {
        "count_wallet": 0,
        "count_address": 0,
        "count_received": 0,
        "count_sent": 0,
        "count_balance": 0,
        "count_txs": 0,
      },
    }

    for category in ["donation", "popular", "ransom"]:
      print("grouping %d addresses for %s category" % (len(self.addresses["category"][category]), category))
      for address in self.addresses["category"][category]:
        if self.addresses["category"][category][address]["retired"]:
          continue
        wallet = self.addresses["category"][category][address]["wallet"]
        if wallet not in self.bitcoin["category"][category]:
          self.bitcoin["category"][category][wallet] = {
            "addresses": 0,
            "received": 0,
            "sent": 0,
            "balance": 0,
            "transaction": 0,
            "lasttxepoch": None,
            "lastseen": None,
          }
        self.bitcoin["category"][category][wallet]["addresses"] += 1
        self.bitcoin["category"][category][wallet]["received"] += (self.addresses["category"][category][address]["received"] / (10**8))
        self.bitcoin["category"][category][wallet]["sent"] += (self.addresses["category"][category][address]["sent"] / (10**8))
        self.bitcoin["category"][category][wallet]["balance"] += (self.addresses["category"][category][address]["balance"] / (10**8))
        self.bitcoin["category"][category][wallet]["transaction"] += self.addresses["category"][category][address]["transaction"]

        if self.addresses["category"][category][address]["lasttxepoch"]:
          if not self.bitcoin["category"][category][wallet]["lasttxepoch"]:
            self.bitcoin["category"][category][wallet]["lasttxepoch"] = self.addresses["category"][category][address]["lasttxepoch"]
            self.bitcoin["category"][category][wallet]["lastseen"] = time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(self.bitcoin["category"][category][wallet]["lasttxepoch"]))
          else:
            if self.addresses["category"][category][address]["lasttxepoch"] > self.bitcoin["category"][category][wallet]["lasttxepoch"]:
              self.bitcoin["category"][category][wallet]["lasttxepoch"] = self.addresses["category"][category][address]["lasttxepoch"]
              self.bitcoin["category"][category][wallet]["lastseen"] = time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(self.bitcoin["category"][category][wallet]["lasttxepoch"]))

      for wallet in self.bitcoin["category"][category]:
        self.bitcoin["stats"][category]["count_received"] += self.bitcoin["category"][category][wallet]["received"]
        self.bitcoin["stats"][category]["count_sent"] += self.bitcoin["category"][category][wallet]["sent"]
        self.bitcoin["stats"][category]["count_txs"] += self.bitcoin["category"][category][wallet]["transaction"]
        self.bitcoin["stats"][category]["count_balance"] += self.bitcoin["category"][category][wallet]["balance"]
        self.bitcoin["stats"][category]["count_address"] = len(self.addresses["category"][category])
        self.bitcoin["stats"][category]["count_wallet"] = len(self.bitcoin["category"][category])
        self.bitcoin["category"][category][wallet]["sparkid"] = self.sparkify("%x%x%x%x%x" % (
          int(self.bitcoin["category"][category][wallet]["addresses"] % 15),
          int(self.bitcoin["category"][category][wallet]["transaction"] % 15),
          int(self.bitcoin["category"][category][wallet]["received"] % 15),
          int(self.bitcoin["category"][category][wallet]["sent"] % 15),
          int(self.bitcoin["category"][category][wallet]["balance"] % 15),
        ), skiphashing=True)

    self.bitcoin["stats"]["count_address"] = len(self.addresses["category"]["donation"]) + len(self.addresses["category"]["popular"]) + len(self.addresses["category"]["ransom"])
    self.bitcoin["stats"]["count_wallet"] = len(self.bitcoin["category"]["donation"]) + len(self.bitcoin["category"]["popular"]) + len(self.bitcoin["category"]["ransom"])
    self.bitcoin["stats"]["count_received"] = self.bitcoin["stats"]["donation"]["count_received"] + self.bitcoin["stats"]["popular"]["count_received"] + self.bitcoin["stats"]["ransom"]["count_received"]
    self.bitcoin["stats"]["count_sent"] = self.bitcoin["stats"]["donation"]["count_sent"] + self.bitcoin["stats"]["popular"]["count_sent"] + self.bitcoin["stats"]["ransom"]["count_sent"]
    self.bitcoin["stats"]["count_balance"] = self.bitcoin["stats"]["donation"]["count_balance"] + self.bitcoin["stats"]["popular"]["count_balance"] + self.bitcoin["stats"]["ransom"]["count_balance"]
    self.bitcoin["stats"]["count_txs"] = self.bitcoin["stats"]["donation"]["count_txs"] + self.bitcoin["stats"]["popular"]["count_txs"] + self.bitcoin["stats"]["ransom"]["count_txs"]

  def update(self, skipupdate=False):
    self.load_from_csv()
    self.get_bitnodes()
    self.bitcoin["last_update_epoch"] = datetime.now().astimezone(tz=None)
    self.bitcoin["last_update"] = self.bitcoin["last_update_epoch"].strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.bitcoin, self.statsfilepath)
    if not skipupdate:
      for category in ["donation", "popular", "ransom"]:
        self.update_category(category)
        self.addresses["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
        utils.save_json(self.addresses, self.addressesfilepath)
    self.group_wallet()
    self.bitcoin["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.bitcoin, self.statsfilepath)

  def get_bitnodes(self):
    nodes = utils.get_http("https://bitnodes.io/api/v1/snapshots/latest/")
    if nodes:
      self.bitcoin["nodes"] = []
      self.bitcoin["nodessummary"] = {
        "asn": {},
        "country": {},
        "useragent": {},
        "timezone": {},
      }
      print("adding stats for %d bitcoin nodes" % len(nodes["nodes"]))
      for node in nodes["nodes"]:
        asn = nodes["nodes"][node][11] if nodes["nodes"][node][11] else "Unknown"
        city = nodes["nodes"][node][6] if nodes["nodes"][node][6] else "Unknown"
        connectedsince = nodes["nodes"][node][2] if nodes["nodes"][node][2] else "Unknown"
        connectedsincehuman = time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(nodes["nodes"][node][2])) if nodes["nodes"][node][2] else "Unknown"
        country = nodes["nodes"][node][7] if nodes["nodes"][node][7] else "Unknown"
        height = nodes["nodes"][node][4] if nodes["nodes"][node][4] else "Unknown"
        hostname = nodes["nodes"][node][5] if nodes["nodes"][node][5] else "Unknown"
        ipurl = node
        latitude = nodes["nodes"][node][8] if nodes["nodes"][node][8] else "Unknown"
        longitude = nodes["nodes"][node][9] if nodes["nodes"][node][9] else "Unknown"
        orgname = nodes["nodes"][node][12] if nodes["nodes"][node][12] else "Unknown"
        protoversion = nodes["nodes"][node][0] if nodes["nodes"][node][0] else "Unknown"
        services = nodes["nodes"][node][3] if nodes["nodes"][node][3] else "Unknown"
        timezone = nodes["nodes"][node][10] if nodes["nodes"][node][10] else "Unknown"
        useragent = nodes["nodes"][node][1] if nodes["nodes"][node][1] else "Unknown"
        servicesflags = []
        if services & 0: servicesflags.append("NODE_NONE")
        if services & (1 << 0): servicesflags.append("NODE_NETWORK")
        if services & (1 << 1): servicesflags.append("NODE_GETUTXO")
        if services & (1 << 2): servicesflags.append("NODE_BLOOM")
        if services & (1 << 3): servicesflags.append("NODE_WITNESS")
        if services & (1 << 4): servicesflags.append("NODE_XTHIN")
        if services & (1 << 10): servicesflags.append("NODE_NETWORK_LIMITED")
        self.bitcoin["nodes"].append({
          "asn": asn,
          "city": city,
          "connectedsince": connectedsince,
          "connectedsincehuman": connectedsincehuman,
          "country": country,
          "height": height,
          "hostname": hostname,
          "ipurl": ipurl,
          "latitude": latitude,
          "longitude": longitude,
          "orgname": orgname,
          "protoversion": protoversion,
          "services": services,
          "servicesflags": servicesflags,
          "timezone": timezone,
          "useragent": useragent,
        })
        if asn not in self.bitcoin["nodessummary"]["asn"]:
          self.bitcoin["nodessummary"]["asn"][asn] = 1
        else:
          self.bitcoin["nodessummary"]["asn"][asn] += 1
        if country not in self.bitcoin["nodessummary"]["country"]:
          self.bitcoin["nodessummary"]["country"][country] = 1
        else:
          self.bitcoin["nodessummary"]["country"][country] += 1
        if timezone not in self.bitcoin["nodessummary"]["timezone"]:
          self.bitcoin["nodessummary"]["timezone"][timezone] = 1
        else:
          self.bitcoin["nodessummary"]["timezone"][timezone] += 1
        if useragent not in self.bitcoin["nodessummary"]["useragent"]:
          self.bitcoin["nodessummary"]["useragent"][useragent] = 1
        else:
          self.bitcoin["nodessummary"]["useragent"][useragent] += 1
    self.bitcoin["stats"]["count_nodes"] = len(self.bitcoin["nodes"])
    self.bitcoin["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.bitcoin, self.statsfilepath)

  def group_and_update(self, categories=["donation", "popular", "ransom"]):
    with open("%s/toolbox/bootstrap/btcpaymon.csv" % (utils.expand_env(var="$HOME"))) as csvfile:
      self.addresses = {
        "category": {
          "donation": {},
          "popular": {},
          "ransom": {},
        }
      }
      rows = csv.reader(csvfile, delimiter=",")
      header = next(rows)
      for row in rows:
        address = row[0]
        wallet = row[1].replace("_", " ")
        tag = row[2]
        category = row[3].lower()
        source = row[4].split(";") if row[4] and row[4] != "" else None
        if category in ["donation", "popular", "ransom"] and address not in self.addresses["category"][category]:
          self.addresses["category"][category][address] = {
            "wallet": wallet,
            "tag": tag,
            "source": source,
          }

    for category in categories:
      self.bitcoin["category"][category] = {}
      self.bitcoin["stats"][category]["count_wallet"] = 0
      self.bitcoin["stats"][category]["count_address"] = 0
      self.bitcoin["stats"][category]["count_received"] = 0
      self.bitcoin["stats"][category]["count_sent"] = 0
      self.bitcoin["stats"][category]["count_balance"] = 0
      self.bitcoin["stats"][category]["count_txs"] = 0
      print("grouping %d addresses in %s category" % (len(self.addresses["category"][category]), category))
      for address in self.addresses["category"][category]:
        wallet = self.addresses["category"][category][address]["wallet"]
        if wallet not in self.bitcoin["category"][category]:
          self.bitcoin["category"][category][wallet] = {
            "addresses": [address],
            "addrstats": [],
            "received": 0,
            "sent": 0,
            "balance": 0,
            "txcount": 0,
            "lasttx": {
              "epoch": None,
              "epochhuman": None,
              "hash": None,
              "block": None,
              "summary": None,
            },
            "sparkid": None,
          }
        else:
          self.bitcoin["category"][category][wallet]["addresses"].append(address)

    for category in categories:
      print("updating %d wallets in %s category" % (len(self.bitcoin["category"][category]), category))
      for wallet in self.bitcoin["category"][category]:
        try:
          # https://www.blockchain.com/api/blockchain_api
          stats = utils.get_http("https://blockchain.info/multiaddr?active=%s" % ("|".join(self.bitcoin["category"][category][wallet]["addresses"])))
        except:
          stats= None
        if stats and "addresses" in stats:
          self.bitcoin["category"][category][wallet]["addrstats"] = []
          for entry in stats["addresses"]:
            self.bitcoin["category"][category][wallet]["addrstats"].append({
              "address": entry["address"],
              "received": entry["total_received"],
              "sent": entry["total_sent"],
              "balance": entry["final_balance"],
              "txcount": entry["n_tx"],
            })
            self.bitcoin["category"][category][wallet]["received"] += entry["total_received"]
            self.bitcoin["category"][category][wallet]["sent"] += entry["total_sent"]
            self.bitcoin["category"][category][wallet]["balance"] += entry["final_balance"]
            self.bitcoin["category"][category][wallet]["txcount"] += entry["n_tx"]
          if len(stats["txs"]):
            self.bitcoin["category"][category][wallet]["lasttx"]["epoch"] = stats["txs"][0]["time"]
            self.bitcoin["category"][category][wallet]["lasttx"]["epochhuman"] = time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(stats["txs"][0]["time"]))
            self.bitcoin["category"][category][wallet]["lasttx"]["hash"] = stats["txs"][0]["hash"]
            self.bitcoin["category"][category][wallet]["lasttx"]["block"] = stats["txs"][0]["block_height"]
            self.bitcoin["category"][category][wallet]["lasttx"]["summary"] = stats["txs"][0]["result"]

          self.bitcoin["category"][category][wallet]["sparkid"] = self.sparkify("%x%x%x%x%x" % (
            int(len(self.bitcoin["category"][category][wallet]["addresses"]) % 15),
            int(self.bitcoin["category"][category][wallet]["txcount"] % 15),
            int(self.bitcoin["category"][category][wallet]["received"] % 15),
            int(self.bitcoin["category"][category][wallet]["sent"] % 15),
            int(self.bitcoin["category"][category][wallet]["balance"] % 15),
          ), skiphashing=True)

        self.bitcoin["stats"][category]["count_wallet"] = len(self.bitcoin["category"][category])
        self.bitcoin["stats"][category]["count_address"] += len(self.bitcoin["category"][category][wallet]["addresses"])
        self.bitcoin["stats"][category]["count_received"] += self.bitcoin["category"][category][wallet]["received"]
        self.bitcoin["stats"][category]["count_sent"] += self.bitcoin["category"][category][wallet]["sent"]
        self.bitcoin["stats"][category]["count_balance"] += self.bitcoin["category"][category][wallet]["balance"]
        self.bitcoin["stats"][category]["count_txs"] += self.bitcoin["category"][category][wallet]["txcount"]

        self.bitcoin["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
        utils.save_json(self.bitcoin, self.statsfilepath)

    self.bitcoin["stats"]["count_wallet"] = self.bitcoin["stats"]["donation"]["count_wallet"] + self.bitcoin["stats"]["popular"]["count_wallet"] + self.bitcoin["stats"]["ransom"]["count_wallet"]
    self.bitcoin["stats"]["count_address"] = self.bitcoin["stats"]["donation"]["count_address"] + self.bitcoin["stats"]["popular"]["count_address"] + self.bitcoin["stats"]["ransom"]["count_address"]
    self.bitcoin["stats"]["count_received"] = self.bitcoin["stats"]["donation"]["count_received"] + self.bitcoin["stats"]["popular"]["count_received"] + self.bitcoin["stats"]["ransom"]["count_received"]
    self.bitcoin["stats"]["count_sent"] = self.bitcoin["stats"]["donation"]["count_sent"] + self.bitcoin["stats"]["popular"]["count_sent"] + self.bitcoin["stats"]["ransom"]["count_sent"]
    self.bitcoin["stats"]["count_balance"] = self.bitcoin["stats"]["donation"]["count_balance"] + self.bitcoin["stats"]["popular"]["count_balance"] + self.bitcoin["stats"]["ransom"]["count_balance"]
    self.bitcoin["stats"]["count_txs"] = self.bitcoin["stats"]["donation"]["count_txs"] + self.bitcoin["stats"]["popular"]["count_txs"] + self.bitcoin["stats"]["ransom"]["count_txs"]

    self.bitcoin["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.bitcoin, self.statsfilepath)

  def wallet_graph(self):
    def sat2btc(sat):
      return sat/10**8

    def sat2size(sat):
      sizemap = {
        1: 10,
        10: 15,
        100: 20,
        1000: 25,
        10000: 30,
        100000: 35,
        1000000: 40,
        10000000: 45,
        100000000: 50,
      }
      btc = sat2btc(sat)
      for maxbtc in sizemap:
        if btc <= maxbtc:
          return sizemap[maxbtc]

    grouplimits = {
      "₿1":     {"min": 0, "max": 1},
      "₿10":    {"min": 1, "max": 10},
      "₿100":   {"min": 10, "max": 100},
      "₿1k":    {"min": 100, "max": 1000},
      "₿10k":   {"min": 1000, "max": 10000},
      "₿100k":  {"min": 10000, "max": 100000},
      "₿1m":    {"min": 100000, "max": 1000000},
      "₿10m":   {"min": 1000000, "max": 10000000},
      "₿100m":   {"min": 10000000, "max": 100000000},
    }

    groupingcriteria = "received"
    defaultnodesize = 20
    defaultfillcolor = "#dedede"
    rootfillcolor = "#c3daf7"
    edgecolor = "#dddddd"
    nodecolor = "#f6f6f6"
    categoryfillcolors = {
      "donation": "#d7ecc9",
      "popular": "#fed9b5",
      "ransom": "#fbbfc5",
    }

    self.bitcoin["graph"] = {
      "grouped": {
        "inlabel": self.bitcoin["stats"]["count_wallet"],
        "outlabel": "💼 Wallets",
        "size": defaultnodesize,
        "edgecolor": edgecolor,
        "fillcolor": rootfillcolor,
        "tooltip": "", #"₿%.8f/₿%.8f/₿%.8f" % (sat2btc(self.bitcoin["stats"]["count_received"]), sat2btc(self.bitcoin["stats"]["count_sent"]), sat2btc(self.bitcoin["stats"]["count_balance"])),
        "donation": {
          "inlabel": None,
          "outlabel": "🙏 Donation",
          "size": defaultnodesize,
          "edgecolor": edgecolor,
          "fillcolor": categoryfillcolors["donation"],
          "tooltip": None,
          "₿1": [],
          "₿10": [],
          "₿100": [],
          "₿1k": [],
          "₿10k": [],
          "₿100k": [],
          "₿1m": [],
          "₿10m": [],
          "children": []
        },
        "popular": {
          "inlabel": None,
          "outlabel": "🔥 Popular",
          "size": defaultnodesize,
          "edgecolor": edgecolor,
          "fillcolor": categoryfillcolors["popular"],
          "tooltip": None,
          "₿1": [],
          "₿10": [],
          "₿100": [],
          "₿1k": [],
          "₿10k": [],
          "₿100k": [],
          "₿1m": [],
          "₿10m": [],
          "children": []
        },
        "ransom": {
          "inlabel": None,
          "outlabel": "👾 Ransom",
          "size": defaultnodesize,
          "edgecolor": edgecolor,
          "fillcolor": categoryfillcolors["ransom"],
          "tooltip": None,
          "₿1": [],
          "₿10": [],
          "₿100": [],
          "₿1k": [],
          "₿10k": [],
          "₿100k": [],
          "₿1m": [],
          "₿10m": [],
          "children": []
        },
        "children": []
      }
    }

    for category in ["donation", "popular", "ransom"]:
      print("gathering stats for %d wallets in %s category" % (len(self.bitcoin["category"][category]), category))
      for wallet in self.bitcoin["category"][category]:
        for fundgroup in grouplimits:
          if sat2btc(self.bitcoin["category"][category][wallet][groupingcriteria]) > grouplimits[fundgroup]["min"] and sat2btc(self.bitcoin["category"][category][wallet][groupingcriteria]) <= grouplimits[fundgroup]["max"]:
            self.bitcoin["graph"]["grouped"][category][fundgroup].append({
              "inlabel": "",
              "outlabel": wallet,
              "size": defaultnodesize, #sat2size(self.bitcoin["category"][category][wallet][groupingcriteria]),
              "edgecolor": edgecolor,
              "nodecolor": nodecolor,
              "fillcolor": categoryfillcolors[category] if self.bitcoin["category"][category][wallet]["balance"] > 0 else defaultfillcolor,
              "tooltip": "₿%.8f/₿%.8f/₿%.8f" % (sat2btc(self.bitcoin["category"][category][wallet]["received"]), sat2btc(self.bitcoin["category"][category][wallet]["sent"]), sat2btc(self.bitcoin["category"][category][wallet]["balance"])),
              "lastactivity": self.bitcoin["category"][category][wallet]["lasttx"]["epochhuman"],
              "children": [],
            })
      print("grouping wallets using criteria '%s'" % groupingcriteria)
      for fundgroup in grouplimits:
        if fundgroup in self.bitcoin["graph"]["grouped"][category]:
          if len(self.bitcoin["graph"]["grouped"][category][fundgroup]):
            self.bitcoin["graph"]["grouped"][category]["children"].append({
              "inlabel": len(self.bitcoin["graph"]["grouped"][category][fundgroup]),
              "outlabel": "<=%s" % (fundgroup),
              "size": defaultnodesize,
              "edgecolor": edgecolor,
              "nodecolor": nodecolor,
              "fillcolor": categoryfillcolors[category],
              "tooltip": "",
              "children": self.bitcoin["graph"]["grouped"][category][fundgroup],
            })
          del self.bitcoin["graph"]["grouped"][category][fundgroup]

    self.bitcoin["graph"]["grouped"]["children"].append({
      "inlabel": self.bitcoin["stats"]["donation"]["count_wallet"],
      "outlabel": "🙏 Donation",
      "size": defaultnodesize,
      "edgecolor": edgecolor,
      "nodecolor": nodecolor,
      "fillcolor": categoryfillcolors["donation"],
      "tooltip": "", #"₿%.8f/₿%.8f/₿%.8f" % (sat2btc(self.bitcoin["stats"]["donation"]["count_received"]), sat2btc(self.bitcoin["stats"]["donation"]["count_sent"]), sat2btc(self.bitcoin["stats"]["donation"]["count_balance"])),
      "children": self.bitcoin["graph"]["grouped"]["donation"]["children"],
    })
    del self.bitcoin["graph"]["grouped"]["donation"]
    self.bitcoin["graph"]["grouped"]["children"].append({
      "inlabel": self.bitcoin["stats"]["popular"]["count_wallet"],
      "outlabel": "🔥 Popular",
      "size": defaultnodesize,
      "edgecolor": edgecolor,
      "nodecolor": nodecolor,
      "fillcolor": categoryfillcolors["popular"],
      "tooltip": "", #"₿%.8f/₿%.8f/₿%.8f" % (sat2btc(self.bitcoin["stats"]["popular"]["count_received"]), sat2btc(self.bitcoin["stats"]["popular"]["count_sent"]), sat2btc(self.bitcoin["stats"]["popular"]["count_balance"])),
      "children": self.bitcoin["graph"]["grouped"]["popular"]["children"],
    })
    del self.bitcoin["graph"]["grouped"]["popular"]
    self.bitcoin["graph"]["grouped"]["children"].append({
      "inlabel": self.bitcoin["stats"]["ransom"]["count_wallet"],
      "outlabel": "👾 Ransom",
      "size": defaultnodesize,
      "edgecolor": edgecolor,
      "nodecolor": nodecolor,
      "fillcolor": categoryfillcolors["ransom"],
      "tooltip": "", #"₿%.8f/₿%.8f/₿%.8f" % (sat2btc(self.bitcoin["stats"]["ransom"]["count_received"]), sat2btc(self.bitcoin["stats"]["ransom"]["count_sent"]), sat2btc(self.bitcoin["stats"]["ransom"]["count_balance"])),
      "children": self.bitcoin["graph"]["grouped"]["ransom"]["children"],
    })
    del self.bitcoin["graph"]["grouped"]["ransom"]

    self.bitcoin["last_update_epoch"] = datetime.now().timestamp(); self.bitcoin["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.bitcoin, self.statsfilepath)


if __name__ == "__main__":
  bitcoin = Bitcoin()
  bitcoin.group_and_update()
  bitcoin.wallet_graph()
  bitcoin.get_bitnodes()
