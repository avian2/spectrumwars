# Copyright (C) 2015 SensorLab, Jozef Stefan Institute http://sensorlab.ijs.si
#
# Written by Tomaz Solc, tomaz.solc@ijs.si
#
# This work has been partially funded by the European Community through the
# 7th Framework Programme project CREW (FP7-ICT-2009-258301).
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/

# This is an ugly work-around so that some tests will run even if
# some dependencies are missing.
#
# The basic problem is that TestLoader.loadTestsFromName() fails badly if a
# test module has a bad "import" line. We try to catch this error and
# substitute a dummy test in place of an unrunnable module.
from unittest import TestCase
from setuptools.command.test import ScanningLoader

class Loader(ScanningLoader):
	def loadTestsFromName(self, name, *args, **kwargs):
		try:
			return super(Loader, self).loadTestsFromName(name, *args, **kwargs)
		except AttributeError, e:
			if "'module' object has no attribute" in str(e):
				print "skipping %s" % (name,)
				# just return an empty TestCase in place of a module
				# we can't load
				return self.loadTestsFromTestCase(TestCase)
			else:
				raise
