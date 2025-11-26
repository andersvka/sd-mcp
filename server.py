"""
TEST
FastMCP slaktdata Server
"""

from fastmcp import FastMCP
import requests
import simplejson

# Create server
mcp = FastMCP("slaktdata")

@mcp.tool
def search_persons(
    text: str,                             # Required - no default value
    födda: bool | None = None,             # Optional - can be None
    vigda: bool | None = None,             # Optional - can be None
    döda: bool | None = None,              # Optional - can be None
    husförhör: bool | None = None,         # Optional - can be None
    in_ut_flyttning: bool | None = None,   # Optional - can be None
    bouppteckning: bool | None = None,     # Optional - can be None
    mantalsskrivning: bool | None = None,  # Optional - can be None
    dombok: bool | None = None,            # Optional - can be None
) -> list[dict]:
    """Sök register, avskrivna kyrkböcker hos släktdata

    Args:
        text: All sökbar text, namn, datum, plats
        födda: Födelse och dop böcker, CI
        vigda: Vigselbok, EI
        döda: Dödbok, FI
        husförhör: Husförhörslängd eller församlingsbok, AI, AII
        in_ut_flyttning: Flyttlängd BI, BII
        bouppteckning: Bouppteckningar
        mantalsskrivning: Mantalsskrivningslängder
        dombok: Domböcker

    Returns:
        Lista av matchande personer, varje representerad som ett JSON dictionary.
        Om inga matchningar är hittade, returneras en tom lista.
    """
    reglist = []
    reglist.append('rtypff=true') if födda else reglist.append('rtypff=false')
    reglist.append('rtypfv=true') if vigda else reglist.append('rtypfv=false')
    reglist.append('rtypfd=true') if döda else reglist.append('rtypfd=false')
    reglist.append('rtypfh=true') if husförhör else reglist.append('rtypfh=false')
    reglist.append('rtypfiu=true') if in_ut_flyttning else reglist.append('rtypfiu=false')
    reglist.append('rtypfb=true') if bouppteckning else reglist.append('rtypfb=false')
    reglist.append('rtypfm=true') if mantalsskrivning else reglist.append('rtypfm=false')
    reglist.append('rtypfj=true') if dombok else reglist.append('rtypfj=false')
    regs = '&'.join(reglist)
    if not text or not regs:
        return []
    typ_map = {'F': 'födda', 'V': 'vigda', 'D': 'döda', 'H': 'husförhör',
               'I': 'in_ut_flyttning', 'B': 'bouppteckning', 'M': 'mantalsskrivning', 'J': 'dombok'}
    url = f"https://www.slaktdata.org/getFreetextRows.php?maxres=2&term={text}&{regs}"
    r = requests.get(url)
    hits = simplejson.loads(r.text)
    return [{"r": r, "URL": url}]
    #return [{"name": x['namn'], "score": x['score'], "id": x['id']} for x in hits]
    result = []
    for pers in hits:
        person = {
            "id": pers['id'],
            "name": pers['namn'],
        }
        result.append(person)
    return result


@mcp.tool
def person_by_id(id: str) -> dict | None:
    """Return record by id.
    
    Args:
        id: Record ID
    """
    url = f"https://www.slaktdata.org/?p=getregbyid&sldid={id}"
    r = requests.get(url)
    hit = simplejson.loads(r.text)['res']
    result = {}
    if hit:
      result = {
        "id": id,
        'source': hit.get('kalla', ''),
        'place_married': hit.get('fsg', ''),
        'id': f"{hit.get('scbkod', '')}_{hit.get('sdsuffix', '')}_{hit.get('lopnr', '')}",
        'date_married': hit.get('vdatum', ''),
        'spouse_1_title': hit.get('mtitel', ''),
        'spouse_1_first_name': hit.get('mfnamn', ''),
        'spouse_1_last_name': hit.get('menamn', ''),
        'spouse_1_address': f"{hit.get('madress', '')}, {hit.get('nmadress', '')}",
        'spouse_2_title': hit.get('ktitel', ''),
        'spouse_2_first_name': hit.get('kfnamn', ''),
        'spouse_2_last_name': hit.get('kenamn', ''),
        'spouse_2_address': f"{hit.get('kadress', '')}, {hit.get('nkadress', '')}",
      }
    return result

#print(search_persons('anders palm'))

