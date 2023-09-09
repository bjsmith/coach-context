import boto3
from chat import ChatConfig
from botocore.exceptions import NoCredentialsError




import boto3
from botocore.exceptions import NoCredentialsError

class S3BucketInterface:

    def __init__(self, access_key, secret_key, bucket):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.region_name = 'us-east-1'

    def _get_s3_object(self):
        return boto3.client('s3',
                            aws_access_key_id=self.access_key,
                            aws_secret_access_key=self.secret_key,
                            region_name=self.region_name)

    def upload_file(self, local_file, s3_file):
        s3 = self._get_s3_object()
        try:
            s3.upload_file(local_file, self.bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def file_exists(self, s3_file):
        s3 = self._get_s3_object()
        try:
            s3.head_object(Bucket=self.bucket, Key=s3_file)
            return True
        except:
            return False

    def download_file(self, s3_file, local_path):
        s3 = self._get_s3_object()
        try:
            s3.download_file(self.bucket, s3_file, local_path)
            print("Download Successful")
            return True
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except FileNotFoundError:
            print("The file was not found")
            return False
        except:
            return False
        



config_settings = ChatConfig.get_config()

bucket = config_settings['S3_BUCKET']
aws_access_key = config_settings['AWS_ACCESS_KEY_ID']
aws_secret_key = config_settings['AWS_SECRET_ACCESS_KEY']


s3_interface = S3BucketInterface(aws_access_key,aws_secret_key,bucket)

exists = s3_interface.file_exists('my_file.txt')
if exists:
    s3_interface.download_file('my_file.txt', 'local/path/to/download/file')
else:
    print("my file doesn't exist")

print(s3_interface.file_exists('alt_prompt.txt'))
upload_successful = s3_interface.upload_file('delivercbt_files/alt_prompt.txt', 'alt_prompt.txt')
download_success = s3_interface.download_file('alt_prompt.txt','delivercbt_files/alt_prompt_copy.txt')
print(download_success)
print(s3_interface.file_exists('alt_prompt.txt'))