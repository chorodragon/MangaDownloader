#!/usr/bin/env python

import sqlite3
import subprocess
import os
import opml
import requests
import urllib.request
from bs4 import BeautifulSoup

pathManga = ""
user = ""
password = ""

def loadConfig():
    file = open("manga.config", "r")
    lines = list()
    global user
    global password
    global pathManga
    for line in file.readlines():
        temp = line.split(" ")
        if (temp[0].strip() == "user"):
            user = temp[2].replace('\n', "") 
        if (temp[0].strip() == "password"):
            password = temp[2].replace('\n', "")
        if (temp[0].strip() == "path"):
            pathManga = temp[2].replace('\n', "")
    file.close()

def parseOPML():
    file = opml.parse('madokami-watched.opml')
    elements = file[0]
    return elements

def filterElements(elements, mangas):
    result = list()
    for element in elements:
        if element.title in mangas and "Raws" not in element.htmlUrl and element.htmlUrl not in result:
            result.append(element.htmlUrl)
    return result

def parseBookMarks():
    file = open("manga.txt", "r")
    lines = list()
    for line in file.readlines():
        lines.append(line.strip())
    file.close()
    return lines

def verifyExistance(link):
    conn = sqlite3.connect('manga.db')
    query = conn.cursor()
    query.execute('select * from downloaded where link = "' + link + '"')
    return len(query.fetchall())

def getLinksFrom(element):
    listado = list()
    session = requests.Session()
    session.auth = (user, password)
    auth = session.post(element)
    page = session.get(element)
    soup = BeautifulSoup(page.text, 'html.parser')
    items = soup.find_all('a')
    for item in items:
        link = item.get('href')
        if link is not None and "reader" not in link and ('cbz' in link or 'zip' in link or 'rar' in link):
            link = "https://manga.madokami.al" + link
            if verifyExistance(link) == 0:
                title = item.contents[0]
                pair = (title, link)
                listado.append(pair)
    return listado

def addToDB(link):
    conn = sqlite3.connect('manga.db')
    query = conn.cursor()
    query.execute('insert into downloaded values ("' + link + '")')
    conn.commit()
    conn.close()

def downloadFrom(links):
    for pair in links:
        title = pair[0]
        link = pair[1]
        session = requests.Session()
        session.auth = (user, password)
        auth = session.post(link)
        print("Downloading: " + title)
        r = session.get(link)
        with open(pathManga + title, "wb") as f:
            f.write(r.content)
        if r.status_code == 200:
            addToDB(link)

def getLinksElements():
    file = open('manga.links', 'r')
    lines = list()
    for line in file.readlines():
        lines.append(line.strip())
    return lines

def main():
    loadConfig()
    elements = parseOPML()
    selected = parseBookMarks()
    elements = filterElements(elements, selected)
    elements.extend(getLinksElements())
    for element in elements:
        links = getLinksFrom(element)
        downloadFrom(links)


if __name__ == '__main__':
    main()
