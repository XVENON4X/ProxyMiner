import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time

PROXY_URL = "https://www.sslproxies.org"
TEST_URL = "http://httpbin.org/ip"  

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36"
}

def fetch_proxies():
    response = requests.get(PROXY_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch proxy list. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    proxy_table = soup.find('table', {'id': 'proxylisttable'})
    if not proxy_table:
        
        proxy_table = soup.find_all('tr')
    
    proxies = []
    for row in proxy_table:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
        ip = cols[0].text.strip()
        port = cols[1].text.strip()
        
        
        proxy_type = cols[4].text.strip() if len(cols) > 4 else "Unknown"
        
        
        proxy_protocol = "SOCKS" if port == "1080" else "HTTP/HTTPS"  
        
        proxies.append((f"{ip}:{port}", proxy_type, proxy_protocol))

    if not proxies:
        raise Exception("No proxies found.")
    
    return proxies

def test_proxy(proxy):
    try:
        start_time = time.time()
        response = requests.get(TEST_URL, proxies={"http": f"http://{proxy[0]}", "https": f"http://{proxy[0]}"}, timeout=5)
        response_time = time.time() - start_time

        if response.status_code == 200:
            return proxy, response_time
    except Exception:
        pass
    return None

def main():
    print("Fetching proxies...")
    try:
        proxies = fetch_proxies()
        print(f"Found {len(proxies)} proxies. Testing...")
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        return

    best_proxies = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(test_proxy, proxies)

        for result in results:
            if result:
                best_proxies.append(result)

    best_proxies.sort(key=lambda x: x[1])   

    print("Best proxies:")
    for proxy, response_time in best_proxies[:10]:   
        print(f"{proxy[0]} - {proxy[1]} - {proxy[2]} - {response_time:.2f} s")

    time.sleep(5)

if __name__ == "__main__":
    main()
