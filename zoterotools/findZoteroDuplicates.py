from pyzotero import zotero
import difflib

def check_for_duplicate(article1, article2, title_thresh, author_thresh, abstract_thresh):
    outputString = ""
    potentialDuplicateIndicatorCount = 0
    if "data" in article1 and "data" in article2:
        # retrieve article data
        articleData1 = article1["data"]
        articleData2 = article2["data"]

        # compare author lists
        authorListSimilarity = 0.0
        if "creators" in articleData1 and "creators" in articleData2:
            creators1 = articleData1["creators"]
            creators2 = articleData2["creators"]
            authors1 = []
            authors2 = []
            for a in range(len(creators1)):
                currentCreator1 = creators1[a]
                if "lastName" in currentCreator1:
                    authors1.append(currentCreator1["lastName"])
                elif "name" in currentCreator1:
                    authors1.append(currentCreator1["name"])
            for b in range(len(creators2)):
                currentCreator2 = creators2[b]
                if "lastName" in currentCreator2:
                    authors2.append(currentCreator2["lastName"])
                elif "name" in currentCreator2:
                    authors2.append(currentCreator2["name"])
            if len(authors1)>0 and len(authors2)>0:
                authorListSimilarity = float(len(set(authors1)&set(authors2)))/len(set(authors1)|set(authors2))
                if authorListSimilarity>author_thresh:
                    potentialDuplicateIndicatorCount += 1

        # compare titles
        titleSimilarity = 0.0
        if "title" in articleData1 and "title" in articleData2:
            title1 = articleData1["title"]
            title2 = articleData2["title"]
            titleSimilarity = difflib.SequenceMatcher(None, title1, title2).ratio()
            if titleSimilarity>title_thresh:
                potentialDuplicateIndicatorCount += 1

        # compare abstracts
        abstractSimilarity = 0.0
        if "abstractNote" in articleData1 and "abstractNote" in articleData2:
            abstract1 = articleData1["abstractNote"]
            abstract2 = articleData2["abstractNote"]
            if abstract1 and abstract2:
                abstractSimilarity = difflib.SequenceMatcher(None, abstract1, abstract2).ratio()
                if abstractSimilarity>abstract_thresh:
                    potentialDuplicateIndicatorCount += 1

        # identify duplicates and write to output string
        if potentialDuplicateIndicatorCount > 1:
            outputString += "Potential duplicate:\n"
            outputString += "--------------------\n"
            outputString = outputString + " " + article1["key"] + "; " + ", ".join(authors1) + ": " + title1 + "\n"
            outputString = outputString + " " + article2["key"] + "; " + ", ".join(authors2) + ": " + title2 + "\n"
            outputString += "\n\n"
            return [1, outputString]
        else:
            return [0, ""]

def find_duplicates(zotero_group_id, zotero_api_key, zotero_collection_id=[], output_file_name="", title_thresh=0.75, author_thresh=0.75, abstract_thresh=0.5):
    """
    Function to be used to find potential duplicates in a zotero library / zotero collections.
    Two papers are considered a duplicate if at least two of the following statements are true
    - The author lists have at least an overlap of author_thresh (default: 75%)
    - The titles have at least an overlap of title_thresh (default: 75%)
    - The abstracts have at least an overlap of abstract_thresh (default: 75%)
    :param zotero_group_id: ID of zotero group in which duplicate search will be performed (see https://forums.zotero.org/discussion/71055/where-do-i-find-the-groupid)
    :param zotero_api_key: Personal key to communicate with API. Can be generated here: https://www.zotero.org/settings/keys
    :param zotero_collection_id: IDs of the zotero collections for the elements of which duplicate search will be performed (see https://forums.zotero.org/discussion/18400/collectionid-collectionkey)
    :param output_file_name: File location where output should be written
    :param title_thresh: Threshold defining the minimum necessary overlap of the titles to be considered as duplicate (default: 0.75)
    :param author_thresh: Threshold defining the minimum necessary overlap of the author lists to be considered as duplicate (default: 0.75)
    :param abstract_thresh: Threshold defining the minimum necessary overlap of the abstracts to be considered as duplicate (default: 0.5)
    :return: String of found potential duplicates
    """
    zot = zotero.Zotero(zotero_group_id, "group", zotero_api_key)
    articles = []
    if len(zotero_collection_id)>0:
        # if at least one zotero collection id is specified load articles from collection(s)
        for i in range(len(zotero_collection_id)):
            articles += zot.everything(zot.collection_items(zotero_collection_id[i]))
    else:
        # else load all articles from zotero group
        articles = zot.everything(zot.items())

    duplicateCount = 0
    outputString = ""

    # compare all articles for potential duplicates
    for i in range(len(articles)-1):
        for j in range(i+1,len(articles)-1):
            article1 = articles[i]
            article2 = articles[j]
            duplicateCheckResult = check_for_duplicate(article1, article2, title_thresh, author_thresh, abstract_thresh)
            duplicateCount += duplicateCheckResult[0]
            outputString += duplicateCheckResult[1]
    if duplicateCount==0:
        outputString += "No duplicates found!"
    else:
        outputString = outputString +  "Number of potential duplicates found: " + str(duplicateCount)

    # print found duplicates and save to file if file name is specified
    print(outputString)
    if output_file_name:
        output_file = open(output_file_name,"w",encoding="utf-8")
        output_file.write(outputString)
        output_file.close()

    return outputString