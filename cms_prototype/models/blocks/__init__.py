import os

dname = os.path.dirname(os.path.abspath(__file__))

mods = []
for fn in os.listdir(dname):
    name, ext = os.path.splitext(os.path.basename(fn))
    if ext not in ('.py', '.pyc', '.so', '.pyo', '.pyd'):
        continue
    if name not in mods and name != '__init__':
        mods.append(name)

for mod in mods:
    __import__('cms_prototype.models.blocks.' + mod)
