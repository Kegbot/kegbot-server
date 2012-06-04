import os
import sys
from tempfile import mkdtemp

from paver.easy import *
import paver.doctools
from paver.virtual import bootstrap

# Import the setup.py module for configuration
sys.path.insert(0, os.path.dirname(__file__))
try:
  kegbot = __import__("setup")
finally:
  sys.path.pop()

CAN_SKIP = False
VENV_DIR = "virtualenv"

options(
  bootstrap = Bunch(bootstrap_dir = VENV_DIR),
  virtualenv = Bunch(
      packages_to_install = kegbot.DEPENDENCIES,
      no_site_packages = True,
      script_name = os.path.join(VENV_DIR, 'bootstrap.py'),
      dest_dir = VENV_DIR,
      #paver_command_line = '_init',
  )
  #setup = kegbot.SETUP
)

@task
def _bootstrap(options):
  """Create virtualenv in ./virtualenv"""
  print("Calling bootstrap")
  bs = path(options.bootstrap_dir)
  if not bs.exists:
    bs.mkdir()

  call_task('paver.virtual.bootstrap')
  sh('%s %s' % (sys.executable, options.virtualenv.script_name))

@task
def clean_all():
  bs = path(options.bootstrap_dir)
  if bs.exists:
    bs.rmtree()

@task
def gaedist():
  """Build a Google AppEngine source distribution based on setup.py.

  The setup involves several steps:
    * create a distribution directory with the kegbot source code
    * generate the dependency sources from setup.py
    * copy the required libraries into the dist directory
  """
  venv = path(VENV_DIR)
  if venv.exists and CAN_SKIP:
    print("Skipping bootstrap. Virtualenv already installed")
  else:
    call_task('_bootstrap')

  srcdir = path('src')
  outdir = path('appengine')

  # Cleanup the old distribution and copy the source again
  outdir.rmtree()
  #srcdir.copytree(outdir)
  (outdir / 'kegbot.egg-info').rmtree() # remove the egg-info directory
  (venv / "lib" / "python2.7" / "site-packages" / "PIL-1.1.7-py2.7-macosx-10.7-intel.egg").rmtree()

  libs = venv / "lib/python2.7/site-packages"
  for p in libs.dirs():
    for dep in p.glob("*"):
      name = dep.basename()
      if name in ['man', 'EGG-INFO', 'pykeg']:
        continue
      #print(dep)
      dep.copytree(outdir / name)


  for d in outdir.dirs():
    (srcdir / d.basename()).rmtree()
    d.move(srcdir)
