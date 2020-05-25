import pprint
import yaml

from xmapper.utils import parse


_SKIP_SEARCH = ['', 'null']


class Mapper(object):
    def __init__(self, input, output):
        self.input_obj = parse(input)
        self.output_obj = parse(output)

        # default mapping format
        self.MAPPER = {
            'exact_match': {},
            'multiple_match': {},
            'human_intervention': {}
        }

    def build_mapping(self):
        # not search the items with value '' or null etc
        needles = {k: v for k, v in self.output_obj.value_mapping.items()
                   if v not in _SKIP_SEARCH}

        haystack = {k: v for k, v in self.input_obj.search_mapping.items()
                    if k not in _SKIP_SEARCH}

        # search and build the MAPPER
        for k, v in needles.items():
            if v in haystack:
                if len(haystack[v]) == 1:
                    self.MAPPER['exact_match'][k] = haystack[v][0]
                else:
                    self.MAPPER['multiple_match'][k] = haystack[v]
            else:
                self.MAPPER['human_intervention'][k] = v
        pprint.pprint(self.MAPPER)

    def dump_yaml_config(self, dest_file):
        """
        Saves the default mapping into the dest_file path.
        """
        self.build_mapping()
        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        with open(dest_file, 'w') as d:
            yaml.dump(self.MAPPER, d, default_flow_style=False,
                      indent=4, Dumper=noalias_dumper)


class Comparer(object):
    """
    simple object comparer for local test
    """
    def __init__(self, file_one, file_two):
        self.obj_file_one = parse(file_one)
        self.obj_file_two = parse(file_two)

    def compare(self):
        match = True
        if self.obj_file_one.paths != self.obj_file_two.paths:
            print('Your input xmls have different structure, pls check')
            match = False
        else:
            for path in self.obj_file_one.paths:
                if self.obj_file_one.get_value_by_path(path) \
                        != self.obj_file_two.get_value_by_path(path):
                    print('mismatch found for path: {}'.format(path))
                    match = False
        return match
