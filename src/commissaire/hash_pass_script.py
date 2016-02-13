# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Utility to help generate bcrypt hashes.
"""

import argparse
import getpass
import sys

import bcrypt


def main():
    """
    Generates a bcrypt hash for a given password.
    """
    parser = argparse.ArgumentParser(
        description='bcrypt based password hasher.',
    )
    parser.add_argument('-r', '--rounds', type=int, default=12, help='')
    parser.add_argument(
        '--pwfile', type=argparse.FileType('r'), required=False,
        help='Reads password from a file instead of prompting.')
    args = parser.parse_args()

    password = None
    if args.pwfile:
        password = args.pwfile.readline().strip()
    else:
        password = getpass.getpass()

    hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=args.rounds))
    sys.stdout.write('{0}\n'.format(hashed))


if __name__ == '__main__':  # pragma no cover
    main()
