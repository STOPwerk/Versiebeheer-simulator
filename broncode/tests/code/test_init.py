#======================================================================
# Importeer deze module vanuit elke test_*.py unit test module
#
# Deze module breidt het pad uit zodat de modules in Applicatie.code
# gevonden worden via de import. Om intellisense in de editor
# te laten werken moeten de imports vanuit de test_*.py module
# wel via "import Applicatie.code.naam" gedaan worden.
#======================================================================
import os.path
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append (os.path.join (project_dir, 'simulator'))
