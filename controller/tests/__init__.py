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
