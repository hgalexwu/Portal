from selenium import webdriver

def download_json(source,destination):
    browser = webdriver.Chrome() #replace with .Firefox(), or with the browser of your choice
    url = "https://www.faredetective.com/farehistory/flights-from-"+source+"-to-"+destination+".html"
    browser.get(url) #navigate to the page
    # click arrow -> save as -> JSON
    browser.find_element_by_xpath("//*[@id='chartdiv_content']/div/div[3]/ul/li/a").click()
    browser.find_element_by_xpath("//*[@id='chartdiv_content']/div/div[3]/ul/li/ul/li[2]/a").click()
    browser.find_element_by_xpath("//*[@id='chartdiv_content']/div/div[3]/ul/li/ul/li[2]/ul/li[3]/a").click()

if __name__ == '__main__':
    download_json("Montreal-YUL","Tokyo-NRT")