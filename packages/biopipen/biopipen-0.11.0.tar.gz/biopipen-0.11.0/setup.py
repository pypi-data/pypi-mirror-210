# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biopipen',
 'biopipen.core',
 'biopipen.ns',
 'biopipen.scripts.bam',
 'biopipen.scripts.bcftools',
 'biopipen.scripts.bed',
 'biopipen.scripts.cnvkit',
 'biopipen.scripts.csv',
 'biopipen.scripts.gene',
 'biopipen.scripts.misc',
 'biopipen.scripts.tcgamaf',
 'biopipen.scripts.vcf',
 'biopipen.scripts.web',
 'biopipen.utils']

package_data = \
{'': ['*'],
 'biopipen': ['reports/bam/*',
              'reports/cnv/*',
              'reports/cnvkit/*',
              'reports/gsea/*',
              'reports/scrna/*',
              'reports/scrna_metabolic_landscape/*',
              'reports/tcr/*',
              'reports/utils/*',
              'reports/vcf/*',
              'scripts/cnv/*',
              'scripts/gsea/*',
              'scripts/plot/*',
              'scripts/rnaseq/*',
              'scripts/scrna/*',
              'scripts/scrna_metabolic_landscape/*',
              'scripts/tcr/*']}

install_requires = \
['cmdy>=0.5,<0.6',
 'datar[pandas]>=0.12,<0.13',
 'pipen-args>=0.9,<0.10',
 'pipen-board>=0.2,<0.3',
 'pipen-cli-run>=0.8,<0.9',
 'pipen-filters>=0.7,<0.8',
 'pipen-report>=0.9,<0.10',
 'pipen-verbose>=0.6,<0.7',
 'pipen>=0.9,<0.10']

entry_points = \
{'pipen_cli_run': ['bam = biopipen.ns.bam',
                   'bcftools = biopipen.ns.bcftools',
                   'bed = biopipen.ns.bed',
                   'cnv = biopipen.ns.cnv',
                   'cnvkit = biopipen.ns.cnvkit',
                   'cnvkit_pipeline = biopipen.ns.cnvkit_pipeline',
                   'csv = biopipen.ns.csv',
                   'gene = biopipen.ns.gene',
                   'gsea = biopipen.ns.gsea',
                   'misc = biopipen.ns.misc',
                   'plot = biopipen.ns.plot',
                   'rnaseq = biopipen.ns.rnaseq',
                   'scrna = biopipen.ns.scrna',
                   'scrna_basic = biopipen.ns.scrna_basic',
                   'scrna_metabolic_landscape = '
                   'biopipen.ns.scrna_metabolic_landscape',
                   'tcgamaf = biopipen.ns.tcgamaf',
                   'tcr = biopipen.ns.tcr',
                   'vcf = biopipen.ns.vcf',
                   'web = biopipen.ns.web']}

setup_kwargs = {
    'name': 'biopipen',
    'version': '0.11.0',
    'description': 'Bioinformatics processes/pipelines that can be run from `pipen run`',
    'long_description': 'None',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
