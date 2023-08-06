from circles_local_aws_s3_storage_python.FileTypeDB import file_type_db
import os
from circles_local_aws_s3_storage_python.AWSStorage import AwsS3Storage
from dotenv.main import load_dotenv
load_dotenv()


class circles_storage:

    def __init__(self):
        print("REGION:"+str(os.getenv("REGION")))
        self.s3 = AwsS3Storage(os.getenv("BUCKET_NAME"), os.getenv("REGION"))
        self.db = file_type_db()

    # returns the folder name from DB according to entity_type_id
    def get_folder(self, entity_type_id):
        select_stmt = "SELECT file_type FROM storage.file_type_table WHERE id = %s"
        select_data = (entity_type_id)
        return self.db.select_from_DB(select_stmt, select_data)

    def get_region_and_folder(self, profile_id, entity_type_id):
        folder = self.get_folder(entity_type_id)
        region = os.getenv("REGION")
        return [folder, region]

    def put(self, profile_id, entity_type_id, file_name, local_file_path):
        folder_and_region = self.get_region_and_folder(
            profile_id, entity_type_id)
        file_database_id = self.s3.upload_file(local_file_path, file_name,
                                               folder_and_region[0]+'/', profile_id)
        return file_database_id
