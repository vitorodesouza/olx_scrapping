import requests

# Make a GET request to the URL
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/vw-volkswagen/nivus/estado-ac?sf=1&o=10'  
hdr= {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
    }

response = requests.get(url,headers=hdr)

print(response.history)
print(response.status_code)

# Check if a redirection occurred
if response.history:
    print(f"Request was redirected {len(response.history)} times")
    for resp in response.history:
        print(f"Redirected to: {resp.url}")
    print(f"Final URL after redirection: {response.url}")
else:
    print("No redirection occurred")