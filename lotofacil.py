from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from collections import Counter
import json
import os

MAIS = True
MENOS = False

def collect(NUMERO_JOGOS_DESEJADOS):
    driver = webdriver.Chrome()
    WEBSITE = "https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx"
    jogos = []

    driver.get(WEBSITE)
    driver.implicitly_wait(10)

    elemento_jogo_inicial = driver.find_element(By.XPATH, '//div[@class="title-bar clearfix"]/h2/span').text.split(" ")[1]
    jogoInicial = int(elemento_jogo_inicial) if elemento_jogo_inicial else 3066
    if NUMERO_JOGOS_DESEJADOS > jogoInicial: NUMERO_JOGOS_DESEJADOS = jogoInicial
    for i in range(NUMERO_JOGOS_DESEJADOS):
        input_element = driver.find_element(By.CSS_SELECTOR, 'input#buscaConcurso')
        input_element.clear()
        input_element.send_keys(jogoInicial - i)
        input_element.send_keys(Keys.ENTER)
        
        try:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.resultado-loteria > div > ul.simple-container.lista-dezenas.lotofacil')))
            elemento_resultado = driver.find_element(By.XPATH, '//div[@class="resultado-loteria"]/div/ul[contains(@class, "simple-container") and contains(@class, "lista-dezenas") and contains(@class, "lotofacil")]').text
            valores_string = ' '.join([elemento_resultado[i:i+2] for i in range(0, len(elemento_resultado), 2)])
            jogos.append({"jogo": jogoInicial - i, "valores": valores_string})
        except TimeoutException:
            print("Tempo limite de espera excedido. A página pode não ter carregado corretamente ou os resultados não foram encontrados.")
        
    driver.quit()

    with open('resultados_lotofacil.json', 'w') as file:
        json.dump(jogos, file)

def count():
    with open('resultados_lotofacil.json', 'r') as file:
        dados = json.load(file)

    contagem_numeros = Counter()
    valores = ""

    for jogo in dados: valores += "".join(jogo['valores'])+" "
    for numero in valores.split(" ")[:-1]: contagem_numeros[numero] += 1

    listNumber(contagem_numeros, MAIS)
    listNumber(contagem_numeros, MENOS)

def listNumber(contagem_numeros, option):
    valores = []
    final = ""
    if option:
        top_15_numeros = contagem_numeros.most_common(15) 
        print("Os 15 números que mais saem na Lotofácil são:\n")
        for numero, contgem in top_15_numeros: valores.append(numero)
    else:
        least_15_numeros = contagem_numeros.most_common()[-15:]
        print("\nOs 15 números que menos saem na Lotofácil são:\n")
        for numero, contagem in least_15_numeros: valores.append(numero)
    valores.sort()
    for i in range(0, 15): final += valores[i] + " "
    print(final)

def menu():
    while True:
        os.system("cls")
        print("1 - Coletar resultados\n2 - Contar números\n3 - Sair")
        opcao = input("Escolha uma opção: ")
        if opcao == "1": 
            numero_jogos = int(input("Digite a quantidade de jogos que deseja coletar: "))
            collect(numero_jogos)
        elif opcao == "2": 
            count()
            input("\nPressione Enter para continuar...")
        elif opcao == "3": 
            break
    os.system("cls")

if __name__ == "__main__":
    menu()