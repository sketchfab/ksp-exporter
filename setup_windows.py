from distutils.core import setup
import py2exe

setup(
    console=['ksp2sketchfab.py'],
    options= {
        'py2exe': {
            'includes': ['requests', 'PyQt4', 'sip']
            }
        }
    )
