# reload(sys)
# sys.setdefaultencoding('utf-8')
import json
import boto3
import base64
from botocore.exceptions import ClientError
from abc import ABC


class Loader(ABC):
    def __init__(self, *args, **kwargs):
        """
        :param credentials: AWS credentials (AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY)
        """
        self._credentials = kwargs.get("credentials", {})

    def get_secrets(self):
        pass


class FileLoader(Loader):
    def get_secrets(self, secret_name):
        try:
            with open(secret_name) as file:
                data = json.load(file)
        except FileNotFoundError:
            return None
        return data


class AwsLoader(Loader):
    def get_aws_key(self):
        myconfig = self._credentials.get("AWS_ACCESS_KEY_ID")
        return myconfig

    def get_aws_region(self):
        myconfig = self._credentials.get("AWS_REGION")
        return myconfig

    def get_aws_secret(self):
        myconfig = self._credentials.get("AWS_SECRET_ACCESS_KEY")
        return myconfig

    def get_secrets(self, secret_name):
        AWS_ACCESS_KEY_ID = self.get_aws_key()
        AWS_SECRET_ACCESS_KEY = self.get_aws_secret()
        AWS_REGION = self.get_aws_region()

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name="secretsmanager",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        secret = ""
        # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
        # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        # We rethrow the exception by default.

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "DecryptionFailureException":
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response["Error"]["Code"] == "InternalServiceErrorException":
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response["Error"]["Code"] == "InvalidParameterException":
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response["Error"]["Code"] == "InvalidRequestException":
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response["Error"]["Code"] == "ResourceNotFoundException":
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            return None
        else:
            # Decrypts secret using the associated KMS key.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if "SecretString" in get_secret_value_response:
                secret = get_secret_value_response["SecretString"]
            else:
                secret = base64.b64decode(get_secret_value_response["SecretBinary"])

        secret = json.loads(secret)
        return secret


# loader_type will define which loader will be used
def get_loader(loader_type):
    if loader_type == "file":
        return FileLoader
    if loader_type == "aws":
        return AwsLoader

    return FileLoader
