
functions = [
    {
        'name': 'fcall_vcf_transform_from_files',
        'description': 'Transforms VCF files into the input format of pyclone_vi (mutation clustering)',
        'parameters': {
            'type': 'object',
            'properties': {
                'vep_vcf': {
                    'type': 'string',
                    'description': 'The path to the vcf_file'
                },
            },
            'required': ['vcf_file']
        }
    },
    {
        'name': 'fcall_pyclone_vi_from_files',
        'description': 'Computes mutation clusters from vcf_transformed file',
        'parameters': {
            'type': 'object',
            'properties': {
                'pyclone_vi_formatted': {
                    'type': 'string',
                    'description': 'The path to the pyclone_vi_formatted file outputed by the vcf_transform'
                },
            },
            'required': ['pyclone_vi_formatted']
        }
    },
    {
        'name': 'fcall_pyclone_vi_from_futures',
        'description': 'Computes mutation clusters from an vcf_transform AppFuture id',
        'parameters': {
            'type': 'object',
            'properties': {
                'vcf_future_id': {
                    'type': 'string',
                    'description': 'The vcf_transform id'
                },
            },
            'required': ['vcf_future_id']
        }
    }
]
