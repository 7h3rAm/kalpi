#!/usr/bin/env python3

from datetime import datetime, timezone
from pprint import pprint
import sparkline
import hashlib
import random
import time
import csv

import utils


class BTCTxsMon:
  def __init__(self):
    self.apikey = utils.expand_env(var="$NASAKEY")

    self.datastore_url = "https://raw.githubusercontent.com/7h3rAm/datastore/master"
    self.datastorepath = "%s/datastore" % (utils.expand_env(var="$PROJECTSPATH"))
    self.walletfilepath = "%s/datastore/btctxsmon.json" % (utils.expand_env(var="$PROJECTSPATH"))
    self.addressfilepath = "%s/toolbox/bootstrap/btctxsmon-addresses.json" % (utils.expand_env(var="$HOME"))
    self.address = utils.load_json(self.addressfilepath)
    self.wallet = {
      "last_update": None,
      "category": {
        "donation": {},
        "popular": {},
        "ransom": {},
      },
      "stats": {},
      "graph": {},
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

  def query_address(self, address):
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
    else:
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

  def load_from_csv(self):
    with open("%s/toolbox/bootstrap/btcpaymon.csv" % (utils.expand_env(var="$HOME"))) as csvfile:
      rows = csv.reader(csvfile, delimiter=",")
      header = next(rows)
      for row in rows:
        address = row[0]
        wallet = row[1].replace("_", " ")
        tag = row[2]
        category = row[3]
        source = row[4].split(";") if row[4] and row[4] != "" else None
        if category == "donation":
          self.address["category"]["donation"][address] = {
            "wallet": wallet,
            "tag": tag,
            "source": source,
          }
        elif category == "popular":
          self.address["category"]["popular"][address] = {
            "wallet": wallet,
            "tag": tag,
            "source": source,
          }
        if category == "ransom":
          self.address["category"]["ransom"][address] = {
            "wallet": wallet,
            "tag": tag,
            "source": source,
          }

  def update_donation(self, force=False):
    updated = []
    chunks = list(utils.chunkify(list(self.address["category"]["donation"].keys()), 50))
    for chunk in chunks:
      stats = utils.get_http("https://blockchain.info/multiaddr?active=%s" % ("|".join(chunk)))
      if "addresses" in stats:
        for entry in stats["addresses"]:
          if entry["address"] in self.address["category"]["donation"]:
            self.address["category"]["donation"][entry["address"]]["balance"] = entry["final_balance"]
            self.address["category"]["donation"][entry["address"]]["received"] = entry["total_received"]
            self.address["category"]["donation"][entry["address"]]["sent"] = entry["total_sent"]
            self.address["category"]["donation"][entry["address"]]["transaction"] = entry["n_tx"]
            if entry["n_tx"] != self.address["category"]["donation"][entry["address"]]["transaction"]:
              updated.append(entry["address"])
            elif force:
              updated.append(entry["address"])
    updated = list(set(updated))
    for address in updated:
      stats = self.query_address(address)
      if stats:
        self.address["category"]["donation"][address]["transaction"] = stats["transaction"]
        self.address["category"]["donation"][address]["received"] = stats["received"]
        self.address["category"]["donation"][address]["sent"] = stats["sent"]
        self.address["category"]["donation"][address]["balance"] = stats["balance"]
        self.address["category"]["donation"][address]["lasttxepoch"] = stats["lasttxepoch"]
        self.address["category"]["donation"][address]["lastseen"] = stats["lastseen"]

  def update_popular(self, force=False):
    updated = []
    chunks = list(utils.chunkify(list(self.address["category"]["popular"].keys()), 50))
    for chunk in chunks:
      stats = utils.get_http("https://blockchain.info/multiaddr?active=%s" % ("|".join(chunk)))
      if "addresses" in stats:
        for entry in stats["addresses"]:
          if entry["address"] in self.address["category"]["popular"]:
            self.address["category"]["popular"][entry["address"]]["balance"] = entry["final_balance"]
            self.address["category"]["popular"][entry["address"]]["received"] = entry["total_received"]
            self.address["category"]["popular"][entry["address"]]["sent"] = entry["total_sent"]
            self.address["category"]["popular"][entry["address"]]["transaction"] = entry["n_tx"]
            if entry["n_tx"] != self.address["category"]["popular"][entry["address"]]["transaction"]:
              updated.append(entry["address"])
            elif force:
              updated.append(entry["address"])
    updated = list(set(updated))
    for address in updated:
      stats = self.query_address(address)
      if stats:
        self.address["category"]["popular"][address]["transaction"] = stats["transaction"]
        self.address["category"]["popular"][address]["received"] = stats["received"]
        self.address["category"]["popular"][address]["sent"] = stats["sent"]
        self.address["category"]["popular"][address]["balance"] = stats["balance"]
        self.address["category"]["popular"][address]["lasttxepoch"] = stats["lasttxepoch"]
        self.address["category"]["popular"][address]["lastseen"] = stats["lastseen"]

  def update_ransom(self, force=False):
    updated = []
    chunks = list(utils.chunkify(list(self.address["category"]["ransom"].keys()), 50))
    for chunk in chunks:
      stats = utils.get_http("https://blockchain.info/multiaddr?active=%s" % ("|".join(chunk)))
      if "addresses" in stats:
        for entry in stats["addresses"]:
          if entry["address"] in self.address["category"]["ransom"]:
            self.address["category"]["ransom"][entry["address"]]["balance"] = entry["final_balance"]
            self.address["category"]["ransom"][entry["address"]]["received"] = entry["total_received"]
            self.address["category"]["ransom"][entry["address"]]["sent"] = entry["total_sent"]
            self.address["category"]["ransom"][entry["address"]]["transaction"] = entry["n_tx"]
            if entry["n_tx"] != self.address["category"]["ransom"][entry["address"]]["transaction"]:
              updated.append(entry["address"])
            elif force:
              updated.append(entry["address"])
    updated = list(set(updated))
    for address in updated:
      stats = self.query_address(address)
      if stats:
        self.address["category"]["ransom"][address]["transaction"] = stats["transaction"]
        self.address["category"]["ransom"][address]["received"] = stats["received"]
        self.address["category"]["ransom"][address]["sent"] = stats["sent"]
        self.address["category"]["ransom"][address]["balance"] = stats["balance"]
        self.address["category"]["ransom"][address]["lasttxepoch"] = stats["lasttxepoch"]
        self.address["category"]["ransom"][address]["lastseen"] = stats["lastseen"]

  def group_wallet(self):
    self.wallet["stats"] = {
      "count_address_donation": 0,
      "count_address_popular": 0,
      "count_address_ransom": 0,
      "count_wallet_donation": 0,
      "count_wallet_popular": 0,
      "count_wallet_ransom": 0,
      "count_address": 0,
      "count_wallet": 0,
      "count_received": 0,
      "count_sent": 0,
      "count_balance": 0,
      "count_txs": 0,
      "count_txs_donation": 0,
      "count_txs_popular": 0,
      "count_txs_ransom": 0,
      "count_balance_donation": 0,
      "count_balance_popular": 0,
      "count_balance_ransom": 0,
      "count_received_donation": 0,
      "count_received_popular": 0,
      "count_received_ransom": 0,
      "count_sent_donation": 0,
      "count_sent_popular": 0,
      "count_sent_ransom": 0,
    }

    for address in self.address["category"]["donation"]:
      if self.address["category"]["donation"][address]["wallet"] not in self.wallet["category"]["donation"]:
        self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]] = {
          "transaction": 0,
          "balance": 0,
          "received": 0,
          "sent": 0,
          "lastseen": None,
          "lasttxepoch": None,
          "address": 0,
        }
      self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["transaction"] += self.address["category"]["donation"][address]["transaction"]
      self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["balance"] += (self.address["category"]["donation"][address]["balance"] / (10**8))
      self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["received"] += (self.address["category"]["donation"][address]["received"] / (10**8))
      self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["sent"] += (self.address["category"]["donation"][address]["sent"] / (10**8))
      self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["address"] += 1
      if "lasttxepoch" not in self.address["category"]["donation"][address]:
        self.address["category"]["donation"][address]["lasttxepoch"] = None
      if self.address["category"]["donation"][address]["lasttxepoch"] and self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["lasttxepoch"]:
        self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["lasttxepoch"] = self.address["category"]["donation"][address]["lasttxepoch"] if self.address["category"]["donation"][address]["lasttxepoch"] > self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["lasttxepoch"] else self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["lasttxepoch"]
      elif self.address["category"]["donation"][address]["lasttxepoch"]:
        self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["lasttxepoch"] = self.address["category"]["donation"][address]["lasttxepoch"]
      self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["lastseen"] = time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["lasttxepoch"])) if self.wallet["category"]["donation"][self.address["category"]["donation"][address]["wallet"]]["lasttxepoch"] else ""
    for wallet in self.wallet["category"]["donation"]:
      self.wallet["stats"]["count_txs_donation"] += self.wallet["category"]["donation"][wallet]["transaction"]
      self.wallet["stats"]["count_balance_donation"] += self.wallet["category"]["donation"][wallet]["balance"]
      self.wallet["stats"]["count_received_donation"] += self.wallet["category"]["donation"][wallet]["received"]
      self.wallet["stats"]["count_sent_donation"] += self.wallet["category"]["donation"][wallet]["sent"]
      self.wallet["category"]["donation"][wallet]["sparkid"] = self.sparkify("%x%x%x%x%x" % (
        int(self.wallet["category"]["donation"][wallet]["address"] % 15),
        int(self.wallet["category"]["donation"][wallet]["transaction"] % 15),
        int(self.wallet["category"]["donation"][wallet]["received"] % 15),
        int(self.wallet["category"]["donation"][wallet]["sent"] % 15),
        int(self.wallet["category"]["donation"][wallet]["balance"] % 15),
      ), skiphashing=True)

    for address in self.address["category"]["popular"]:
      if self.address["category"]["popular"][address]["wallet"] not in self.wallet["category"]["popular"]:
        self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]] = {
          "transaction": 0,
          "balance": 0,
          "received": 0,
          "sent": 0,
          "lastseen": None,
          "lasttxepoch": None,
          "address": 0,
        }
      self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["transaction"] += self.address["category"]["popular"][address]["transaction"]
      self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["balance"] += (self.address["category"]["popular"][address]["balance"] / (10**8))
      self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["received"] += (self.address["category"]["popular"][address]["received"] / (10**8))
      self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["sent"] += (self.address["category"]["popular"][address]["sent"] / (10**8))
      self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["address"] += 1
      if "lasttxepoch" not in self.address["category"]["popular"][address]:
        self.address["category"]["popular"][address]["lasttxepoch"] = None
      if self.address["category"]["popular"][address]["lasttxepoch"] and self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["lasttxepoch"]:
        self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["lasttxepoch"] = self.address["category"]["popular"][address]["lasttxepoch"] if self.address["category"]["popular"][address]["lasttxepoch"] > self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["lasttxepoch"] else self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["lasttxepoch"]
      elif self.address["category"]["popular"][address]["lasttxepoch"]:
        self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["lasttxepoch"] = self.address["category"]["popular"][address]["lasttxepoch"]
      self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["lastseen"] = time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["lasttxepoch"])) if self.wallet["category"]["popular"][self.address["category"]["popular"][address]["wallet"]]["lasttxepoch"] else ""
    for wallet in self.wallet["category"]["popular"]:
      self.wallet["stats"]["count_txs_popular"] += self.wallet["category"]["popular"][wallet]["transaction"]
      self.wallet["stats"]["count_balance_popular"] += self.wallet["category"]["popular"][wallet]["balance"]
      self.wallet["stats"]["count_received_popular"] += self.wallet["category"]["popular"][wallet]["received"]
      self.wallet["stats"]["count_sent_popular"] += self.wallet["category"]["popular"][wallet]["sent"]
      self.wallet["category"]["popular"][wallet]["sparkid"] = self.sparkify("%x%x%x%x%x" % (
        int(self.wallet["category"]["popular"][wallet]["address"] % 15),
        int(self.wallet["category"]["popular"][wallet]["transaction"] % 15),
        int(self.wallet["category"]["popular"][wallet]["received"] % 15),
        int(self.wallet["category"]["popular"][wallet]["sent"] % 15),
        int(self.wallet["category"]["popular"][wallet]["balance"] % 15),
      ), skiphashing=True)

    for address in self.address["category"]["ransom"]:
      if self.address["category"]["ransom"][address]["wallet"] not in self.wallet["category"]["ransom"]:
        self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]] = {
          "transaction": 0,
          "balance": 0,
          "received": 0,
          "sent": 0,
          "lastseen": None,
          "lasttxepoch": None,
          "address": 0,
        }
      pprint(self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]])
      pprint(self.address["category"]["ransom"][address])
      self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["transaction"] += self.address["category"]["ransom"][address]["transaction"]
      self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["balance"] += (self.address["category"]["ransom"][address]["balance"] / (10**8))
      self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["received"] += (self.address["category"]["ransom"][address]["received"] / (10**8))
      self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["sent"] += (self.address["category"]["ransom"][address]["sent"] / (10**8))
      self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["address"] += 1
      if "lasttxepoch" not in self.address["category"]["ransom"][address]:
        self.address["category"]["ransom"][address]["lasttxepoch"] = None
      if self.address["category"]["ransom"][address]["lasttxepoch"] and self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["lasttxepoch"]:
        self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["lasttxepoch"] = self.address["category"]["ransom"][address]["lasttxepoch"] if self.address["category"]["ransom"][address]["lasttxepoch"] > self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["lasttxepoch"] else self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["lasttxepoch"]
      elif self.address["category"]["ransom"][address]["lasttxepoch"]:
        self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["lasttxepoch"] = self.address["category"]["ransom"][address]["lasttxepoch"]
      self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["lastseen"] = time.strftime("%d/%b/%Y @ %H:%M:%S %Z", time.localtime(self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["lasttxepoch"])) if self.wallet["category"]["ransom"][self.address["category"]["ransom"][address]["wallet"]]["lasttxepoch"] else ""
    for wallet in self.wallet["category"]["ransom"]:
      self.wallet["stats"]["count_txs_ransom"] += self.wallet["category"]["ransom"][wallet]["transaction"]
      self.wallet["stats"]["count_balance_ransom"] += self.wallet["category"]["ransom"][wallet]["balance"]
      self.wallet["stats"]["count_received_ransom"] += self.wallet["category"]["ransom"][wallet]["received"]
      self.wallet["stats"]["count_sent_ransom"] += self.wallet["category"]["ransom"][wallet]["sent"]
      self.wallet["category"]["ransom"][wallet]["sparkid"] = self.sparkify("%x%x%x%x%x" % (
        int(self.wallet["category"]["ransom"][wallet]["address"] % 15),
        int(self.wallet["category"]["ransom"][wallet]["transaction"] % 15),
        int(self.wallet["category"]["ransom"][wallet]["received"] % 15),
        int(self.wallet["category"]["ransom"][wallet]["sent"] % 15),
        int(self.wallet["category"]["ransom"][wallet]["balance"] % 15),
      ), skiphashing=True)

    self.wallet["stats"]["count_address_donation"] = len(self.address["category"]["donation"])
    self.wallet["stats"]["count_address_popular"] = len(self.address["category"]["popular"])
    self.wallet["stats"]["count_address_ransom"] = len(self.address["category"]["ransom"])
    self.wallet["stats"]["count_wallet_donation"] = len(self.wallet["category"]["donation"])
    self.wallet["stats"]["count_wallet_popular"] = len(self.wallet["category"]["popular"])
    self.wallet["stats"]["count_wallet_ransom"] = len(self.wallet["category"]["ransom"])
    self.wallet["stats"]["count_address"] = len(self.address["category"]["donation"]) + len(self.address["category"]["popular"]) + len(self.address["category"]["ransom"])
    self.wallet["stats"]["count_wallet"] = len(self.wallet["category"]["donation"]) + len(self.wallet["category"]["popular"]) + len(self.wallet["category"]["ransom"])
    self.wallet["stats"]["count_received"] = self.wallet["stats"]["count_received_donation"] + self.wallet["stats"]["count_received_popular"] + self.wallet["stats"]["count_received_ransom"]
    self.wallet["stats"]["count_sent"] = self.wallet["stats"]["count_sent_donation"] + self.wallet["stats"]["count_sent_popular"] + self.wallet["stats"]["count_sent_ransom"]
    self.wallet["stats"]["count_balance"] = self.wallet["stats"]["count_balance_donation"] + self.wallet["stats"]["count_balance_popular"] + self.wallet["stats"]["count_balance_ransom"]
    self.wallet["stats"]["count_txs"] = self.wallet["stats"]["count_txs_donation"] + self.wallet["stats"]["count_txs_popular"] + self.wallet["stats"]["count_txs_ransom"]

  def update(self):
    #self.load_from_csv()

    self.update_donation()
    self.update_popular()
    self.update_ransom()
    self.address["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.address, self.addressfilepath)

    self.group_wallet()
    self.wallet["last_update"] = datetime.now().astimezone(tz=None).strftime("%d/%b/%Y @ %H:%M:%S %Z")
    utils.save_json(self.wallet, self.walletfilepath)


if __name__ == "__main__":
  btctxsmon = BTCTxsMon()
  btctxsmon.update()
