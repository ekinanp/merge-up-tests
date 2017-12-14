import json
import os

# The TimingResults object encapsulates the following structure:
#    { test_file => { host => timing_tree } }
# where the host should be a hash of its platform and name
class TimingResults(object):
    @staticmethod
    def add_host(host, timing_trees_json_path, **kwargs):
        timing_trees = json.load(open(timing_trees_json_path))
        timing_trees_new_format = { 'host' : host, 'timing_trees' : timing_trees }
        
        output_file = kwargs.get("output_file", None)
        if output_file is None:
            (directory, basename) = os.path.split(timing_trees_json_path)
            output_file = os.path.join(directory, "%s-%s" % (host['name'], basename))

        with open(output_file, 'w') as f:
            f.write(json.dumps(timing_trees_new_format, sort_keys=True, indent=2, separators=(",", ": ")))

    def __init__(self, *result_files):
        self.results = {}
        for result_file in result_files:
            parsed_result = json.load(open(result_file, 'r'))
            host = parsed_result['host']
            for timing_tree in parsed_result['timing_trees']:
                test_file = timing_tree['test_file']
                if self.results.get(test_file, None) is None:
                    self.results[test_file] = {}
                self.results[test_file][host] = timing_tree
