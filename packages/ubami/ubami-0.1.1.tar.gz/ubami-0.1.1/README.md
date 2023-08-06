# ubami

A module and CLI for listing and filtering the latest Ubuntu AMIs from
cloud-images.ubuntu.com.

For when you'd rather not hard-code an Ubuntu AMI ID.

## Installation

```
pip install ubami
```

## Usage

```python
# find the latest Jammy Jellyfish AMI for amd64+hvm:ebs-ssd in London
ami_id = ubami.find(region='eu-west-2',
                    version='22.04 LTS',
                    arch='amd64',
                    instance_type='hvm:ebs-ssd')[0]['ami_id']
```

```python
# fetch a list of all the latest official Ubuntu AMIs
ami_list = ubami.list()
```

```bash
ubami --region=eu-west-2 --version='22.04 LTS' --arch=amd64 --instance-type=hvm:ebs-ssd | jq -r '.[0].ami_id'
```
