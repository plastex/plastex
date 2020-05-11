# Fragments from external (other than the current document) files

import csv
import os
from itertools import islice
from typing import NamedTuple

from plasTeX import Command
from plasTeX.Logging import getLogger

log = getLogger()

package_prefix_exports = ['block']

FRAGMENTS_FILE = 'external-fragments.csv'


class FragmentLocus(NamedTuple):
    file_name: str
    begin: int
    end: int


def ProcessOptions(_options, document):
    build_directory = document.config['files']['directory']
    if os.path.isabs(build_directory):
        directory = build_directory
    else:
        working_directory = document.userdata['working-dir']
        directory = os.path.join(working_directory, build_directory)

    fragments_file = os.path.join(directory, FRAGMENTS_FILE)

    try:
        with open(fragments_file, newline='') as csv_file:
            reader = csv.DictReader(
                csv_file,
                fieldnames=['identifier', 'file_name', 'begin', 'end']
            )
            document.userdata['external_fragments'] = {}
            for row in reader:
                identifier = row['identifier']
                file_name = row['file_name']
                begin = int(row['begin']) - 1
                end = int(row['end'])
                document.userdata['external_fragments'][
                    identifier] = (
                    FragmentLocus(file_name, begin, end)
                )
    except OSError:
        log.warning(f'Failed to open {fragments_file} for reading')


class Fragment(NamedTuple):
    language: str
    text: str


class externalfragments_block(Command):
    args = 'identifier:str'
    blockType = True

    @property
    def fragment(self):
        identifier = self.attributes['identifier']
        locus = self.ownerDocument.userdata['external_fragments'][
            identifier
        ]
        file_name, begin, end = locus
        if os.path.splitext(file_name)[1] == '.v':
            language = 'coq'
        else:
            language = 'text'
        with open(file_name) as lines:
            text = ''.join(islice(lines, begin, end)).strip()
        return Fragment(language, text)

# End of file
