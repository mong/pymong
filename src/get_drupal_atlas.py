#!/usr/bin/env python

import os
import re
import markdownify
from shutil import copy

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

def get_hovedfunn_content(file_content):
    html_content = ""
    collecting = False
    for line in file_content:
        if re.search("BEGIN OUTPUT from 'sites/all/themes/custom/helseatlas/templates/ds-1col", line):
            collecting = True
        if re.search("END OUTPUT from 'sites/all/themes/custom/helseatlas/templates/ds-1col", line):
            collecting = False
        if collecting:
            html_content = html_content + line
    markdown = markdownify.markdownify(html_content, heading_style = "ATK")

    return(markdown)

def get_figures(file_content, path):
    for line in file_content:
        if re.search("media-element file-default", line):
            filename = line.split()[1].split("//")[-1].replace("\"", "").replace("helseatlas.no/", "")
            print(filename)
            copy(filename, path)




with os.scandir("hovedfunn") as it:
    for entry in it:
        if entry.is_file():
            file = open(entry.path, "r")
            file_content = list(file.read().splitlines())
            file.close()

            atlas_num = map_hovedfunn_atlas(file_content)
            print(atlas_num)

            img_path = "output/img/" + str(atlas_num)
            md_path = "output/md/" + str(atlas_num)

            if not os.path.exists(md_path):
                os.makedirs(md_path)
            if not os.path.exists(img_path):
                os.makedirs(img_path)

            title_line = get_hovedfunn_title(file_content)
#            print(title_line)
            hovedfunn = get_hovedfunn_content(file_content)

            get_figures(file_content, img_path)
#            print(markdown)
            quit()



