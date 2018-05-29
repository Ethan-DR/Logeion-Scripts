# This script allows you to go through a SQL database to find what authors most commonly use the different lemmas throughout all of the works present in the database. The script will output a .tsv file with the lemmas, and the authors ranked in order of most common to least common usage of that lemma.

# The script will use the second argument of the command line as the path for writing the .tsv file. All arguments after the second argument can be used to exclude authors whose works you don't want to include. For example, to remove all of Homer, input "Homer". This is case sensitive. Authors with multiple names (e.g. Diogenes Laertius), should be excluded using the first name which appears in the file names of their texts. Certain texts can be excluded using this method or their full name. For example, the New Testament can be excluded via "New" or via "New Testament". Such texts can be found in the "incorrect" and "corrected" arrays. These arrays can also be used to change the output of the .tsv file. For example, the script would normally write "New" as opposed to "New Testament". However, by putting the unwanted output in the "incorrect" array, and the wanted outpute in the "corrected array", you can change the author's name in anyway way. In order for these two things to work, you must put the unwanted and wanted outputs in the same positions in their respective arrays (e.g. if the unwanted output "New" is the second value in the "incorrect" array, "New Testament" must be the second value in the corrected array).

import codecs
import sys
import unicodedata
import csv
import re
import copy
import sqlite3
conn = sqlite3.connect(---Path to SQL database---)
db = conn.cursor()



def main():
    # Dictionary for author
    authors = {}
    # Dictionary for the words and wordcount for each author
    wordcount = {}
    # Dictionary for total number of tokens per author
    totalwords = {}
    # Dictionary of every lemma found
    words = {}
    # Dictionary of every lemma with the frequency per author
    percentages = {}
    # Dictionary of every lemma with authors ordered, frequence number has been removed
    nonumbers = {}
    # Array of authors that create name issues
    incorrect = ["Demades12","New", "Reading"]
    # Array of authors that are solutions to the ones that cause problems. In order for the program to work, a corrected author name must occupy the same slot posiiton as the incorrect name that it corresponds with.
    corrected = ["Demades", "New Testament", "Reading Greek"]
    
    # Iterates through each content entry in tokens
    for wordposition in conn.execute("SELECT tokenid FROM tokens"):
        skip = 0
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
            # If came across author before updates lemma counts
            if author in authors:
                authors[author] = copy.copy(wordcount)
            # If we did not come across the author before then it resets word count and begins again. Doing this would cause us to miss an author if they only have one word total in their text. We are assuming authors have a minimum of two words.
            if author not in authors:
                wordcount.clear()
                counter = 0
                authors[author] = wordcount

        # Checks if there's an assigned lemma in the parsing table
        db.execute("SELECT lemma FROM parses WHERE tokenid=?", wordposition)
        alemma = db.fetchall()
        # Adds value to the wordcount if there is a valid lemma
        if alemma:
            # Checks for potential lemma values which are not valid lemmas
            if not (None,) in alemma and not ('<unknown>',) in alemma and not ('unknown',)in alemma and not ('segment',) in alemma and not ('textual problem',) in alemma and not ('crux',) in alemma:
                alemmatext = alemma[0]
                # Checks if we have come across lemma before and cleans up lemma so it's just text. Also makes sure ΑΒΓ is not counted.
                if "ΑΒΓ" not in alemmatext:
                    if alemmatext[0] in wordcount:
                        # Updates wordcount if lemma was already found and adds value to counter of total words for author
                        wordcount[alemmatext[0]] += 1
                        counter += 1
                        totalwords[author] = copy.copy(counter)
                    else:
                        # Creates new entry for the lemma and adds value to counter of total words for the author
                        wordcount[alemmatext[0]] = 1
                        counter += 1
                        totalwords[author] = copy.copy(counter)
        
            else:
                # Gets lex value of the token
                db.execute("SELECT lex FROM parses WHERE tokenid=?", wordposition)
                lex = db.fetchall()
                if lex:
                    # Checks if multiple lex values as diff potential parses when no bless lemma is picked
                    if len(lex) > 1:
                        vallist = []
                        for i in range(len(lex)):
                            # Gets probabilities for each lex
                            db.execute("SELECT prob FROM parses WHERE tokenid=?", wordposition)
                            probs = db.fetchall()
                            # Getting float vals of the probabilities from the tuple
                            probval = ""
                            probval = probval.join(str(j) for j in probs[i])
                            # Creating list of float values
                            vallist.append(probval)
                        # Getting max value of that list
                        prob = max(vallist)
                        # Finds and uses the lex it corresponds
                        index = vallist.index(prob)
                        lex[0] = lex[index]
                    # Gets lemma of word as defined by Lexicon
                    db.execute("SELECT lemma FROM Lexicon WHERE lexid=?", lex[0])
                    lemma = db.fetchall()
                    # Checks if we have a lemma and cleans up lemma so it's just text
                    if lemma:
                        lemmatext = lemma[0]
                        # Checks if we have come across lemma before and makes sure ΑΒΓ is not counted
                        if "ΑΒΓ" not in lemmatext:
                            if lemmatext[0] in wordcount:
                                # Updates wordcount if already found, and adds value to counter of total words for author
                                wordcount[lemmatext[0]] += 1
                                counter += 1
                                totalwords[author] = copy.copy(counter)
                            else:
                                # Creates new entry if not found, and adds value to counter of total words for author
                                wordcount[lemmatext[0]] = 1
                                counter += 1
                                totalwords[author] = copy.copy(counter)

    # Gets percents of each word for each author
    for w in authors:
        for v in authors[w]:
            percentage = 100 * authors[w][v]/totalwords[w]
            authors[w][v] = percentage

    # Gets all the obtained lemmas and puts them in a dict
    for w in authors:
        for v in authors[w]:
            lemma = v
            if lemma not in words:
                words[lemma] = ""

    # Goes through authors and gets percentages per lemma and puts the authors with their percentages into the percentages dictionary, ordered from most frequent to least
    # May be an issue if two authors have the exact same percent, haven't found a case for that yet though
    for n in words:
        for w in authors:
            if n in authors[w]:
                if n not in percentages:
                    percentages[n] = (w, authors[w][n])
                else:
                    # Check if higher than the first one
                    if percentages[n][1] < authors[w][n]:
                        curpcopy = percentages[n]
                        percentages[n] = (w, authors[w][n]) + curpcopy
                    # Check if lower than last one
                    elif percentages[n][len(percentages[n]) - 1] > authors[w][n]:
                        percentages[n] = percentages[n] + (w, authors[w][n])
                    else:
                        z = 1
                        l = 1
                        pcopy = copy.copy(percentages[n])
                        while z <= len(pcopy):
                            # Make copy for testing values, as original values will be cleared. If true then it is higher than that value so rewrites dict to that point, adds in value, then writes rest of the dict
                            if pcopy[z] < authors[w][n]:
                                j = z - 1
                                del percentages[n]
                                # Adds in first two of set
                                percentages[n] = (pcopy[0], pcopy[1])
                                # Fills in howevermany more entries go first
                                while l + 2 < z:
                                    l += 1
                                    percentages[n] = percentages[n] + (pcopy[l], pcopy[l+1])
                                    l += 1
                                # Adds in new entry
                                percentages[n] = percentages[n] + (w, authors[w][n])
                                # Finishes up entry with lesser values
                                while j < len(pcopy) - 1:
                                    percentages[n] = percentages[n] + (pcopy[j], pcopy[j+1])
                                    j += 2
                                z = len(pcopy) + 1
                            z += 2


    # Removes percentages so it's just the authors
    for w in percentages:
        q = 0
        nonumbers[w] = []
        while q < len(percentages[w]):
            nonumbers[w].append(percentages[w][q])
            q += 2

    # Writes out nonumbers as a tsv file wherever specified
    with open(sys.argv[1], 'w', encoding= 'utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE, escapechar=' ')
        for w in nonumbers:
            cleanstr = ""
            cleanstrcounter = 0
            for q in nonumbers[w]:
                # Corrects author names so just text of name when written to the file
                if q in incorrect:
                    q = corrected[incorrect.index(q)]
                cleanstr += q
                cleanstrcounter + 1
                if cleanstrcounter != len(nonumbers[w]) - 1:
                    cleanstr += ("\t")
            writer.writerow([w, cleanstr])

if __name__== "__main__":
    main()





