import requests
from bs4 import BeautifulSoup
import os


def listlink(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text,"lxml")
    cartellanome = url.split(".")[1]+"_siti"
    os.makedirs(cartellanome,exist_ok= True)
    lista = []

    with open(cartellanome+"/siti.txt", "w") as f:
        f.write("I link sono:   \n")
        for link in soup.find_all("a"):
            sololink = str(link.get("href"))
            if sololink.startswith("https"):
                f.write(sololink+"\n")    
    print("Operation successful")
    print(lista)
