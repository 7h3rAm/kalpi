#!/usr/bin/env python
# encoding: utf-8

import json

datadict = {
  "research": {
    "patents": {
      "2017": {
        "04": {
          "title": "Method and Apparatus for Intelligent Aggregation of Threat Behavior for the Detection of Malware",
          "description": "An attempt towards automated selection and grouping of aggregated threat behavior indicators depicting dominant malware characteristics.",
          "pretty_date": "Apr/2017",
          "patent_id": None,
          "patent_url": None
        }
      },
      "2014": {
        "12": {
          "title": "Using A Probability-based Model To Detect Random Content In A Protocol Field Associated With Network Traffic",
          "description": "A novel idea based upon stochastic processes derived machine learning model to identify and classify random/malicious content in network traffic.",
          "pretty_date": "Dec/2014",
          "patent_id": "US9680832B1",
          "patent_url": "https://patents.google.com/patent/US9680832B1/"
        },
        "09": {
          "title": "Deobfuscating Scripted Language For Network Intrusion Detection Using A Regular Expression Signature",
          "description": "An attempt towards normalizing obfuscated web scripts for network security appliances to consume and operate upon.",
          "pretty_date": "Sep/2014",
          "patent_id": "US9419991B2",
          "patent_url": "https://patents.google.com/patent/US9419991B2/"
        }
      }
    },
    "talks": [
      {
        "title": "Visual Network and File Forensics",
        "description": "This presentation aims to demo the effectiveness of visual tooling for malware and file-format forensics. It will cover structural analysis and visualization of malware and network artifacts. Various techniques like entropy/n-gram visualization, using compression-ratio and theoretical minsize to identify file type and packed content will be shown. Along with this, a framework that helps automate these tasks will be presented. Attendees with an interest in network monitoring, signature writing, malware analysis and forensics will find this presentation to be useful.",
        "events": [
          {
            "name": "DEF CON 25 Packet Hacking Village",
            "url": "https://www.wallofsheep.com/pages/dc25#atyagi",
            "pretty_date": "29/Jul/2017",
            "media": [
              {
                "name": "Help Net Security",
                "url": "https://www.helpnetsecurity.com/2017/09/12/rudra-file-forensics/"
              }
            ]
          },
        ]
      },
      {
        "title": "Rudra: The Destroyer of Evil",
        "description": "Rudra aims to provide a developer-friendly framework for exhaustive analysis of (PCAP and PE) files. It provides features to scan and generate reports that include file's structural properties, entropy visualization, compression ratio, theoretical minsize, etc. These details, alongwith file-format specific analysis information, help an analyst to understand the type of data embedded in a file and quickly decide if it deserves further investigation. It supports scanning PE files and can perform API scans, anti{debug, vm, sandbox} detection, packer detection, authenticode verification, alongwith Yara, shellcode, and regex detection upon them.",
        "events": [
          {
            "name": "DEF CON 24 Demo Labs",
            "url": "https://www.defcon.org/html/defcon-24/dc-24-demolabs.html#Tyagi",
            "pretty_date": "06/Aug/2016",
            "media": None,
          },
          {
            "name": "BlackHat USA 2016 Arsenal",
            "url": "http://www.blackhat.com/us-16/arsenal.html#ankur-tyagi",
            "pretty_date": "03/Aug/2016",
            "media": None,
          },
          {
            "name": "OWASP Pune Meeting May/July 2016",
            "url": "https://www.owasp.org/index.php/OWASP_Pune_Meeting_May/July_2016",
            "pretty_date": "28/Jul/2016",
            "media": None,
          },
          {
            "name": "BlackHat Asia 2016 Arsenal",
            "url": "https://www.blackhat.com/asia-16/arsenal.html#ankur-tyagi",
            "pretty_date": "31/Mar/2016",
            "media": None,
          },
          {
            "name": "BlackHat EU 2015 Arsenal",
            "url": "https://www.blackhat.com/eu-15/arsenal.html#ankur-tyagi",
            "pretty_date": "13/Nov/2015",
            "media": None,
          },
          {
            "name": "DEF CON 23 Demo Labs",
            "url": "https://www.defcon.org/html/defcon-23/dc-23-demo-labs-schedule.html#Tyagi",
            "pretty_date": "08/Aug/2015",
            "media": None,
          },
          {
            "name": "BlackHat USA 2015 Arsenal",
            "url": "https://www.blackhat.com/us-15/arsenal.html#ankur-tyagi",
            "pretty_date": "05/Aug/2015",
            "media": [
              {
                "name": "Help Net Security",
                "url": "https://www.helpnetsecurity.com/2015/09/04/rudra-framework-for-automated-inspection-of-network-capture-files/"
              }
            ]
          }
        ]
      },
      {
        "title": "Flowinspect: Network Inspection Tool on Steroids",
        "description": "Flowinspect is a tool developed specifically for network monitoring and inspection purposes. It takes network traffic as input and extracts layer 4 flows from it. These flows are then passed through an inspection engine that filters and extracts interesting network sessions. For flows that meet inspection criteria, the output mode dumps match statistics to either stdout or a file or both.",
        "events": [
          {
            "name": "BlackHat USA 2014 Arsenal",
            "url": "https://www.blackhat.com/us-14/arsenal.html#Tyagi",
            "pretty_date": "06/Aug/2014",
            "media": [
              {
                "name": "ToolsWatch",
                "url": "http://www.toolswatch.org/2014/08/black-hat-arsenal-usa-2014-wrap-up-day-1/"
              }
            ]
          },
          {
            "name": "Nullcon 2014",
            "url": "http://nullcon.net/website/goa-14/speakers/ankur-tyagi.php",
            "pretty_date": "14/Feb/2014",
            "media": [
              {
                "name": "Video",
                "url": "https://www.youtube.com/watch?v=E4YptOJzVXQ"
              }
            ]
          }
        ]
      }
    ],
    "projects": [
      {
        "title": "Rudra",
        "description": "A developer-friendly framework for exhaustive analysis of (PCAP and PE) files.",
        "url": "https://github.com/7h3rAm/rudra",
      },
      {
        "title": "Aayudh",
        "description": "The weaponary you need in your fight against evil.",
        "url": "https://github.com/7h3rAm/aayudh",
      },
      {
        "title": "Flowinspect",
        "description": "A Network Inspection Tool.",
        "url": "https://github.com/7h3rAm/flowinspect",
      },
      {
        "title": "Cryptopaymon",
        "description": "A bot to monitor crypto payments (donations and ransom).",
        "url": "https://github.com/7h3rAm/cryptopaymon",
      },
      {
        "title": "Kalpi",
        "description": "A static site generator in Python.",
        "url": "https://github.com/7h3rAm/kalpi",
      },
      {
        "title": "Cigma",
        "description": "A pure-Python file type identification library.",
        "url": "https://github.com/7h3rAm/cigma",
      },
      {
        "title": "PcapEdit",
        "description": "An Interactive Pcap Editor (based on Scapy).",
        "url": "https://github.com/7h3rAm/pcapedit",
      },
      {
        "title": "RE2DotGraph",
        "description": "Visualize a (non-POSIX) regular expression (uses pyFSA and dot).",
        "url": "https://github.com/7h3rAm/re2dotgraph",
      },
      {
        "title": "ARP-Secur",
        "description": "A proof-of-concept tool to safegaurd against ARP cache poisoning attacks.",
        "url": "https://github.com/7h3rAm/arp-secur",
      },
    ],
  },
  "aboutme": "<img alt=\"Ankur Tyagi\" class=\"aboutimg\" src=\"/static/images/ankur-tyagi-3120x4160-small.jpg\"><p>Hi, I'm Ankur Tyagi and this is my blog where I document ideas and list updates on several topics of interest that span <a href=\"/tags.html\">security</a>, <a href=\"/tags.html#code\">programming</a> and <a href=\"/tags.html#writeups\">problem solving</a> in general. It is completely <a href=\"https://github.com/7h3rAm/7h3rAm.github.io\" target=\"_blank\">opensource</a> and created using a minimal static site generator called <a href=\"https://github.com/7h3rAm/kalpi/\" target=\"_blank\">Kalpi</a>.</p><p>I've completed my graduate studies with a formal background in Computer Science and Software Systems. I started my professional journey with Vulnerability Assessment as the primary work domain but in a few years moved to Intrusion Prevention which eventually became my expertise. In an attempt to further improve infosec domain understanding, I moved to my present profile where I work as a Malware Researcher and get exposure to a wide array of concepts and ideas. At present, malware analysis, file-format decoding and network traffic inspection are my primary areas of interest.</p><p>I use <strong>7h3rAm</strong> (<a href=\"https://en.wikipedia.org/wiki/International_Phonetic_Alphabet\" target=\"_blank\">IPA</a>: <i>θˈɛɹam</i>) as my handle and you can find me using it on most social platforms. You can also reach me via <a href=\"mailto:echo 2s6eln@vncad.bzn | tr [62cbvsadnzel] [37acghilmorA]\">mail</a>, <a href=\"http://in.linkedin.com/in/ankurstyagi\" target=\"_blank\">linkedin</i></a>, <a href=\"https://github.com/7h3rAm\" target=\"_blank\">github</i></a>, <a href=\"https://twitter.com/7h3rAm\" target=\"_blank\">twitter</i></a> or <a href=\"https://keybase.io/7h3ram\" target=\"_blank\">keybase</a>.</p>"
}


def get():
  return datadict
