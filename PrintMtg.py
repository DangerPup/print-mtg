import scryfallapi
import datetime
import logging
import io
import sys

# Open a file and return lines as a list.
# Good for small to medium sized files.
# List items will be bytearrays. Caller can use decode() function to convert to string.
def OpenFileAsList(strFilePath):
    if not strFilePath:
        return None
    
    retList = None
    f = None
    try:
        f = io.FileIO(strFilePath, 'r')
        if f:
            retList = f.readlines()
    except:
        dt = datetime.datetime.now()
        for ex in sys.exc_info():
            logging.error(f'{dt.isoformat()} Exception: {ex}')

    finally:
        if f:
            f.close()
            f = None

    return retList

# Read a file of mtg cards and create an html file with images for printing.
def main():
    logging.basicConfig(filename="PrintMtg.log", level=logging.INFO)

    myMtgFilePath = "MyMtgList.txt"

    logging.info(f'Reading {myMtgFilePath}')   
    myMtgList = OpenFileAsList(myMtgFilePath)
    
    # Identify each card and how many, then get the image uri.
    cardCount = 0
    cardName = ""
    cardImageUriList = []
    for card in myMtgList:
        # Clean up line: decode, tabs, end lines.
        cardClean = card.decode()
        cardClean = cardClean.replace("\t", " ")
        cardClean = cardClean.replace("\r\n", "")

        cardSplit = cardClean.partition(" ")
        cardCount = int(cardSplit[0])
        cardName = cardSplit[2]
        i = 0
        while i < cardCount:
            cardImageUriList.append(scryfallapi.GetImageUriByCardName(cardName))
            i = i + 1

    # Create an html file next to myMtgFilePath.
    myMtgFilePathParts = myMtgFilePath.rpartition("\\")
    myMtgFilePathOut = myMtgFilePathParts[0] + myMtgFilePathParts[1] + "out.html" 
    myMtgFileFileOut = io.FileIO(myMtgFilePathOut, 'w')
    myMtgFileFileOut.write(b"<html><body><table>")
    colCount=1
    for cardUri in cardImageUriList:
        if colCount == 1:
            myMtgFileFileOut.write(f"<tr>".encode())

        colCount = colCount + 1
        myMtgFileFileOut.write(f'<td><img width="223" height="311" src="{cardUri}" /></td>'.encode())

        if colCount > 3:
            myMtgFileFileOut.write(b"</tr>")
            colCount = 1
        
    myMtgFileFileOut.write(b"</table></body></html>")
    myMtgFileFileOut.close()
    myMtgFileFileOut = None


main()

