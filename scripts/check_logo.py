import urllib.request
r=urllib.request.urlopen('http://127.0.0.1:5000/')
text=r.read().decode('utf-8')
for i,line in enumerate(text.splitlines(), start=1):
    if 'logo_olga_bayone' in line or 'rel="icon"' in line or 'favicon' in line:
        print(i, line.strip())
print('\n--- Full occurrences ---')
for line in text.splitlines():
    if 'logo_olga_bayone' in line:
        print(line)
