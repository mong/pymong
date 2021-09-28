#!/usr/bin/env python

import os
import re
import markdownify
from shutil import copy
import glob

atlas = {1: "no/barn",
         39: "no/dagkir",
         49: "no/nyfodt",
         90: "no/eldre",
         117: "en/dagkir",
         118: "en/barn",
         120: "en/nyfodt",
         121: "en/eldre",
         123: "no/kols",
         131: "en/kols",
         138: "no/ortopedi",
         150: "no/dagkir2",
         154: "en/dagkir2",
         155: "no/gyn",
         157: "no/fodsel",
         158: "en/gyn",
         178: "en/fodsel",
         184: "en/ortopedi",
         259: "no/psyk",
         260: "no/kvalitet",
         274: "en/psyk",
         279: "en/kvalitet"
         }

def map_hovedfunn_atlas(file_content):
  for line in file_content:
     if re.search("atlas-button atlas", line):
         # Get <num> out of the following line:
         # <a href="/atlas/<num>/details" class="atlas-button atlas">
         num = re.sub(r"\D", "", line)
         return(num)

def get_hovedfunn_title(file_content):
  for line in file_content:
     if re.search("page-title", line):
         # Get the line with id="page-title"
         return(line.strip())

def get_hovedfunn_content(file_content, img_path):
    html_content = ""
    collecting = False
    mod_img_path = img_path.replace("output/", "/helseatlas/")
    for line in file_content:
        # Start collecting text from line with BEGIN OUTPUT ...
        if re.search("BEGIN OUTPUT from 'sites/all/themes/custom/helseatlas/templates/ds-1col", line):
            collecting = True
        # Stop collecting text after line with END OUTPUT ...
        if re.search("END OUTPUT from 'sites/all/themes/custom/helseatlas/templates/ds-1col", line):
            collecting = False
        if collecting:
            if re.search("media-element file-default", line):
                # Replace image line
                filename = line.split()[1].split("/")[-1].replace("\"", "")
                html_content = html_content + "![" + filename.split(".")[-2] + "](" + mod_img_path + "/" + filename + ")"
            elif re.search("element-invisible", line):
                pass
            else:
                html_content = html_content + line
    markdown = markdownify.markdownify(html_content, heading_style = "ATK")

    return(markdown + "\n\n\n")

def get_figures(file_content, path):
    for line in file_content:
        if re.search("media-element file-default", line):
            filename = line.split()[1].split("//")[-1].replace("\"", "").replace("helseatlas.no/", "")
            copy(filename, path)

def get_file_content(filename):
    file = open(filename, "r")
    file_content = list(file.read().splitlines())
    file.close()
    return(file_content)

def get_hovedfunn_order(file_content):
    hovedfunn = []
    for line in file_content:
        if re.search("<a href=\"/hovedfunn", line):
            hovedfunn.append("hovedfunn/" + line.replace("%C3%B8", "ø").replace("%C3%A6", "æ").replace("%C3%A5", "å").replace("%C2%A0", "").split(">")[4].split("/")[-1].replace("\"", ""))
    return(hovedfunn)

def get_hovedfunn_start(file_content):
    count = 0
    return_string = ""
    for line in file_content:
        if count == 1:
            return_string = return_string + line + "\n"
            if re.search("</div>", line):
               count = count + 1
        if re.search("<div class=\"pane-content\">", line):
            count = count + 1
    
    return(markdownify.markdownify(return_string.strip(), heading_style = "ATK"))

if not os.path.exists("output/md/no"):
    os.makedirs("output/md/no")
if not os.path.exists("output/md/en"):
    os.makedirs("output/md/en")

for details in glob.glob("atlas/*/details"):
    atlas_num = int(details.split("/")[1])
    atlas_name = atlas[atlas_num]

    img_path = "output/img/" + atlas_name
    md_name = "output/md/" + atlas_name + ".md"
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    detailsfile_content = get_file_content(details)
    entries = get_hovedfunn_order(detailsfile_content)
    hovedfunn_start = get_hovedfunn_start(detailsfile_content)

    md_file = open(md_name, "w")
    md_file.write(hovedfunn_start)
    md_file.close()

    for entry in entries:
        try:
            file_content = get_file_content(entry)
            title_line = get_hovedfunn_title(file_content)
            hovedfunn = get_hovedfunn_content(file_content, img_path)
            md_file = open(md_name, "a")
            md_file.write(hovedfunn)
            md_file.close()

            get_figures(file_content, img_path)

        except:
            print("file " + entry + " not found!")

