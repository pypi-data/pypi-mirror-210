#!/usr/bin/env python3

'''Query the latest Ubuntu AMIs from cloud-images.ubuntu.com.

For when you'd rather not hard-code an AMI ID.

# find the latest Jammy Jellyfish AMI for amd64 and hvm:ebs-ssd in London
ami_id = ubami.find(region='eu-west-2',
                    version='22.04 LTS',
                    arch='amd64',
                    instance_type='hvm:ebs-ssd')[0]['ami_id']

# fetch a list of all the latest official Ubuntu AMIs
ami_list = ubami.list()
'''

__version__ = '0.1.0'

import json
import re

import click
import httpx

__all__ = ['list', 'find']


def list():
    '''Get the current list of Ubuntu AMIs from cloud-images.ubuntu.com.'''

    r = httpx.get('https://cloud-images.ubuntu.com/locator/ec2/releasesTable')
    r.raise_for_status()

    data = json.loads(r.text.replace(',\n]', '\n]'))['aaData']
    keys = ('region', 'name', 'version', 'arch', 'instance_type', 'release',
            'ami_id', 'aki_id')

    def to_dict(item):
        item = dict(zip(keys, item))
        item['ami_id'] = re.sub(r'<[^>]+>', '', item['ami_id'])
        return item

    return [item for item in map(to_dict, data)]


def find(region=None, name=None, version=None, arch=None, instance_type=None,
         release=None, ami_id=None, aki_id=None):
    '''Find AMIs that match the given parameters.'''

    q = {k: v for k, v in locals().items() if v is not None}

    def match(item):
        return not any([item.get(k) != v for k, v in q.items()])

    return [item for item in filter(match, list())]


@click.command()
@click.option('--region')
@click.option('--name')
@click.option('--version')
@click.option('--arch')
@click.option('--instance-type')
@click.option('--release')
@click.option('--ami-id')
@click.option('--aki-id')
def main(**kwargs):
    try:
        click.echo(json.dumps([ami for ami in find(**kwargs)], indent=2))
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == '__main__':
    main()
