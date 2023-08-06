import os

API_KEY = "MXfA0QLSzva8FW8VyNDr4FuAu5iaEn6dTvDfFWx2EJY="

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
TEST_FILE_PATH = os.path.join(current_directory, "files", "test-file-upload.pdf")
