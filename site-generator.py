import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse

def slugify(value):
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', str(value)).strip().lower())

# 1. Initialization
data_folder = 'data'
all_reactors = []

with open('templates/reactor_page.html', 'r') as f:
    site_template = f.read()
with open('templates/home_page.html', 'r') as f:
    home_template = f.read()

# 2. Collect Data & Generate Individual Pages
for filename in os.listdir(data_folder):
    if filename.endswith('.json'):
        with open(os.path.join(data_folder, filename), 'r') as f:
            reactor = json.load(f)
        
        # Safety for list-formatted JSON
        if isinstance(reactor, list): reactor = reactor[0]
        
        # Clean metadata
        reactor['slug'] = slugify(reactor.get('name', filename))
        reactor['timestamp'] = reactor.get('last_modified', '2000-01-01 00:00:00')
        if 'image_url' in reactor:
            reactor['image_domain'] = urlparse(reactor['image_url']).netloc.replace('www.', '')

        # Generate the site page
        content = site_template
        placeholders = re.findall(r"\{\{(.*?)\}\}", content)
        for p in placeholders:
            if p in reactor:
                content = content.replace(f"{{{{{p}}}}}", str(reactor[p]))
            else:
                # Remove entire line if data is missing
                content = re.sub(f".*{{{{{p}}}}}.*", "", content)

        path = f"sites/{reactor['slug']}"
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/index.html", "w") as f:
            f.write(content)
        
        all_reactors.append(reactor)

# 3. Create Lists for Homepage
# Sort Alphabetically (for the main list)
alphabetical = sorted(all_reactors, key=lambda x: x.get('name', '').lower())
all_links = [f"<li><a href='sites/{r['slug']}/index.html'>{r['name']}</a></li>" for r in alphabetical]

# Sort by Date (for the "Recent" list)
# We sort descending (newest first) and take the top 5
recent_reactors = sorted(all_reactors, key=lambda x: x['timestamp'], reverse=True)[:5]
recent_links = [
    f"<li><a href='sites/{r['slug']}/index.html'><strong>{r['name']}</strong></a> <span class='date-tag'>({r['timestamp']})</span></li>" 
    for r in recent_reactors
]

# 4. Finalize Homepage
global_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
final_home = home_template.replace("{{list_items}}", "\n".join(all_links))
final_home = final_home.replace("{{recent_items}}", "\n".join(recent_links))
final_home = final_home.replace("{{timestamp}}", global_sync)

with open("index.html", "w") as f:
    f.write(final_home)

print(f"Build success. {len(all_reactors)} pages generated.")