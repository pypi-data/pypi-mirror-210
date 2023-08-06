import requests
from requests.auth import HTTPBasicAuth

class PaligoClient():
    def __init__(self, user="", key=""):
        self.username = user
        self.password = key
        self.headers = {
            'Accept': 'application/json'
        }

    def get_documents(self, parent):
        '''Get all documents in a parent folder, takes the folder UUID'''
        document = requests.get(f'''https://mesangs.paligoapp.com/api/v2/documents?parent={parent}''', auth=HTTPBasicAuth(self.username, self.password), headers=self.headers)
        return document.json()["documents"]

    def get_document(self, doc_id):
        '''Get all document content, takes the document ID or UUID'''
        document = requests.get(f'''https://mesangs.paligoapp.com/api/v2/documents/{doc_id}''', auth=HTTPBasicAuth(self.username, self.password), headers=self.headers)
        return document.json()

    def get_folders(self, parent=""):
        '''Get all folders in a parent folder, takes the folder UUID'''
        folders = requests.get(f'''https://mesangs.paligoapp.com/api/v2/folders?parent={parent}''', auth=HTTPBasicAuth(self.username, self.password), headers=self.headers)
        return folders.json()["folders"]

    def get_folder(self, folder_id):
        '''Get folder, takes the folder ID or UUID'''
        folder = requests.get(f'''https://mesangs.paligoapp.com/api/v2/folders/{folder_id}''', auth=HTTPBasicAuth(self.username, self.password), headers=self.headers)
        return folder.json()["children"]

    def get_images(self, parent):
        '''Get all images in a parent folder, takes the folder UUID'''
        images = requests.get(f'''https://mesangs.paligoapp.com/api/v2/images?parent={parent}''', auth=HTTPBasicAuth(self.username, self.password), headers=self.headers)
        return images.json()["images"]

    def get_image(self, image_id):
        '''Gets information about an image, takes the image ID or UUID'''
        image = requests.get(f'''https://mesangs.paligoapp.com/api/v2/images/{image_id}''', auth=HTTPBasicAuth(self.username, self.password), headers=self.headers)
        return image.json()

    def download_image(self, image_id, path):
        '''Download an image from paligo. Takes the image ID or UUID and the filename and path to save the file at.'''
        with requests.get(f'''https://mesangs.paligoapp.com/api/v2/images/{image_id}?size=&download=true''', auth=HTTPBasicAuth(self.username, self.password), headers=self.headers) as r:
            if r.ok:
                with open(path, 'wb') as f:
                    f.write(r.content)
            else:
                print(r.content)
