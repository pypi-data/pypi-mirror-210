#DONWLOAD IMG DI UN SITO
import requests
from bs4 import BeautifulSoup
import os


def downloadallimg(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text,"lxml")

    lista = []

    for link in soup.find_all("img"):
        lista.append(link.get("data-src"))
        lista.append(link.get("src"))

    nomecartella = url.split(".")[1]+"_img"
    os.makedirs(nomecartella, exist_ok=True)
    warning,x = 0,0
    for linkimg in lista:
        
        if linkimg is None: 
            continue
        print(linkimg)
        nome_img = linkimg.split("/")[-1]
        nome_img = nome_img.split("?")[0]
        print(nome_img)
        try:
            req = requests.get(linkimg)
        except:
            print("warning")
            warning +=1
        with open(nomecartella+"/"+str(x)+"__" +nome_img, "wb") as f:
            f.write(req.content)
            x+= 1

    print("ci sono stati: ",warning , "warning su un totale di ", len(lista), " immagini")




