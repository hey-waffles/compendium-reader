#! /usr/bin/python3

from __future__ import print_function
import pickle
import io
import os.path
import re
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from get_credentials import fetch_credentials

def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = fetch_credentials()
   
  service = build('drive', 'v3', credentials=creds)

  # Call the Drive v3 API
  results = service.files().list(
    pageSize=10,
    q="name contains 'sea compendium'",
    fields="nextPageToken, files(id, name)"
  ).execute()
  items = results.get('files', [])

  if not items:
    print('No files found.')
  else:
    print('Files:')
    for item in items:
      print(u'{0} ({1})'.format(item['name'], item['id']))
      if (os.path.exists(item['name'] + ".html")):
        with open(item['name'] + ".html", 'r') as f:
          htmlFile = f.read()
      else:
        htmlFile = skim_file(service, item['id'])
        with open(item['name'] + ".html", 'w') as f:
          f.write(htmlFile)

      parsedYamlFile = parse_html(htmlFile)

      f = open(item['name'] + ".yaml", "w")
      f.write(parsedYamlFile)
      f.close()

      # exit()

def parse_html(html):
  # Remove head
  parsedHTML = re.sub("\<(head|div|sup)[\s\S]+?(head|div|sup)\>\n", "", html)

  # Remove surrounding tags
  parsedHTML = re.sub("<[\/]?(html|body|span|hr).*?>\n", "", parsedHTML)

  # Remove styling and ids
  parsedHTML = re.sub("\s?(style|id|class)=\".+?\"", "", parsedHTML)

  # Deal with ul and li
  parsedHTML = re.sub("</?ul[/s/S]*?>\n?", "", parsedHTML)
  parsedHTML = re.sub("<li[/s/S]*?>\n", "<p> * ", parsedHTML)
  parsedHTML = re.sub("</li>", "</p>", parsedHTML)

  # Remove empty p tags
  parsedHTML = re.sub("<p>\s*</p>\n", "", parsedHTML)

  # p class title to "h0"
  parsedHTML = re.sub("<p class=\"title\">\s(.+?)</p>\n", h0_replace, parsedHTML)
  # Subtitle
  parsedHTML = re.sub("<p class=\"subtitle\">\s(.+?)\n?</p>\n", subtitle_replace, parsedHTML)

  # Remove excess newlines
  parsedHTML = re.sub("(<[^/]*?>)\n", clean_newlines, parsedHTML)

  # TODO - read title?
  parsedHTML = re.sub("[\s\S]*</h7>\n", "", parsedHTML)
  print(parsedHTML)

  parsedHTML = parsedHTML.split("\n")

  yaml = clean_html_to_yaml(parsedHTML)
  return yaml



def h0_replace(matchobj):
  return "<h0>" + matchobj.group(1) + "</h0>\n"

def subtitle_replace(matchobj):
  return "<h7>" + matchobj.group(1) + "</h7>\n"

def clean_newlines(matchobj):
  return matchobj.group(1)

def clean_html_to_yaml(cleanHTML):
  yaml = ""
  depth = 0
  lastHeader = None
  content = ""
  for line in cleanHTML:

    # print(line)
    header = re.sub("<h?|>.+", "", line)
    cleanedLine = re.sub("<.+?>", "", line)

    if (header == ""):
      continue
    
    if lastHeader == "p" and header != "p":
      yaml += (" " * 2 * (depth + 1)) + "content: \"" + content + "\"\n"
      content = ""
    
    if header != "p":
      yaml += (" " * int(header) * 2) + re.sub("\s", "_", cleanedLine.lower()) + ":\n"
      yaml += (" " * (int(header) + 1) * 2) + "title: \"" + cleanedLine + "\"\n"
      depth = int(header)

    if header == "p":
      content += cleanedLine + "\\n"

    lastHeader = header
    
  yaml += (" " * 2 * (depth + 1)) + "content: \"" + content + "\"\n"

  return yaml



def skim_file(service, id):
  request = service.files().export_media(fileId=id, mimeType="text/html")
  fh = io.BytesIO()
  downloader = MediaIoBaseDownload(fh, request)
  done = False
  while done is False:
    status, done = downloader.next_chunk()
    print("Download %d%%." % int(status.progress() * 100))

  return fh.getvalue().decode("utf-8").replace(">", ">\n")

if __name__ == '__main__':
  main()
