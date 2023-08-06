import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(), verbose=True)
currentEnv = os.getenv("BR_CI_CMD_ENV")

if currentEnv == "prod":
    from .prod import Config

    Conf = Config
elif currentEnv == "develop":
    from .develop import Config

    Conf = Config
else:
    from .develop import Config

    Conf = Config

print(f"ENV: {currentEnv}")
