import boto3


def get_boto3_client(resource, region, acces_key_id, secret_access_key):
    client = boto3.client(
        resource,
        region_name=region,
        aws_access_key_id=acces_key_id,
        aws_secret_access_key=secret_access_key
    )
    return client


def delete_user(operation_parameters, organization, region):
    # Create IAM client
    client = get_boto3_client('identitystore', region, organization)

    deleteResponse = client.delete_user(**operation_parameters)

    return deleteResponse


def get_identitystore_id(organization, region):
    client = get_boto3_client('sso-admin', region, organization)
    identitystore = client.list_instances()
    id = identitystore['Instances'][0]['IdentityStoreId']
    return id


def describe_user(userId, organization, region):
    client = get_boto3_client('identitystore', region, organization)
    identitystore = get_identitystore_id(organization)
    response = client.describe_user(
        IdentityStoreId=identitystore, UserId=userId)
    return response


def create_user(userEmail, firstName, surnames, organization, region):
    client = get_boto3_client('identitystore', region, organization)
    identitystore = get_identitystore_id(organization)
    display_name = f'{firstName} {surnames}'

    response = client.create_user(
        IdentityStoreId=identitystore,
        UserName=userEmail,
        DisplayName=display_name,
        Name={
            'FamilyName': firstName,
            'GivenName': surnames
        },
        Emails=[
            {
                'Value': userEmail,
                'Type': 'Work',
                'Primary': True
            }
        ]
    )
    return response


def pagination(action, operation_parameters, organization, region):
    # Create IAM client
    client = get_boto3_client('identitystore', region, organization)

    paginator = client.get_paginator(action)
    page_iterator = paginator.paginate(**operation_parameters)

    return page_iterator
