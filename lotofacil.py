from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from collections import Counter
from datetime import datetime
import time
import csv
import os
import re

CSV_FILE = 'resultados_lotofacil.csv'

def openDriver():
    driver = webdriver.Chrome()
    WEBSITE = "https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx"
    driver.get(WEBSITE)
    driver.implicitly_wait(10)
    return driver

def getLastGame():
    try:
        with open('resultados_lotofacil.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            linhas = list(reader)
            if len(linhas) <= 1:
                return 0
            return int(linhas[-1][0])
    except FileNotFoundError:
        return 0


def getGameNumberAndDate(chromeDriver):
    tituloJogoData = chromeDriver.find_element(By.XPATH, '//div[@class="title-bar clearfix"]/h2/span')
    textoRepartido = tituloJogoData.text.split(" ") 
    numeroJogo = textoRepartido[1]
    data = re.search(r"\d{2}/\d{2}/\d{4}", textoRepartido[2]).group()
    timestamp = int(datetime.strptime(data, "%d/%m/%Y").timestamp())
    return {"nJogo": numeroJogo, "timestamp": timestamp}

def collectResults(driver, ultimoJogo):
    jogos = []
    countProcessados = 0
    jogoMaisRecente = int(getGameNumberAndDate(driver)["nJogo"])

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(["jogo", "timestamp"] + [f"bola{i+1:02}" for i in range(15)])

    for jogoAtual in range(ultimoJogo + 1, jogoMaisRecente + 1):
        campoPesquisaJogo = driver.find_element(By.CSS_SELECTOR, 'input#buscaConcurso')
        campoPesquisaJogo.clear()
        campoPesquisaJogo.send_keys(jogoAtual)
        campoPesquisaJogo.send_keys(Keys.ENTER)
        
        try:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.resultado-loteria > div > ul.simple-container.lista-dezenas.lotofacil')))

            elementoResultado = driver.find_element(By.XPATH, '//div[@class="resultado-loteria"]/div/ul[contains(@class, "simple-container") and contains(@class, "lista-dezenas") and contains(@class, "lotofacil")]')
            numeros = elementoResultado.text.strip().split()
            if len(numeros) != 15:
                print(f"Erro na leitura dos números do jogo {jogoAtual}. Pulando...")
                continue

            dataJogoAtual = getGameNumberAndDate(driver)
            linha = [jogoAtual, dataJogoAtual["timestamp"]] + numeros

            with open(CSV_FILE, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(linha)

            countProcessados += 1
            print(f"Adicionado jogo {jogoAtual}", end="\r")

        except TimeoutException:
            print(f"Timeout ao processar jogo {jogoAtual}")

def count():
    if not os.path.exists(CSV_FILE):
        print("Arquivo CSV não encontrado.")
        return

    contagem_numeros = Counter()

    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            bolas = row[2:]
            for numero in bolas:
                contagem_numeros[numero] += 1

    listNumber(contagem_numeros, True)
    listNumber(contagem_numeros, False)

def listNumber(contagem_numeros, option):
    valores = []
    final = ""
    if option:
        top_15_numeros = contagem_numeros.most_common(15) 
        print("Os 15 números que mais saem na Lotofácil são:\n")
        for numero, _ in top_15_numeros: valores.append(numero)
    else:
        least_15_numeros = contagem_numeros.most_common()[-15:]
        print("\nOs 15 números que menos saem na Lotofácil são:\n")
        for numero, _ in least_15_numeros: valores.append(numero)
    valores.sort()
    final = " ".join(valores)
    print(final)

def main():
    ultimoJogo = getLastGame()
    driver = openDriver()
    print("Iniciando a coleta dos dados em breve", end="\r")
    collectResults(driver, ultimoJogo)
    driver.quit()
    print("Coleta concluída", end="\r")
    time.sleep(0.5)
    print("Iniciando a contagem bruta dos resultados", end="\r")
    count()

if __name__ == "__main__":
    main()
