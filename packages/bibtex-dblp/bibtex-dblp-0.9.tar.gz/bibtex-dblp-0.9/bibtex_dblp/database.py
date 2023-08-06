import logging

import pybtex.database

import bibtex_dblp.dblp_api as dblp_api
import bibtex_dblp.search


def load_from_file(infile):
    """
    Load bibliography from file.
    :param infile: Path of input file.
    :return: Bibiliography in pybtex format.
    """
    return pybtex.database.parse_file(infile, bib_format="bibtex")


def write_to_file(bib, outfile):
    """
    Write bibliography to file.
    :param bib: Bibliography in pybtex format.
    :param outfile: Path of output file.
    """
    bib.to_file(outfile, bib_format="bibtex")


def parse_bibtex(bibtex):
    """
    Parse bibtex string into pybtex format.
    :param bibtex: String containing bibtex information.
    :return: Entry in pybtex format.
    """
    return pybtex.database.parse_string(bibtex, bib_format="bibtex")


def convert_dblp_entries(bib, bib_format=dblp_api.BibFormat.condensed):
    """
    Convert bibtex entries according to DBLP bibtex format.
    :param bib: Bibliography in pybtex format.
    :param bib_format: Bibtex format of DBLP.
    :return: converted bibliography, number of changed entries
    """
    logging.debug("Convert to format '{}'".format(bib_format))
    no_changes = 0
    for entry_str, entry in bib.entries.items():
        # Check for id
        dblp_id = dblp_api.extract_dblp_id(entry)
        if dblp_id is not None:
            logging.debug("Found DBLP id '{}'".format(dblp_id))
            result_dblp = dblp_api.get_bibtex(dblp_id, bib_format=bib_format)
            data = parse_bibtex(result_dblp)
            assert len(data.entries) <= 2 if bib_format is dblp_api.BibFormat.crossref else len(data.entries) == 1
            if entry_str not in data.entries:
                # DBLP key is not used as bibtex key -> remember DBLP key
                key = next(iter(data.entries))
                new_entry = data.entries[key]
                new_entry.fields['biburl'] = entry.fields['biburl']
                bib.entries[entry_str] = new_entry

            else:
                new_entry = data.entries[entry_str]
                # Set new format
                bib.entries[entry_str] = new_entry
                if bib_format is dblp_api.BibFormat.crossref:
                    # Possible second entry
                    for key, entry in data.entries.items():
                        if key != entry_str:
                            if key not in bib.entries:
                                bib.entries[key] = entry
            logging.debug("Set new entry for '{}'".format(entry_str))
            no_changes += 1
    return bib, no_changes


def search(bib, search_string):
    """
    Search for string in bibliography.
    Only the fields 'author' and 'title' are checked.
    :param bib: Bibliography in pybtex format.
    :param search_string: String to search for.
    :return: List of possible matches of publications with their score.
    """
    results = []
    for _, entry in bib.entries.items():
        if 'author' in entry.persons:
            authors = entry.persons['author']
            author_names = " and ".join([str(author) for author in authors])
        elif 'organization' in entry.fields:
            author_names = str(entry.fields["organization"])
        else:
            author_names = ""
        inp = "{}:{}".format(author_names, entry.fields["title"])
        score = bibtex_dblp.search.search_score(inp, search_string)
        if score > 0.5:
            results.append((entry, score))
    results.sort(key=lambda tup: tup[1], reverse=True)
    return results


def print_entry(bib_entry):
    """
    Print pybtex entry.
    :param bib_entry: Pybtex entry.
    :return: String.
    """
    if 'author' in bib_entry.persons:
        authors = ", ".join([str(author) for author in bib_entry.persons['author']])
    elif 'organization' in bib_entry.fields:
        authors = str(bib_entry.fields["organization"])
    else:
        authors = ""
    book = ""
    if 'booktitle' in bib_entry.fields:
        book = bib_entry.fields['booktitle']
    if 'volume' in bib_entry.fields:
        book += " ({})".format(bib_entry.fields['volume'])
    return "{}:\n\t{} {} {}".format(authors, bib_entry.fields['title'], book, bib_entry.fields['year'])
