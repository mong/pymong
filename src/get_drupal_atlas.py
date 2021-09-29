#!/usr/bin/env python

import os
import re
import markdownify
from shutil import copy
import glob

atlas = {1:   ["no/barn", "Barnehelseatlas, 2011–2014", "2015-09-01", "9 2015", "2"],
         39:  ["no/dagkir", "Dagkirurgi,  2011–2013", "2015-01-01", "1 2015", "1"],
         49:  ["no/nyfodt", "Nyfødtmedisin, 2009–2014", "2016-12-01", "12 2016", "3"],
         90:  ["no/eldre", "Eldrehelseatlas, 2013–2015", "2017-06-01", "6 2017", "4"],
         117: ["en/dagkir", "Day surgery atlas, 2011–2013", "2017-09-01", "9 2017", "1"],
         118: ["en/barn", "Child Healthcare Atlas, 2011–2014", "2017-09-02", "9 2017", "2"],
         120: ["en/nyfodt", "Neonatal Atlas, 2009–2014", "2017-09-03", "9 2017", "3"],
         121: ["en/eldre", "Elderly Healthcare Atlas, 2013–2015", "2017-09-04", "9 2017", "4"],
         123: ["no/kols", "Kols, 2013–2015", "2017-10-01", "10 2017", "5"],
         131: ["en/kols", "COPD healthcare atlas, 2013–2015", "2018-03-01", "3 2018", "5"],
         138: ["no/ortopedi", "Ortopedi, 2012–2016", "2018-12-01", "12 2018", "7"],
         150: ["no/dagkir2", "Dagkirurgi, 2013–2017", "2018-11-01", "11 2018", "6"],
         154: ["en/dagkir2", "Day surgery atlas 2013–2017", "2018-12-01", "12 2018", "6"],
         155: ["no/gyn", "Gynekologi, 2015–2017", "2019-01-01", "1 2019", "8"],
         157: ["no/fodsel", "Fødselshjelp, 2015–2017", "2019-04-01", "4 2019", "9"],
         158: ["en/gyn", "Gynaecology, 2015–2017", "2019-05-01", "5 2019", "8"],
         178: ["en/fodsel", "Obstetrics 2015–2017", "2019-08-01", "8 2019", "9"],
         184: ["en/ortopedi", "Orthopaedic, 2012-2016", "2019-08-01", "8 2019", "7"],
         259: ["no/psyk", "Psykisk helsevern og TSB, 2014-2018", "2020-06-01", "6 2020", "10"],
         260: ["no/kvalitet", "Kvalitet, 2017–2019", "2021-01-01", "1 2021", "11"],
         274: ["en/psyk", "Mental Healthcare 2014-2018", "2021-01-01", "1 2021", "10"],
         279: ["en/kvalitet", "Healthcare Quality Atlas", "2021-08-01", "8 2021", "11"],
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
    # Get the main content from a hovedfunn page
    # Retun a md text string
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
                # Remove year range in the beginning of each section
                test_string = re.sub("<div class=\"field-item even\">\d*-\d*</div>", "", line)
                html_content = html_content + test_string
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
            hovedfunn.append("hovedfunn/" + line
            .replace("%C3%B8", "ø")
            .replace("%C3%A6", "æ")
            .replace("%C3%A5", "å")
            .replace("%C2%A0", "")
            .split(">")[4].split("/")[-1]
            .replace("\"", ""))
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

def create_md_heading(atlas_num):
    short_title = atlas[atlas_num][1]
    date = atlas[atlas_num][4]
    heading = '''---
num: {0}
mainTitle: {1}
shortTitle: {1}
---

## Innhold

'''.format(date, short_title)

    return(heading)
    

if not os.path.exists("output/md/no"):
    os.makedirs("output/md/no")
if not os.path.exists("output/md/en"):
    os.makedirs("output/md/en")

for details in glob.glob("atlas/*/details"):
    atlas_num = int(details.split("/")[1])
    atlas_name = atlas[atlas_num][0]

    img_path = "output/img/" + atlas_name
    md_name = "output/md/" + atlas_name + ".md"
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    detailsfile_content = get_file_content(details)
    entries = get_hovedfunn_order(detailsfile_content)
    hovedfunn_start = get_hovedfunn_start(detailsfile_content)

    md_heading = create_md_heading(atlas_num)

    md_file = open(md_name, "w")
    md_file.write(md_heading + hovedfunn_start)
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
