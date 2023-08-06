import os
import copy
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

HOME_DIR = os.path.expanduser("~")

class DataAccessor:
    def __init__(self, key,
        user_template=None, member_template=None,
        server_template=None, bot_template=None,
        storage_location="DiscordDataStorage",
        salt=b""):
        """Constructor for the object used to save and retrieve data

        The only required parameter is a key created using cryptography Fernet.
        Optional keyword arguments:
        user_template - the template to use when retrieving user data
        member_template - the template to use when retrieving member data
        server_template - the template to use when retrieving server data
        bot_template - the template to use when retrieving bot data
        storage_location - where to store the data files
        If a relative storage_location is given, it is joined with home.
        salt - the salt to use when creating user hashes
        """
        self._key = key
        self._fernet = Fernet(self._key)
        self._user_template = user_template
        self._member_template = member_template
        self._server_template = server_template
        self._bot_template = bot_template
        self._salt = salt
        self._storage_location = os.path.join(HOME_DIR,storage_location)
        if not os.path.isdir(self._storage_location):
            os.makedirs(self._storage_location)

    def read(self, server_id="", user_id=""):
        """Reads data

        Will raise a FileNotFoundError if the data doesn't exist and
        if there is no corresponding template.
        Optional keyword arguments:
        server_id - the server id of the data to read
        user_id - the user id of the data to read

        returns the data read
        """
        template = self._get_template(server_id != "", user_id != "")
        if template == None and not self.data_exists(server_id, user_id):
            raise FileNotFoundError("No data file found")

        if not self.data_exists(server_id, user_id):
            data = copy.deepcopy(template)
        else:
            data = json.loads(self._read_file(server_id, user_id))
            if isinstance(data, dict) and isinstance(template, dict):
                DataAccessor._apply_template(data, template)
        return data

    def write(self, data, server_id="", user_id=""):
        """Writes data

        Optional keyword arguments:
        server_id - the server id of the data to write
        user_id - the user id of the data to write
        """
        self._write_file(json.dumps(data), server_id, user_id)

    def delete(self, server_id="", user_id=""):
        """Deletes data

        Deletes the data if it exists, does nothing if it doesn't.
        Optional keyword arguments:
        server_id - the server id of the data to delete
        user_id - the user id of the data to delete
        """
        if self.data_exists(server_id=server_id, user_id=user_id):
            os.remove(self._get_file_path(
                server_id=server_id,
                user_id=user_id
            ))

    def data_exists(self,  server_id="", user_id=""):
        """Checks if data exists

        Optional keyword arguments:
        server_id - the server id of the data to check
        user_id - the user id of the data to check

        returns a boolean showing if the data exists
        """
        return os.path.isfile(self._get_file_path(server_id, user_id))

    def _read_file(self, server_id="", user_id=""):
        """Reads data from a file

        Simply returns the unencrypted data in a file, without applying
        any templates or checking if the file exists.
        Optional keyword arguments:
        server_id - the server id of the data to read
        user_id - the user id of the data to read

        returns the data read
        """
        with open(self._get_file_path(server_id, user_id), "r") as data_file:
            data = data_file.read()
        return self._decrypt(data)

    def _write_file(self, data, server_id="", user_id=""):
        """Writes data to a file

        Writes a string to a file in encrypted form
        Optional keyword arguments:
        server_id - the server id of the data to write
        user_id - the user id of the data to write
        """
        data = self._encrypt(data)
        with open(self._get_file_path(server_id, user_id), "w") as data_file:
            data = data_file.write(data)

    def _get_template(self, is_server, is_user):
        """Gets the correct template for some data

        The first argument should be a boolean specifying if the data
        is specific to a server.
        The second argument should be a boolean specifying if the data
        is specific to a user.

        returns the corresponding template
        """
        if not is_server and not is_user:
            return self._bot_template
        elif not is_server:
            return self._user_template
        elif not is_user:
            return self._server_template
        else:
            return self._member_template

    def _get_file_path(self, server_id="", user_id=""):
        """Gets the file path for the file that stores some data

        Optional keyword arguments:
        server_id - the server id of the file to locate
        user_id - the user id of the file to locate

        returns the file path
        """
        return os.path.join(
            self._storage_location,
            self._get_file_name(server_id, user_id)
        )

    def _get_file_name(self, server_id="", user_id=""):
        """Gets the file name for the file that stores some data

        Optional keyword arguments:
        server_id - the server id of the file to locate
        user_id - the user id of the file to locate

        returns the file name
        """
        base_file_name = "{}:{}".format(server_id, user_id)
        return self._get_user_hash(base_file_name)

    def _encrypt(self, value):
        """Encrypts a string

        The argument should be the string value to encrypt.

        returns the encrypted value in string form
        """
        return self._fernet.encrypt(value.encode()).decode()

    def _decrypt(self, encrypted_value):
        """Decrypts a string

        The argument should be the string value to decrypt.

        returns the decrypted value
        """
        return self._fernet.decrypt(encrypted_value.encode()).decode()

    def _get_user_hash(self, value):
        """Gets a hash of a value

        Specifically has user in the method name to specify that a constant
        salt is used, so only unique values should be used (such as user ids).
        The argument should be the string value to hash.

        returns the hash as a hex string
        """
        kdf = Scrypt(salt=self._salt, length=32, n=2**14, r=8, p=1)
        return kdf.derive(value.encode()).hex()

    @staticmethod
    def _apply_template(value, template):
        """Applies a dictionary template to a value

        Modifies the value in place, so nothing is returned.
        The first argument should be the current dictionary value.
        The second argument should be the dictionary template to apply.
        """
        for key in template:
            if key not in value:
                value[key] = copy.deepcopy(template[key])
            elif isinstance(value[key], dict):
                DataAccessor._apply_template(value[key], template[key])
