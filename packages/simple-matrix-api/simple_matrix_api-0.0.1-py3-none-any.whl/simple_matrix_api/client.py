from typing import Mapping
import requests
import os
from typing import Union, Any
from urllib.parse import urlparse


class Client:

    def __init__(self, base_url: str, access_token: str):
        self.base_url: str = base_url
        self.access_token: str = access_token

    def upload(self, file_name: str, content: bytes) -> str:
        """
        Upload some content. This method expects raw bytes as content.
        If request is successful, returns content URI (MXC).
        """
        headers: Mapping[str, str] = {
            "Content-Length": str(len(content)),
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.post(f"{self.base_url}/_matrix/media/v3/upload",
                                 headers=headers,
                                 data=content,
                                 params={"filename": file_name})
        return response.json()["content_uri"]

    def upload_file(self, file_name: str, file_path: str) -> str:
        with open(file_path, "rb") as f:
            return self.upload(file_name, f.read())

    def _send_message(self, room_id: str, message: dict[str, Any]):
        requests.put(
            f"{self.base_url}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{os.urandom(24).hex()}",
            json=message,
            headers={"Authorization": f"Bearer {self.access_token}"})

    def send_message_text(self, room_id: str, message: str):
        self._send_message(room_id, {"body": message, "msgtype": "m.text"})

    def get_file(
            self,
            file_url: str,
            file_save_path: Union[str, None] = None) -> Union[bytes, None]:
        file_path: str = urlparse(file_url).path
        file_hostname: Union[str, None] = urlparse(file_url).hostname

        if file_hostname == None:
            return None

        file_content = requests.get(
            f"{self.base_url}/_matrix/media/v3/download/{file_hostname}{file_path}"
        ).content

        if file_save_path != None:
            with open(file_save_path, "wb") as f:
                f.write(file_content)

        return file_content
