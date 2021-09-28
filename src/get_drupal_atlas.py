#!/usr/bin/env python

import os
import re
import markdownify
from shutil import copy
import glob

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
                html_content = html_content + "![" + filename.split(".")[-2] + "](" + img_path + "/" + filename + ")"
#            elif re.search("Nedlastbar PDF", line):
#                pass
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

for details in glob.glob("atlas/*/details"):

    detailsfile_content = get_file_content(details)
    entries = get_hovedfunn_order(detailsfile_content)

    for entry in entries:
        try:
            file_content = get_file_content(entry)
            atlas_num = map_hovedfunn_atlas(file_content)

            img_path = "output/img/" + str(atlas_num)
            md_path = "output/md/" + str(atlas_num)

            if not os.path.exists(md_path):
                os.makedirs(md_path)
            if not os.path.exists(img_path):
                os.makedirs(img_path)

            title_line = get_hovedfunn_title(file_content)
            hovedfunn = get_hovedfunn_content(file_content, img_path)
            md_file = open(md_path + "/hovedfunn.md", "a")
            md_file.write(hovedfunn)
            md_file.close()

            get_figures(file_content, img_path)

        except:
            print("file " + entry + " not found!")

