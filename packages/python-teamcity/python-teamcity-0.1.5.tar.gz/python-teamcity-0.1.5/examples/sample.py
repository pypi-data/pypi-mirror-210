import logging
import os

from teamcity import TeamCity

TEAMCITY_SERVER = os.environ.get('TEAMCITY_SERVER', None)
TEAMCITY_TOKENS = os.environ.get('TEAMCITY_TOKENS', None)

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    tc = TeamCity(server=TEAMCITY_SERVER, tokens=TEAMCITY_TOKENS)
    # s = tc.get_build_details(1)
    # print(tc.get_build_details(23929740))
    # print(tc.get_all_builds(build_type_id='Hk4eAsset_Streaming_38devAssignerTools'))
    test = tc.get_builds_by_since_build(23948144,count = 50)

    pass