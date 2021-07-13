#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" ShaZam  can calculate a file sum and compare with a given one.
ShaZam as also other options like:
	calculate all supported hashsums of one file
	read a file with hash sum and filename inside
	calculate only the file sum without compare it
Prerequesites:
	python version 3.2.x or higher
	termcolor version 1.1.x or higher (can install it with pip3 or conda)
	alive_progress version 1.6.x or higher (can install it with pip3 or conda)
"""
__author__ = "Anaxímeno Brito"
__version__ = '0.4.6-beta'
__license__ = "GNU General Public License v3.0"
__copyright__ = "Copyright (c) 2020-2021 by " + __author__
from common import File, TextFile, Process, Errors, get_hashtype
import argparse
import sys


class MainFlow(object):
	"""Organizes the program's processing flow."""

	__slots__ = ["args", "subarg", "_process"]
	def __init__(self, args):
		self.args = args
		self._process = Process()

		if not args.subparser:
			Errors.print_error("No Subcommands were received!")

		self.subarg = args.subparser

	def make_process(self):
		"""Performs specific processing depending on the arguments."""
		if self.subarg == 'check':
			self._process.checkfile(
				file=File(self.args.FILE, self.args.HASH_SUM),
				hashtype=self.args.type, verbosity=self.args.no_verbose)
		elif self.subarg == 'calc':
			files = [File(fname) for fname in self.args.FILES]

			if self.args.type != 'all':
				self._process.calculate_sum(
					files=files, verbosity=self.args.no_verbose,
					hashtype=self.args.type)
				if self.args.write:
					self._process.write(files, self.args.type, self.args.name)
			else: 
				self._process.totalcheck(files)
		elif self.subarg == 'read':
			textfile = TextFile(self.args.filename)
			contents = textfile.read_content()
			if len(contents) == 1:
				fsum, fname = contents[0]
				self._process.checkfile(
					file=File(fname, fsum),
					hashtype=self.args.type or get_hashtype(self.args.filename),
					verbosity=self.args.verbose)
			else:
				self._process.checkfiles(
					files=[File(fname, fsum) for fsum, fname in contents], 
					hashtype=self.args.type or get_hashtype(self.args.filename),
					verbosity=self.args.verbose)


if __name__ == '__main__':
	hash_types = Process.HASHTYPES_LIST+['all']

	parser = argparse.ArgumentParser(
		prog="shazam",
		usage='%(prog)s {sub-command}',
		epilog='SHAZAM *License* %s' % __license__
	)
	parser.add_argument("--version",
		help="print the current version of this program", action='version',
		version='%(prog)s {}'.format(__version__)
	)

	# Stores all subparsers
	subparser = parser.add_subparsers(dest='subparser', title='Sub Commands')

	# Positional arguments for check and compare hashsums
	check = subparser.add_parser('check',
		help="check and Compare the file's hash sum",
		description="Verifies the integrity of the file.",
		usage='shazam check HASH_SUM FILE {--type/-t}'
	)
	check.add_argument("-t", "--type", help=f"The type of hash sum, it must be one these: {Process.HASHTYPES_LIST}",
		choices=Process.HASHTYPES_LIST, metavar='TYPE', required=True)
	#check.add_argument("hashtype", choices=Process.HASHTYPES_LIST)
	check.add_argument("HASH_SUM", help="file's hash sum")
	check.add_argument("FILE", help="file's full or relative location")
	check.add_argument("--no-verbose", "--noverbose",
		action='store_false'
	)

	# Positional arguments for only calculate hashsums
	calc = subparser.add_parser('calc',
		help='calculates and show the hash sum',
		usage='shazam calc {-t/--type} FILES (...)',
		description='Calculates and show the hash sum.'
	)
	calc.add_argument("-t", "--type", help=f"The type of hash sum, it must be one these: {hash_types}",
		choices=hash_types, metavar='TYPE')
	# calc.add_argument('hashtype', choices=Process.HASHTYPES_LIST+['all'])
	calc.add_argument("-w", "--write", action='store_true',
		help='Saves all calculated hash sums inside one file'
	)
	calc.add_argument("--no-verbose", "--noverbose",
		action='store_false'
	)
	calc.add_argument('-n', '--name', metavar='NAME',
		help='Use this with the argument --write for determining the file\'s name.'
	)
	calc.add_argument('FILES', nargs='+',
		help="One or more files for calculating the hash sums"
	)

	# Positional arguments for reading a file which
	# has the file sum and names wrote in.
	read = subparser.add_parser('read',
		help='read a file with hash sum and filename inside',
		description='Read a file with hash sum and filename inside.',
		usage='shazam read [-h/--help] [--verbose] filename'
	)
	read.add_argument('filename',
		help="file to read in, and check the hash sum of the files inside"
	)
	read.add_argument('--verbose',
		action='store_true', help="verbose option"
	)
	read.add_argument('-t', '--type', metavar='', choices=Process.HASHTYPES_LIST,
		help='This can be used to specify the hashtype if it was not recognized in the file\'s name.'
	)

	if len(sys.argv) > 1:
		mf = MainFlow(parser.parse_args()) #TODO: add args --type/-t for determining the type of sum wanted!
		mf.make_process()
		# print('\n')
	else:
		print("usage: shazam [-h] [--version] {Sub-Command}")
		print("       shazam --help         display the help section and exit")
		print("       shazam --version      display the Version information and exit")
