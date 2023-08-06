import os

from dataclasses import dataclass

@dataclass
class EnvironmentVariables:
    """
    Holds environment variables that AnastasiaLogger can recieve

    """

    ANASTASIA_LOG_NAME: str = os.getenv("ANASTASIA_LOG_NAME", "anastasia-log")
    ANASTASIA_LOG_TAG: str = os.getenv("ANASTASIA_LOG_TAG", "ANASTASIA-JOB")
    ANASTASIA_LOG_LEVEL: str = os.getenv("ANASTASIA_LOG_LEVEL", "INFO")
    ANASTASIA_LOG_SAVELOG: int = int(os.getenv("ANASTASIA_LOG_SAVELOG", "0")) if os.getenv("ANASTASIA_LOG_SAVELOG", "0").isdigit() else 0
    ANASTASIA_LOG_PATH: str = os.getenv("ANASTASIA_LOG_TAG", "anastasia-log.log")