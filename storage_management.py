import os
import boto3
from chat import ChatConfig
from botocore.exceptions import NoCredentialsError, BotoCoreError

class StorageManager:

    def __init__():
        pass

    def save(self, contents, filename):
        with open(self.local_path + filename, 'w') as f:
            f.write(contents)
        return True
    
    def open_append(self, append_contents, filename):
        with open(self.local_path + filename, 'a+') as f:
            f.write(append_contents)
    
    def exists(self, filename):
        try:
            f = open(self.local_path + filename)
            return True
        except FileNotFoundError:
            return False
        
    def load(self, filename):
        with open(self.local_path + filename, 'r') as f:
            return f.read()
        
    def remove(self, filename):
        os.remove(self.local_path + filename)

    
class LocalStorageManagement(StorageManager):
    
    def __init__(self, local_path):
        self.local_path = local_path
        print("using local storage management only")
        


class S3BucketManagement(StorageManager):

    def __init__(self, access_key, secret_key, bucket):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.region_name = 'us-east-1'
        self.local_cache = bucket + '_S3BucketManagement_cache'
        self.s3_client = None
        self.local_path = self.local_cache + "/"
        self.local_append_path = self.local_path  + '/for_append'
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)

        if not os.path.exists(self.local_append_path):
            os.makedirs(self.local_append_path)

        print("using s3 bucket management")


    def is_s3_client_active(self, s3_client):
        try:
            s3_client.list_buckets()  # low-impact operation.
            return True
        except (BotoCoreError, NoCredentialsError):  # handle relevant exceptions
            return False
        

    def _get_s3_object(self):
        #should add a client age tracker so that if the client is under a certain age (say 1 hour) we don't even bother checking 
        # if it is active, we just return it
        #would probably need to be coupled with try/catch statements around other s3 operations, i.e., load, remove, upload
        if self.s3_client is None or not self.is_s3_client_active(self.s3_client):
            self.s3_client = boto3.client('s3',
                            aws_access_key_id=self.access_key,
                            aws_secret_access_key=self.secret_key,
                            region_name=self.region_name)
        
        return self.s3_client
    

    def save(self, contents, filename):
        local_path = self.local_cache + '/' + filename
        super().save(contents, filename)
        self.upload(local_path, filename)
        os.remove(local_path)
        return True
    
    def open_append(self, append_contents, filename):
        append_filecache_subpath = '/for_append/' + filename
        append_filecache_filepath = self.local_cache + append_filecache_subpath
        self.download_file(filename, append_filecache_filepath)
        super().open_append(append_contents, append_filecache_subpath)
        self.upload(append_filecache_filepath, filename)
        os.remove(append_filecache_filepath)

    def load(self, filename):
        local_path = self.local_cache + '/' + filename
        self._get_s3_object().download_file(self.bucket, filename, local_path)
        local_file_data = super().load(filename)
        #remove the file we downloaded
        os.remove(local_path)
        return(local_file_data)
    
    def remove(self, filepath):
        self._get_s3_object().delete_object(Bucket=self.bucket, Key=filepath)
        return True
    


    def upload(self, local_file, s3_file):
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

    def exists(self, s3_file):
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
        



# config_settings = ChatConfig.get_config()

# bucket = config_settings['S3_BUCKET']
# aws_access_key = config_settings['AWS_ACCESS_KEY_ID']
# aws_secret_key = config_settings['AWS_SECRET_ACCESS_KEY']


# s3_interface = S3BucketInterface(aws_access_key,aws_secret_key,bucket)

# exists = s3_interface.file_exists('my_file.txt')
# if exists:
#     s3_interface.download_file('my_file.txt', 'local/path/to/download/file')
# else:
#     print("my file doesn't exist")

# print(s3_interface.file_exists('alt_prompt.txt'))
# upload_successful = s3_interface.upload_file('delivercbt_files/alt_prompt.txt', 'alt_prompt.txt')
# download_success = s3_interface.download_file('alt_prompt.txt','delivercbt_files/alt_prompt_copy.txt')
# print(download_success)
# print(s3_interface.file_exists('alt_prompt.txt'))