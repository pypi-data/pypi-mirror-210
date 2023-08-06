from circles_local_aws_s3_storage_python.CirclesStorage import circles_storage
import os
import unittest
from dotenv.main import load_dotenv
load_dotenv()


class circles_storage_test(unittest.TestCase):
    def setUp(self) -> None:
        self.circles_storage = circles_storage()
        print("REGION:"+str(os.getenv("REGION")))

    def test_get_folder(self):
        actual_folder = self.circles_storage.get_folder(1)
        expected_folder = 'Profile Image'
        self.assertEqual(actual_folder, expected_folder)

    def test_get_region_and_folder(self):
        actual = self.circles_storage.get_region_and_folder(
            profile_id=1, entity_type_id=1)
        actual = str(actual).replace(" ", "")
        expected = "['ProfileImage','us-east-1']"
        self.assertEqual(actual, expected)

    def test_put(self):
        cwd = os.getcwd()
        filepath = os.path.join(cwd, 'tests/test.txt')
        id = self.circles_storage.put(profile_id=1, entity_type_id=1, file_name='circles_test.txt',
                                      local_file_path=filepath)
        self.assertGreater(id, 0)


if __name__ == '__main__':
    unittest.main()
