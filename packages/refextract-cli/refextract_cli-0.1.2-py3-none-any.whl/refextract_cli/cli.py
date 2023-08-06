#!/usr/bin/python3
import refextract
import argparse
import urllib.parse
import shutil
import sqlite3
import hashlib
import json

from rich import print, traceback
from pathlib import Path

# Constants
URL_ESCAPE_CHARACTERS = r'/:&=?~#+!$,;\'@()*[]'
DB_PATH = Path.home() / '.config' / 'refextract' / 'references-cache.db'
MAX_CACHE_SIZE = 200

# sqlite3 cache class
class RefCache:
    def __init__(self, db_path):
        self.db_path = db_path

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self 

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

    def get(self, checksum):
        self.cursor.execute('SELECT * FROM pdf_refs WHERE checksum = ?', (checksum,))
        return self.cursor.fetchone()

    def insert(self, checksum, references):
        # check if cache is full
        self.cursor.execute('SELECT COUNT(*) FROM pdf_refs')
        count = self.cursor.fetchone()[0]
        if count >= MAX_CACHE_SIZE:
            self.cursor.execute('DELETE FROM pdf_refs WHERE timestamp = (SELECT MIN(timestamp) FROM pdf_refs)')

        self.cursor.execute('INSERT INTO pdf_refs (checksum, refs) VALUES (?, ?)', (checksum, references))

    @staticmethod
    def create_db(db_path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE IF NOT EXISTS pdf_refs (checksum TEXT PRIMARY KEY, refs TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
        conn.commit()
        conn.close()

        return RefCache(db_path)

# file checksum shorthand (md5)
def file_checksum(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

cache = None
try:
    cache = RefCache.create_db(DB_PATH)
    print(f'Using cache database at {DB_PATH}')
except Exception as e:
    print("Couldn't open cache database")
    traceback.pretty.pprint(e)


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Extract references from a source or from the current opened PDF.\n Supported viewers: Okular')

    parser.add_argument('source', metavar='source', type=str, help='The source to extract references from. Accepts path to PDF or URL.', nargs='?')

    # add a flag to create a google scholar link
    parser.add_argument('-g', '--google', action='store_true', help='Create a google scholar link for each reference.')

    # sort flag with year, author and title otions
    parser.add_argument('-s', '--sort', type=str, help='Sort references by year, author or title.')

    # flag for a 'rofi' mode
    parser.add_argument('-r', '--rofi', action='store_true', help='Use rofi to select the reference.')

    args = vars(parser.parse_args())
    
    if args['source'] == None:
        try:
            interactive = not args['rofi']
            args['source'] = get_okular_files(interactive)
            print(f'No source provided. Using current document from Okular: {args["source"]}')
        except Exception as e:
            print(e)
            exit(1)

    
    if args['rofi']:
        # check if rofi is installed
        if not shutil.which('rofi'):
            print('Rofi is not installed.')
            exit(1)

        rofi_references(args['source'])
    else:
        references = get_references(args['source'])
        refs_str = format_references(references)
        for ref in refs_str:
            print(ref)

# get current document from okular
def get_okular_files(interactive=False):
    import dbus
    from xml.dom.minidom import parseString

    # Connect to the Okular DBus interface
    bus = dbus.SessionBus()

    # filter okular interfaces
    interfaces = [ bus for bus in bus.list_names() if bus.startswith('org.kde.okular')]
    if (len(interfaces) == 0):
        raise Exception('No Okular instance found.')
    interface = interfaces[0]

    # introspect the interface
    introspect = dbus.Interface(bus.get_object(interface, "/"), r"org.freedesktop.DBus.Introspectable")

    xml = parseString(introspect.Introspect())

    # get nodes whose name attribute starts with 'okular'
    objs = [node.getAttribute('name') for node in xml.getElementsByTagName('node') if node.getAttribute('name').startswith('okular')]

    opened_files = []
    for obj in objs:
        okular = bus.get_object(interface, f"/{obj}")
        
        try:
            opened_files += [okular.currentDocument()]
        except dbus.DBusException:
            pass

    if (len(opened_files) == 0):
        raise Exception('No opened files found.')
    
    if (len(opened_files) == 1 or not interactive):
        return opened_files[0]
    
    # let the user choose the file in a list
    print('Multiple files opened. Choose one:')
    for i, file in enumerate(opened_files):
        print(f'  [{i + 1}]: {file}')
    
    choice = int(input('Choice: ')) - 1
    return opened_files[choice]


# Check the source type
def get_references(source, sort_key=None):
    references = []

    # Check cache
    if cache:
        checksum = file_checksum(source)
        with cache as c:
            cached = c.get(checksum)
            if cached:
                return json.loads(cached['refs'])

    # Handle url
    if source.startswith('http'):
        references = refextract.extract_references_from_url(source)
    # Handle file
    elif source.endswith('.pdf'):
        references = refextract.extract_references_from_file(source)
    else:
        print('Unknown source type.')

    # try to see if adjacent references complement the missing itens
    # this occurs when the reference is split in two lines
    required_keys = ['author', 'year']
    k = 0
    while k + 1 < len(references):
        missing_keys = set([key for key in required_keys if key not in references[k]])
        present_keys = set([key for key in required_keys if key in references[k]])

        next_ref = references[k + 1]
        next_ref_missing_keys = set([key for key in required_keys if key not in next_ref])
        next_ref_present_keys = set([key for key in required_keys if key in next_ref])

        # check if current and next reference complement each other
        if missing_keys == next_ref_present_keys and present_keys == next_ref_missing_keys:
            references[k].update(next_ref)

            # join the 'raw_ref' key
            references[k]['raw_ref'] = references[k]['raw_ref'] + next_ref['raw_ref']

            references.pop(k + 1)
        
        k += 1
    
    # sort references
    if sort_key:
        references.sort(key=lambda k: k.get(sort_key, [''])[0])

    # save to cache as json
    if cache:
        checksum = file_checksum(source)
        with cache as c:
            c.insert(checksum, json.dumps(references))

    return references

def scholar_link(reference):
    author = ('author' in reference and ', '.join(reference['author'])) or '????'
    year = 'year' in reference and reference['year'][0] or '????'
    raw_ref = (reference['raw_ref'][0]) or '????'
    query_str = f'{raw_ref}'
    if ('author' in reference and 'year' in reference):
        query_str = f'{author} {year}'

    # sanitize the link
    query_str = urllib.parse.quote_plus(query_str, safe='')

    return f'https://scholar.google.com.br/scholar?q={query_str}'

def format_references(references, generate_scholar_link=False): 
    ref_strs = []

    # Pretty print references
    for reference in references:
        author = ('author' in reference and ', '.join(reference['author'])) or '????'
        year = 'year' in reference and reference['year'][0] or '????'
        raw_ref = (reference['raw_ref'][0]) or '????'
        journal_title = ('journal_title' in reference and reference['journal_title']) or '????'

        ref_print = f'[bold]{author}[/bold] ({year}) [bright_black][italic]{raw_ref}[/bright_black]'

        if generate_scholar_link:        
            ref_print += "\n   " + scholar_link(reference)

        ref_strs += [ref_print]

    return ref_strs

def rofi_references(source):
    import subprocess, webbrowser
    
    # display a rofi message while the references are being fetched
    message = f'Found PDF opened in Okular. Fetching references...'
    proc = subprocess.Popen(['rofi', '-e', message], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    references = get_references(source)
    proc.kill()

    # format the references
    ref_str = []
    for reference in references:
        if 'raw_ref' not in reference:
            continue
        raw_ref = (reference['raw_ref'][0]) or '????'
        ref_str += [raw_ref] 
    
    proc = subprocess.Popen(['rofi', '-dmenu', '-i', '-p', 'References'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(input='\n'.join(ref_str).encode())

    if proc.returncode == 0:
        # get the selected reference
        selected_ref = stdout.decode('utf-8').strip()
        if (len(selected_ref) > 0):
            print(f'Opening reference: {selected_ref}')
            ref_idx = ref_str.index(selected_ref)

            if (ref_idx >= 0):
                scholar_url = scholar_link(references[ref_idx])
                webbrowser.open(scholar_url)


if __name__ == "__main__":
    main()
