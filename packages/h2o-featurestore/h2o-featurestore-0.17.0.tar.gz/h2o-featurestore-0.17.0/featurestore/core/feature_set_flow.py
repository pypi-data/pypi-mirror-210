from enum import Enum


class FeatureSetFlow(Enum):

    ONLINE_ONLY = 1
    OFFLINE_ONLY = 2
    OFFLINE_ONLINE_MANUAL = 3
    OFFLINE_ONLINE_AUTOMATIC = 4
