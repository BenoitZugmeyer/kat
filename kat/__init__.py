import sys
import urllib.parse
import re
from collections import namedtuple
import subprocess

import click
from pyquery import PyQuery as pq

from . import tableformatter


SEARCH_URL = 'http://kasssto.come.in/usearch/{}/?field=seeders&sorder=desc'


def sanitize_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def iter_tree(el):
    yield el

    for e in el:
        yield from iter_tree(e)


def iter_text(el):
    for el in iter_tree(el):

        text = el.text or ''

        # if el.attrib.get('class') == 'red':
        #     text = click.style(text, bold=True, fg='red')

        text += el.tail or ''

        yield text


def get_text(el):
    return sanitize_text(''.join(iter_text(el)))


Result = namedtuple('Result', [
    'title',
    'size',
    'age',
    'seed',
    'leech',
    'magnet'
])


def search(d):

    for line in d('.data > tr'):
        line = d(line)

        title = line('.torrentname .cellMainLink')
        if not title:
            continue

        tds = line('td')

        size, _, unit = get_text(tds[1]).partition(' ')
        yield Result(
            title=get_text(title[0]),
            size='%.02f %s' % (float(size), unit),
            age=get_text(tds[3]),
            seed=get_text(tds[4]),
            leech=get_text(tds[5]),
            magnet=line('.imagnet')[0].attrib['href'],
        )


@click.command()
@click.argument('query', nargs=-1)
def cli(query):
    if not query:
        print('Please set a query')
        sys.exit(1)

    url = SEARCH_URL.format(urllib.parse.quote(' '.join(query)))
    d = pq(url=url)

    results = list(search(d))

    if not results:
        click.echo('No result')
        return

    f = tableformatter.TableFormatter()
    f.max_width, f.height = click.get_terminal_size()
    f.whitespace = re.compile(r'(\s|\.)+')
    f.add_column('#', align='>')
    f.add_column('Title')
    f.add_column('Size', align='>')
    f.add_column('Age', align='<')
    f.add_column('Seed', align='>')
    f.add_column('Leech', align='>')
    click.echo(f.dumps((
        index + 1,
        r.title,
        r.size,
        r.age,
        r.seed,
        r.leech,
    ) for index, r in enumerate(results)))

    while True:
        index = click.prompt('Choose?', type=int, default=1) - 1
        if 0 <= index < len(results):
            break
        click.echo('Not found')

    result = results[index]
    click.echo('Downloading %s...' % result.title)
    subprocess.check_call(['xdg-open', results[index].magnet])
