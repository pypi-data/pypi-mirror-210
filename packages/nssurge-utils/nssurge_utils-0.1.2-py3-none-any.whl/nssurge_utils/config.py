from typing import Literal, get_args
from nssurge_utils.types import SurgeConfigSections

# Retrieve the valid options from SurgeConfigSections
# valid_sections = get_args(SurgeConfigSections)
surge_config_sections: tuple[str] = get_args(SurgeConfigSections)

# Iterate through all valid values
# for section in valid_sections:
#     print(section)

# must be the first ones
special_proxy_group_value = {'select', 'url-test'}

from pathlib import Path

parent_dir = Path(__file__).parent.parent
data_dir = parent_dir / 'data'
countryFlagsNamesAndDialCodes_json_path = (
    data_dir / 'countryFlagsNamesAndDialCodes.json'
)
