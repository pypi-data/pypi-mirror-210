from difflib import SequenceMatcher


def search(query: str, lst: list, match_case=True):
    """
    Searches a list of strings and returns them sorted by similarity to a query string.

    Parameters
    ----------
    query : str
        The string to search for in the list.

    lst : list
        The list of strings to search.

    match_case : bool, optional
        If True (default), the search is case-insensitive.
        If False, the search is case-sensitive.

    Returns
    -------
    list
        A list of strings from 'lst', sorted by their similarity to 'query', with the most similar first.
    """
    if match_case:
        query_lower = query.lower()
        sims = [SequenceMatcher(None, query_lower, i.lower()).ratio() for i in lst]
    else:
        sims = [SequenceMatcher(None, query, i).ratio() for i in lst]
    return [i for _, i in sorted(zip(sims, lst), reverse=True)]
