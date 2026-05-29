import importlib
import sys

# Proxy package so tests that import 'Componentes' work when app is located at 'vet3.Componentes'
mod = importlib.import_module('vet3.Componentes')
sys.modules['Componentes'] = mod
