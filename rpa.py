from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import logging

# Configuração do log
logging.basicConfig(filename="rpa_debug.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do Selenium
def configure_browser():
    options = Options()
    options.add_argument('--headless')  # Executar em modo headless
    options.add_argument('--disable-gpu')
    service = Service('C:\\Users\\vitor\\Documents\\RPA\\chromedriver.exe')  # Atualize o caminho correto
    return webdriver.Chrome(service=service, options=options)

# Função para realizar a pesquisa e coletar dados
def search_books(browser, query, max_results=8):
    books = []

    try:
        # Acessar o site
        url = "https://www.amazon.com.br"
        browser.get(url)

        # Realizar a pesquisa
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box = browser.find_element(By.ID, "twotabsearchtextbox")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Esperar pelos resultados
        WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']")))
        book_elements = browser.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")[:max_results]

        for book in book_elements:
            try:
                title = book.find_element(By.XPATH, ".//div/div/span/div/div/div[2]/div[1]/a/h2/span").text
            except Exception:
                title = "N/A"

            try:
                author_element = book.find_elements(By.XPATH, ".//div/div/span/div/div/div[2]/div[1]/div/span[3]")
                author = author_element[0].text if author_element else "Autor não disponível"
            except Exception:
                author = "N/A"

            try:
                price_whole = book.find_element(By.XPATH, ".//span[contains(@class, 'a-price-whole')]").text
                price_fraction = book.find_element(By.XPATH, ".//span[contains(@class, 'a-price-fraction')]").text
                price = f"R${price_whole},{price_fraction}"
            except Exception:
                price = "Preço não disponível"

            try:
                # Usando BeautifulSoup para capturar a nota média
                soup = BeautifulSoup(browser.page_source, "html.parser")
                rating_tag = soup.select_one(".//div/div/span/div/div/div[2]/div[2]/div/span/a/i[1]/span")
                rating = rating_tag.text if rating_tag else "Nota não disponível"
            except Exception as e:
                rating = "N/A"
                logging.error(f"Erro ao capturar nota: {e}")

            try:
                reviews_element = book.find_elements(By.XPATH, ".//div/div/span/div/div/div[2]/div[2]/div/a/span")
                reviews = reviews_element[0].text if reviews_element else "Avaliações não disponíveis"
            except Exception:
                reviews = "N/A"

            # Adicionar aos resultados
            if title != "N/A":
                books.append({
                    "Titulo": title,
                    "Autor": author,
                    "Preço": price,
                    "Nota Média": rating,
                    "Avaliações": reviews
                })
    except Exception as e:
        logging.error(f"Erro durante a coleta de dados: {e}")

    return books

# Função para salvar os dados em CSV
def save_to_csv(data, filename="livros_automacao_processos.csv"):
    if data:
        try:
            df = pd.DataFrame(data)
            df.sort_values(by="Titulo", inplace=True)
            df.to_csv(filename, index=False, encoding="utf-8")
            logging.info(f"Dados salvos no arquivo '{filename}'.")
        except Exception as e:
            logging.error(f"Erro ao salvar os dados no arquivo CSV: {e}")
    else:
        logging.warning("Nenhum dado disponível para salvar.")

# Main
def main():
    browser = configure_browser()

    try:
        logging.info("Iniciando a automação de coleta de livros.")
        query = "livros sobre automação de processos"
        books = search_books(browser, query)
        save_to_csv(books)
        logging.info("Automação concluída com sucesso.")
    except Exception as e:
        logging.error(f"Erro na execução do RPA: {e}")
    finally:
        browser.quit()
        logging.info("Navegador encerrado.")

if __name__ == "__main__":
    main()
