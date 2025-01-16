import json
import re
import uuid

from django.conf import settings
from django.utils import timezone

settings.configure()
timezone.now()

bookmarks_profiles = [{
        "model": "bookmarks.bookmarksprofile",
        "pk": 1,
        "fields": {
            "user": 1
        }
    }]

def generate_fixation(input_data):
    """
    Converts the input JSON into two fixtures:
    - Categories (as their own model)
    - Bookmarks (not storing relationships here directly).
    - ManyToMany relationships saved as a separate intermediate list for the bookmark->categories relationships.
    """
    pk_counter = 1
    category_tracker = {}  # Track categories to avoid duplicates
    categories = []
    bookmarks = []
    bookmark_categories = []  # ManyToMany intermediate links

    # Get the current timestamp in ISO 8601 format
    now = timezone.now()

    # Process the input JSON to separate categories and bookmarks
    for category_name, bookmark_list in input_data.items():
        # Assign a category PK if not tracked already
        if category_name not in category_tracker:
            category_pk = len(category_tracker) + 1
            category_tracker[category_name] = category_pk
            categories.append({
                "model": "bookmarks.category",
                "pk": category_pk,
                "fields": {
                    "name": category_name,
                    "owner": 1,  # Adjust "owner" if needed (e.g., User id 1)
                    "created": now.isoformat(),
                    "updated": now.isoformat(),
                    "uuid": str(uuid.uuid4()),
                    "active": True
                }
            })

        # Add bookmarks referencing the category
        for bookmark in bookmark_list:
            bookmarks.append({
                "model": "bookmarks.bookmark",
                "pk": pk_counter,
                "fields": {
                    "name": bookmark.get("name"),
                    "url": bookmark.get("href"),
                    "icon_url": bookmark.get("icon_uri"),
                    "created": now.isoformat(),
                    "updated": now.isoformat(),
                    "uuid": str(uuid.uuid4()),
                    "owner_id": 1
                }
            })
            # Add the ManyToMany relationship for this bookmark and category
            bookmark_categories.append({
                "model": "bookmarks.category_bm",  # Intermediate model for ManyToMany relations
                "pk": len(bookmark_categories) + 1,
                "fields": {
                    "bookmark_id": pk_counter,  # Foreign key to `bookmarks.bookmark`
                    "category_id": category_tracker[category_name],  # Foreign key to `bookmarks.category`
                }
            })
            pk_counter += 1

    return categories, bookmarks, bookmark_categories

def parse_bookmarks(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Regular expressions to extract categories and bookmarks
    category_regex = r"<H3.*?>(.*?)</H3>"
    bookmark_regex = r'<A HREF="(.*?)"(?:.*?ICON_URI="(.*?)")?.*?>(.*?)</A>'

    categories = re.finditer(category_regex, html_content, re.IGNORECASE)

    result = {}
    current_category = None

    for line in html_content.splitlines():
        if match := re.search(category_regex, line, re.IGNORECASE):
            current_category = match.group(1).strip()
            if current_category not in result:
                result[current_category] = []
        elif match := re.search(bookmark_regex, line, re.IGNORECASE):
            href = match.group(1).strip()
            icon_uri = match.group(2).strip() if match.group(2) else None
            name = match.group(3).strip()

            # Validate icon_uri to ensure it starts with http
            if icon_uri and not icon_uri.startswith('http'):
                icon_uri = None

            if current_category:
                result[current_category].append({
                    "href": href,
                    "name": name,
                    "icon_uri": icon_uri
                })

    return result


def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

with open("bookmarks.html", "r") as f:
    html_content = f.read()

bookmarks_data = parse_bookmarks("bookmarks.html")

# Generate fixtures
categories, bookmarks, bc = generate_fixation(bookmarks_data)

for c in categories:
    bookmarks_profiles.append(c)

for bm in bookmarks:
    bookmarks_profiles.append(bm)

for bc_link in bc:
    bookmarks_profiles.append(bc_link)

with open("fixtures/bookmarks.json", "w") as f:
    json.dump(bookmarks_profiles, f, indent=4)
print("Fixtures generated")