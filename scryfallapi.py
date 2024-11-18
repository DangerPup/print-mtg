import httplib
import json
import logging
import math
import random

scryfallAPIUrl         = "api.scryfall.com"
scryfallResource_Cards = "cards"
scryfallResource_CardsSearch = "cards/search"

# we could just use Scryfall's "random" resource, but let's make things interesting
# known, from https://api.scryfall.com/cards/
#       total number of cards: 255826,  "total_cards" field
#       number of cards per page: 175.
#       total number of pages: [total_cards]/[pagesize=175] rounded up. Odd that they don't allow a 'page size' input.

# make totalCards able to be dynamic and persisted.
totalCards = 255826
# make pageSize able to be dynamic and persisted.
pageSize = 175

# Print card details
propsToPrint = ['name', 'scryfall_uri', 'mana_cost', 'cmc', 'oracle_text', 'set_name', 'artist']
def PrintRandomCard():
    randomCard = GetRandomCard()
    if randomCard:
        for prop in propsToPrint:
            print(f'{prop}: {randomCard[prop]}')
    else:
        print("Not found. See log.")
            
# Get a random English card object.
def GetRandomCard():    
    tries = 1
    while tries <= 20:
        tries = tries + 1
        rndNum = GetRandomNumber(1, totalCards)
        myPageNumAndIndex = [0, 0] # 0 index is 'Page Number', 1 index is 'PageIndex (0-based)'
        DeterminePageNumberAndPageIndex(rndNum, myPageNumAndIndex)
        url = BuildPageUrl(myPageNumAndIndex[0])
        cardListAsString = httplib.HttpInvoke("GET", scryfallAPIUrl, url, None)
        randomCardAsJsonObj = None
        if cardListAsString:
            jsonDec = json.decoder.JSONDecoder()
            cardListAsJsonObj = jsonDec.decode(cardListAsString)
            randomCardAsJsonObj = cardListAsJsonObj["data"][myPageNumAndIndex[1]]
            if randomCardAsJsonObj["lang"] == "en":
                #logging.debug
                break
            else:
                #logging.debug
                randomCardAsJsonObj = None

    return randomCardAsJsonObj

def BuildPageUrl(intPageIndex):
    return f'/{scryfallResource_Cards}?page={intPageIndex}'

def BuildSearchUrl(searchQuery):
    return f'/{scryfallResource_CardsSearch}?q={searchQuery}'
    
def DeterminePageNumberAndPageIndex(intRndNum, listPageNumAndIndex):
    refPageNum = math.ceil(intRndNum/pageSize)
    refIndex = (pageSize - ((pageSize * refPageNum) - intRndNum) - 1) # 0-based.
    refIndex = refIndex.__trunc__()
    listPageNumAndIndex[0] = refPageNum
    listPageNumAndIndex[1] = refIndex

def GetRandomNumber(rangeLow, rangeHigh):
    r = random.Random()
    return r.randrange(rangeLow, rangeHigh)

def TestCases():
    myPageNumAndIndex = [0, 0] # 0 index is 'Page Number', 1 index is 'PageIndex (0-based)'
    DeterminePageNumberAndPageIndex(1, myPageNumAndIndex)
    print(f'r: {pageSize}; Page: {myPageNumAndIndex[0]}; Index: {myPageNumAndIndex[1]}')
    DeterminePageNumberAndPageIndex(2, myPageNumAndIndex)
    print(f'r: {pageSize}; Page: {myPageNumAndIndex[0]}; Index: {myPageNumAndIndex[1]}')
    DeterminePageNumberAndPageIndex(3, myPageNumAndIndex)
    print(f'r: {pageSize}; Page: {myPageNumAndIndex[0]}; Index: {myPageNumAndIndex[1]}')
    DeterminePageNumberAndPageIndex(175, myPageNumAndIndex)
    print(f'r: {pageSize}; Page: {myPageNumAndIndex[0]}; Index: {myPageNumAndIndex[1]}')
    DeterminePageNumberAndPageIndex(176, myPageNumAndIndex)
    print(f'r: {pageSize}; Page: {myPageNumAndIndex[0]}; Index: {myPageNumAndIndex[1]}')    
    DeterminePageNumberAndPageIndex(totalCards, myPageNumAndIndex)
    print(f'r: {pageSize}; Page: {myPageNumAndIndex[0]}; Index: {myPageNumAndIndex[1]}')

def GetImageUriByCardName(cardName):
    if not cardName:
        return ""
    
    cardName = cardName.replace(" ", "%20")
    searchUrl = BuildSearchUrl(cardName)
    searchResultAsString = httplib.HttpInvoke("GET", scryfallAPIUrl, searchUrl, None)
    imageUrl = ''
    if searchResultAsString:
        jsonDec = json.decoder.JSONDecoder()
        searchResultAsJsonObj = jsonDec.decode(searchResultAsString)
        if searchResultAsJsonObj["object"]=="list":
            cardAsJsonObj = searchResultAsJsonObj["data"][0]
            imageUrl = cardAsJsonObj["image_uris"]["normal"]
        elif searchResultAsJsonObj["object"]=="error":
            imageUrl = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
    
    return imageUrl
   