import requests
import json
from pyzotero import zotero


def get_medrxiv_group_items(groupID: int):
    params = {"grp": groupID}
    response = requests.get(
        "https://connect.medrxiv.org/relate/collection_json.php", params=params
    )
    decoded = json.loads(response.text)
    print("Got", len(decoded["rels"]), "from medrxiv group", groupID)
    return decoded["rels"]


def convert_rel_to_item(zot, rel, collection_id):
    template = zot.item_template("journalArticle")
    template["title"] = rel["rel_title"]
    template["DOI"] = rel["rel_doi"]
    template["url"] = rel["rel_link"]
    template["abstractNote"] = rel["rel_abs"]
    template["date"] = rel["rel_date"]
    template["archive"] = rel["rel_site"]
    template["creators"] = []
    for author in rel["rel_authors"]:
        # TODO figure out author institution, if necessary
        creator = {"name": author["author_name"], "creatorType": "author"}
        template["creators"].append(creator)
    template["collections"].append(collection_id)
    return template


def add_to_zotero(zot, items):
    pages = []
    for i in range(0, len(items), 50):
        page = items[i : i + 50]
        pages.append(page)
    print("Number of pages to submit: " + str(len(pages)))
    i = 0
    for page in pages:
        i += 1
        print("submitting page " + str(i) + " of " + str(len(pages)))
        zot.create_items(page)


def import_medrxiv_group_to_zotero(
    medarxiv_group: int, zotero_group_id: str, zotero_collection_id, zotero_api_key
):
    zot = zotero.Zotero(zotero_group_id, "group", zotero_api_key)
    rels = get_medrxiv_group_items(medarxiv_group)
    items = []
    for rel in rels:
        items.append(convert_rel_to_item(zot, rel, zotero_collection_id))
    add_to_zotero(zot, items)
