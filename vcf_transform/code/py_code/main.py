import sys
import vcf
import json
from pathlib import Path

import py_code.mutation as mutation
from py_code.mutation import Mutation

def main(args):
    success = False
    print("main.py: got the args: " + str(args))

    vcf_type:str = args[0]
    if vcf_type not in ['mutect', 'moss']:
        raise Exception('Can only understand vcf from mutect or moss')

    vcf_fn:str = args[1]
    header_json_out_fn = args[2]
    mutations_json_out_fn = args[3]
    pyclone_vi_out_fn = args[4]
    pyclone_out_dirname = args[5]

    vcf_reader:vcf.Reader = load_vcf(vcf_fn)

    write_headers_as_json(vcf_reader, header_json_out_fn)

    sample_id = extract_sample_id(vcf_fn)

    if vcf_type == 'mutect':
        mutations = Mutation.mutation_list_from_mutect(sample_id, vcf_reader)
    elif vcf_type == 'moss':
        mutations = Mutation.mutation_list_from_moss(sample_id, vcf_reader)

    mutation.write_mutations_json(mutations_json_out_fn, mutations)
    mutation.write_pyclone_vi_input(pyclone_vi_out_fn, mutations)
    mutation.write_pyclone_inputs(pyclone_out_dirname, mutations)

    success = True
    return success

def load_vcf(vcf_fn:str) -> vcf.Reader:
    """ 
    given the filename of a vcf, returns a Reader object that is an
    iterator over the rows in the file (yields vcf._Record objects)
    """
    reader = vcf.Reader(open(vcf_fn, 'r'))
    return reader

def extract_sample_id(input_filename):
    """
    infers a sample_id from the input filename of the vcf file.
    The result is the basename without the suffix (.vcf)
    """
    p = Path(input_filename)
    sample_id = (p.stem)
    return sample_id

def extract_sample_id_from_header(vcf_reader: vcf.Reader):
    """
    infers a sample_id from the header of the vcf file.
    """
    sample_id = vcf_reader.metadata["tumor_sample"]
    return sample_id

def pp_jsons(jdata) -> str:
    """
    convert a data structure to json and create a pretty print string.
    works best on nested dicts/lists/primitives.
    """
    s = json.dumps(jdata, indent=4)
    return s
  

def write_headers_as_json(vcf_reader:vcf.Reader, fn_out:str) -> None:
    """
    Once the vcf if loaded, put all the metadata from the header into
    a single json object and pretty print it to a file.
    Has no effect on the Reader but creates a new file
    """
    header_json = dict()

    header_json["metadata"] = vcf_reader.metadata
    header_json["infos"] =   vcf_reader.infos
    header_json["filters"] = vcf_reader.filters
    header_json["formats"] = vcf_reader.formats
    header_json["samples"] = vcf_reader.samples

    print("writing header info as json to : " + str(fn_out))
    with open(fn_out, 'w') as outfile:
        json.dump(header_json, outfile, indent=4)
    return



if __name__ == "__main__":
    succeeded = main(sys.argv[1:])

    if succeeded:
        exit_code = 0
    else:
        exit_code = 1

    sys.exit(exit_code)
