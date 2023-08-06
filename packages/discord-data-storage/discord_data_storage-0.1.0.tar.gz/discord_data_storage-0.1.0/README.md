# DiscordDataStorage
## Summary
A simple data storage module I made for when creating Discord bots. <br />
Uses the cryptography module for encryption. Although this is designed for Discord, it isn't dependent on any Discord specific features or modules, so it could be used for any data storage. <br />
When reading or writing data, it uses server ids and user ids, which can be omitted. If neither is passed, it returns a global data file, useful for data that might be meant for the entire bot. Passing only the server id can be used to store data for a server itself, such as configuring roles or channels. Passing only the user id can be used for storing data to a user that is shared across all servers, such as bot preferences. Passing both can be used to store user data specific to a server, such as levels. <br />
This also supports templates for each of the four combinations. If a non-dictionary type is passed, it is used as a default when data doesn't exist. If a dictionary is passed, it goes over each key and sets the value to match the template if it doesn't exist in the data, also recursively calling itself for any dictionary values. Note that templates are not applied to existing data. They are applied before returning the data when reading, where they will theoretically get written later. As such, if a new template is given to the constructor and then later reverted, any data that wasn't read and then written with the new template will not return with the new template after it is reverted. <br />
## Documentation
`discord_data_storage.DataAccessor(key, user_template=None, member_template=None, server_template=None, bot_template=None, storage_location="DiscordDataStorage", salt=b"")` <br />
The main class used to read and write data. <br />
**Parameters:** <br />
key - The fernet key to use for encrypting data. <br />
user_template - the template to use when retrieving user data <br />
member_template - the template to use when retrieving member data <br />
server_template - the template to use when retrieving server data <br />
bot_template - the template to use when retrieving bot data <br />
storage_location - where to store the data files <br />
If a relative storage_location is given, it is joined with home. <br />
salt - the salt to use when creating user hashes <br />
 <br />
`discord_data_storage.DataAccessor.read(server_id="", user_id="")` <br />
Reads the data matching the given parameters. <br />
**Parameters:** <br />
server_id - the server id of the data to read <br />
user_id - the user id of the data to read <br />
**Raises:** <br />
FileNotFoundError - No data was found for the parameters, and no template exists for it <br />
cryptography.fernet.InvalidToken - An invalid key was given when this object was constructed <br />
**Returns:** <br />
The retrieved data <br />
 <br />
`discord_data_storage.DataAccessor.write(data, server_id="", user_id="")` <br />
Writes the data to the given parameters. <br />
**Parameters:** <br />
data - the data to write <br />
server_id - the server id of the data to write <br />
user_id - the user id of the data to write <br />
 <br />
`discord_data_storage.DataAccessor.delete(server_id="", user_id="")` <br />
Deletes the data matching the given parameters if it exists. <br />
**Parameters:** <br />
server_id - the server id of the data to delete <br />
user_id - the user id of the data to delete <br />
 <br />
`discord_data_storage.DataAccessor.data_exists(server_id="", user_id="")` <br />
Checks if data exists for the given parameters. <br />
**Parameters:** <br />
server_id - the server id of the data to check <br />
user_id - the user id of the data to check <br />
**Returns:** <br />
True if the data exists, False if not <br />
