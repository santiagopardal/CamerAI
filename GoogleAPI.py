import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import pickle


class GoogleAPI:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.CREDENTIALS = self._get_credentials()
        self.METADATA = []
        self._update_metadata()

    def upload(self, filepath, filename, mimetype):
        service = self.CREDENTIALS

        id = self._get_folder_id(self._get_parents(filepath))

        exists = not (id is None)

        if not exists:
            print("Created path...")
            id = self._setup_path(filepath)

        file_metadata = {'name': filename,
                         'parents': [id]}

        media = MediaFileUpload(filepath + filename,
                                mimetype=mimetype)

        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    def create_folder(self, name):
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder"
        }

        file = self.CREDENTIALS.files().create(body=file_metadata, fields="id").execute()

        return file.get("id")

    def create_sub_folder(self, parent, folder_name):
        exists, parent_id = self.exists_folder(parent)

        if not exists:
            parent_id = self.create_folder(parent)

        file_metadata = {
            "name": folder_name,
            "parents": [parent_id],
            "mimeType": "application/vnd.google-apps.folder"
        }

        file = self.CREDENTIALS.files().create(body=file_metadata, fields="id").execute()

        return file.get("id")

    def exists_folder(self, folder):
        res = None
        for data in self.METADATA:
            if data.get("name") == folder:
                res = data
                break

        return not (res is None), res.get("id") if not (res is None) else None

    def exists_file(self, file):
        results = self.CREDENTIALS.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        id = None

        if not items:
            res = False
        else:
            res = False

            while len(items) > 0 and not res:
                item = items.pop(0)
                id = item.get("id")
                res = item.get("name") == file

        if not res:
            id = None

        return res, id

    def list_folders(self):
        results = self.CREDENTIALS.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        if not items:
            res = []
        else:
            res = []
            for item in items:
                res.append(item.get("name"))

        return res

    def remove_everything(self):
        results = self.CREDENTIALS.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        for item in items:
            self.CREDENTIALS.files().delete(fileId=item.get("id")).execute()

        results = self.CREDENTIALS.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                                pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        for item in items:
            self.CREDENTIALS.files().delete(fileId=item.get("id")).execute()

    def _get_credentials(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_id.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds)

        return service

    def _get_parents(self, folder):
        parent_folders = folder.split("/")

        if parent_folders[len(parent_folders) - 1] == '':
            parent_folders.pop(len(parent_folders) - 1)

        if parent_folders[0] == '' or parent_folders[0] == 'to upload':
            parent_folders.pop(0)

        return parent_folders

    def _get_folder_id(self, parents_list):
        res = None
        for data in self.METADATA:
            if data.get("name") == parents_list[1]:
                found = False
                for d in self.METADATA:
                    if d.get("name") == parents_list[0] and d.get("id") == data.get("parents")[0]:
                        found = True

                if found:
                    res = data.get("id")
                    break

        return res

    def _create_sub_folder_id(self, parent_id, name):

        file_metadata = {
            "name": name,
            "parents": [parent_id],
            "mimeType": "application/vnd.google-apps.folder"
        }

        file = self.CREDENTIALS.files().create(body=file_metadata, fields="id").execute()

        return file.get("id")

    def _setup_path(self, path):
        if str(path).startswith("to upload/"):
            path = path[len("to upload/"):]

        parents = self._get_parents(path)

        folder = parents[len(parents) - 1]

        if len(parents) == 1:
            id = self.create_folder(folder)
            self.METADATA.append(self.CREDENTIALS.files().get(fileId=id, fields='*').execute())
        else:
            id = None
            i = 0

            while i < len(parents):
                prev_id = id

                id = prev_id

                if i == 0:
                    id = self.create_folder(parents[i])
                else:
                    self.METADATA.append(self.CREDENTIALS.files().get(fileId=id, fields='*').execute())
                    id = self._create_sub_folder_id(id, parents[i])

                self.METADATA.append(self.CREDENTIALS.files().get(fileId=id, fields='*').execute())

                i = i + 1

        return id

    def _update_metadata(self):
        results = self.CREDENTIALS.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                                pageSize=10, fields="nextPageToken, files(id, name)").execute()
        results = results.get("files")
        for file in results:
            id = file.get("id")
            self.METADATA.append(self.CREDENTIALS.files().get(fileId=id, fields='*').execute())