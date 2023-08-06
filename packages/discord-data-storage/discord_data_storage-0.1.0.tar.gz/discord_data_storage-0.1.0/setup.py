from setuptools import setup

with open("README.md") as readme:
    long_description = readme.read()

setup(
    name = "discord_data_storage",
    version = "0.1.0",
    description = "Encrypted data storage with a format based on Discord",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/jfechete/DiscordDataStorage",
    author = "jfechete",
    packages = ["discord_data_storage"],
    install_requires = [
        "cryptography"
    ]
)
