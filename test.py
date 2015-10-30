import pickle

from interface import GCEInterface

interface = GCEInterface()

interface.create_and_connect_all()

# This pickled Configuration was obtained from a sample Rosenbrock run.
config = "ccopy_reg\n_reconstructor\np0\n(copentuner.resultsdb.models\nConfiguration\np1\nc__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nS'hash'\np6\nV83ac1831a07641c427034456f55959439a51d0c5ac70cabed19a6dd935b96adf\np7\nsS'_sa_instance_state'\np8\ng0\n(csqlalchemy.orm.state\nInstanceState\np9\ng2\nNtp10\nRp11\n(dp12\nS'class_'\np13\ng1\nsS'committed_state'\np14\n(dp15\nsS'instance'\np16\ng4\nsS'manager'\np17\ng0\n(csqlalchemy.orm.instrumentation\n_SerializeManager\np18\ng2\nNtp19\nRp20\n(dp21\nS'class_'\np22\ng1\nsbsS'key'\np23\n(g1\n(I1021\ntp24\ntp25\nsS'expired_attributes'\np26\nc__builtin__\nset\np27\n((lp28\ntp29\nRp30\nsbsS'data'\np31\n(dp32\nI0\nF5.975213959409189\nsI1\nF-203.1835732791592\nssS'id'\np33\nI1021\nsS'program_id'\np34\nI1\nsb."

# This pickled input was obtained from a sample Rosenbrock run.
c_input = "ccopy_reg\n_reconstructor\np0\n(copentuner.resultsdb.models\nInput\np1\nc__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nS'_sa_instance_state'\np6\ng0\n(csqlalchemy.orm.state\nInstanceState\np7\ng2\nNtp8\nRp9\n(dp10\nS'class_'\np11\ng1\nsS'modified'\np12\nI00\nsS'committed_state'\np13\n(dp14\nsS'instance'\np15\ng4\nsS'manager'\np16\ng0\n(csqlalchemy.orm.instrumentation\n_SerializeManager\np17\ng2\nNtp18\nRp19\n(dp20\nS'class_'\np21\ng1\nsbsS'parents'\np22\n(dp23\nI140694690707408\ng0\n(g7\ng2\nNtp24\nRp25\n(dp26\ng11\ncopentuner.resultsdb.models\nInputClass\np27\nsg12\nI00\nsg13\n(dp28\nsg15\ng0\n(g27\ng2\nNtp29\nRp30\n(dp31\nS'size'\np32\nI-1\nsg6\ng25\nsS'name'\np33\nVfixed\np34\nsS'program_id'\np35\nI1\nsS'id'\np36\nI1\nsbsg16\ng0\n(g17\ng2\nNtp37\nRp38\n(dp39\ng21\ng27\nsbsS'key'\np40\n(g27\n(I1\ntp41\ntp42\nsS'expired_attributes'\np43\nc__builtin__\nset\np44\n((lp45\ntp46\nRp47\nsS'expired'\np48\nI00\nsbssg40\n(g1\n(I8\ntp49\ntp50\nsg43\ng44\n((lp51\ntp52\nRp53\nsg48\nI00\nsbsS'extra'\np54\nNsS'input_class'\np55\ng30\nsS'input_class_id'\np56\nI1\nsS'path'\np57\nNsg36\nI8\nsb."

# This limit value was obtained from a sample Rosenbrock run.
limit = 1254.78722859

requests = [(pickle.loads(config), pickle.loads(c_input), limit)] * 16

results = interface.compute_results(requests)

for result in results:
    print result.time

interface.delete_all()
