import http.client
import re

conn = http.client.HTTPConnection('localhost', 8000)
conn.request('GET', '/api/pets/')
r = conn.getresponse()
body = r.read().decode()

print('Status:', r.status)

# Extract all traceback frames
frames = re.findall(r'<span class="fname">(.*?)</span>', body)
for f in frames:
    print('File:', f)

# Extract error message
m = re.search(r'<pre class="exception_value">(.*?)</pre>', body, re.DOTALL)
if m:
    print('\nError:', m.group(1).strip())

# Extract all context lines
contexts = re.findall(r'<ol class="context" start="(\d+)">(.*?)</ol>', body, re.DOTALL)
for start, ctx in contexts[:5]:
    lines = re.findall(r'<span class="cline">(.*?)</span>', ctx)
    for l in lines:
        print(f'  Line {start}: {l.strip()[:100]}')
