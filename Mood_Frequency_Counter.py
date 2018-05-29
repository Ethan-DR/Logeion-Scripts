# This script allows you to go through a SQL database to find the frequency of different moods throughout all of the works present in the database. The script will output a .tsv file with the moods and their respective frequencies.

# The script will use the second argument of the command line as the path for writing the .tsv file. All arguments after the second argument can be used to exclude authors whose works you don't want to include. For example, to remove all of Homer, input "Homer". This is case sensitive. Authors with multiple names (e.g. Diogenes Laertius), should be excluded using the first name which appears in the file names of their texts. Certain texts can be excluded using this method or their full name. For example, the New Testament can be excluded via "New" or via "New Testament". Such texts can be found in the "incorrect" and "corrected" arrays. In order for this to work, you must put the unwanted and wanted outputs in the same positions in their respective arrays (e.g. if the unwanted output "New" is the second value in the "incorrect" array, "New Testament" must be the second value in the corrected array).

import codecs
import sys
import unicodedata
import re
import csv
import sqlite3
conn = sqlite3.connect(---Path to SQL database---)
db = conn.cursor()



def main():
    # Dictionary for all the words and codecount
    codecount = {}
    # Dictionary for ordered codecount
    orderedcc = {}
    # Array of authors that create name issues
    incorrect = ["Demades12","New", "Reading"]
    # Array of authors that are solutions to the ones that cause problems. In order for the program to work, a corrected author name must occupy the same slot posiiton as the incorrect name that it corresponds with
    corrected = ["Demades", "New Testament", "Reading Greek"]
    # Iterates through each content entry in tokens
    for wordposition in conn.execute("SELECT tokenid FROM tokens"):
        skip = 0
        # Checks for command line inputs that exclude authors
        if len(sys.argv) > 2:
        # Gets author
            db.execute("SELECT file FROM tokens WHERE tokenid=?", wordposition)
            text = db.fetchall()
            if text:
                # Cleans up author text so it is just the name of the author from the file. This assumes that each word of the file name has only its first letter capitalized and that the first word in the name of the author. Cases for which this cannot be assumed should be added to the incorrect and corrected arrays.
                author0 = text[0]
                author1 = author0[0]
                author2 = re.findall('[A-Z][^A-Z]*', author1)
                author = author2[0]
                # Checks if author is excluded, and if so, moves on to next word
                if len(sys.argv) > 2:
                    for w in sys.argv:
                        if w == author:
                            skip = 1
                        if w in corrected:
                            if author == incorrect[corrected.index(w)]:
                                skip = 1
        if skip == 1:
            continue
        # Checks if there's an assigned parse already assigned in parses
        db.execute("SELECT code FROM parses WHERE tokenid=?", wordposition)
        code = db.fetchall()
        # Adds value to list if it exists
        if code:
            # Makes sure parsing are valid
            if not (None,) in code and not ('----------',) in code:
                # Checks if we have come across code before and cleans up code so it's just wanted value
                codetext0 = code[0]
                codetext = codetext0[0]
                if codetext[5] in codecount:
                    # Updates codecount if so
                    codecount[codetext[5]] += 1
                else:
                    # Creates new entry
                    codecount[codetext[5]] = 1
            else:
                # Gets lex value of the token
                db.execute("SELECT lex FROM parses WHERE tokenid=?", wordposition)
                lex = db.fetchall()
                if lex:
                    # Checks if multiple lex values as diff potential parses when no bless lemma is picked
                    if len(lex) > 1:
                        vallist = []
                        for i in range(len(lex)):
                            # Gets probs for each lex
                            db.execute("SELECT prob FROM parses WHERE tokenid=?", wordposition)
                            probs = db.fetchall()
                            # Getting float values of the probabilities from each tuple
                            probval = ""
                            probval = probval.join(str(j) for j in probs[i])
                            # Creating list of float values
                            vallist.append(probval)
                        # Getting max value of that list
                        prob = max(vallist)
                        # Finds which lex it corresponds to and using that lex
                        index = vallist.index(prob)
                        lex[0] = lex[index]
                    # Gets code of word as defined by Lexicon
                    db.execute("SELECT code FROM Lexicon WHERE lexid=?", lex[0])
                    code = db.fetchall()
                    # Checks if we have a code and cleans up code so just text
                    if code:
                        # Turns tuple into string
                        codetext0 = code[0]
                        codetext = codetext0[0]
                        # Cleans up code so it's just the wanted value and checks if we have come across code before
                        if codetext[5] in codecount:
                            # Updates codecount if previously come across
                            codecount[codetext[5]] += 1
                        else:
                            # Creates new entry if not previously come across
                            codecount[codetext[5]] = 1

    # Orders moods from most to least common
    for w in sorted(codecount, key=codecount.get, reverse=True):
        orderedcc[w] = codecount[w]
    # Writes .tsv file of moods and their frequencies
    with open(sys.argv[1], 'w', encoding= 'utf-8') as f:
        writer = csv.writer(f, delimiter=' ', quotechar='', quoting=csv.QUOTE_NONE, escapechar= ' ')
        for w in orderedcc:
            writer.writerow([w, "\t", codecount[w]])

if __name__== "__main__":
    main()





