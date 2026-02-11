import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse

def slugify(value):
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', str(value)).strip().lower())

# Get current time for the footer
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 1. Load Templates
with open('templates/reactor_page.html', 'r') as f:
    site_template = f.read()
with open('templates/home_page.html', 'r') as f:
    home_template = f.read()

home_links = []

# 2. Process every JSON file in /data
data_folder = 'data'
for filename in os.listdir(data_folder):
    if filename.endswith('.json'):
        with open(os.path.join(data_folder, filename), 'r') as f:
            reactor = json.load(f)
            
        # Safety check: if the JSON is a list with one item, grab that item
        if isinstance(reactor, list):
            reactor = reactor[0]

        # Add timestamp and domain to the data dictionary
        reactor['timestamp'] = now
        if 'image_url' in reactor:
            reactor['image_domain'] = urlparse(reactor['image_url']).netloc.replace('www.', '')

        # Build the page content
        content = site_template
        
        # Get all placeholders in the template using regex {{key}}
        placeholders = re.findall(r"\{\{(.*?)\}\}", content)
        
        for p in placeholders:
            if p in reactor:
                content = content.replace(f"{{{{{p}}}}}", str(reactor[p]))
            else:
                # If key is missing, remove the line that contains the placeholder
                # This prevents "Location: {{location}}" from showing if location is null
                content = re.sub(f".*{{{{{p}}}}}.*", "", content)

        # Create slug and save
        slug = slugify(reactor.get('name', filename.replace('.json', '')))
        path = f"sites/{slug}"
        os.makedirs(path, exist_ok=True)
        
        with open(f"{path}/index.html", "w") as f:
            f.write(content)
        
        home_links.append(f"<li><a href='sites/{slug}/index.html'>{reactor.get('name', slug)}</a></li>")

# 3. Build Homepage
home_links.sort() # Keep the list alphabetical
list_html = "\n".join(home_links)
final_home = home_template.replace("{{list_items}}", list_html).replace("{{timestamp}}", now)

with open("index.html", "w") as f:
    f.write(final_home)

print(f"Build complete at {now}. Processed {len(home_links)} files.")
