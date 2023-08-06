
import boto3
import os
import unittest
from dotenv.main import load_dotenv

from circles_local_aws_s3_storage_python.AWSStorage import AwsS3Storage
from circles_local_aws_s3_storage_python.StorageDB import StorageDB
load_dotenv()


class s3_test(unittest.TestCase):
    def setUp(self) -> None:
        self.s3_resource = boto3.resource('s3')
        self.awsS3 = AwsS3Storage(
            os.getenv("BUCKET_NAME"), os.getenv("REGION"))
        self.test_file_contents = b'this it a file test!'
        self.database = StorageDB()

    def test_upload(self):
        cwd = os.getcwd()
        filepath = os.path.join(cwd, 'tests/test.txt')
        functionId = self.awsS3.upload_file(
            filepath, 'test.txt', 'python/', 1)
        s3_object = self.s3_resource.Object(
            os.getenv("BUCKET_NAME"), 'python/test.txt')
        s3_file_contents = s3_object.get()['Body'].read()
        self.assertEqual(s3_file_contents, self.test_file_contents)
        actualId = self.database.getLastId()
        self.assertEqual(functionId, actualId)

    def test_download(self):
        cwd = os.getcwd()
        self.awsS3.download_file(
            'python/test.txt', cwd+'/test.txt')
        assert os.path.isfile(
            cwd+'/test.txt')

    def test_logical_delete(self):
        self.awsS3.delete_file('python\\', 'test.txt', 1)
        result = self.database.getEndTimeStampFromDB(
            'python\\', 'test.txt', os.getenv("REGION"))
        self.assertIsNotNone(result[0])


if __name__ == '__main__':
    unittest.main()
