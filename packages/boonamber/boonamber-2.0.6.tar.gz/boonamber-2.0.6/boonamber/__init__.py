from .v1 import AmberV1Client as acv1
from .v1 import float_list_to_csv_string
from .v2.amber_client import AmberV2Client as acv2
from boonamber.v2.models import *
from .util.ambererror import AmberCloudError, AmberUserError
from .v2.rest import ApiException

import glob
import os


# version 1 Amberclient
class AmberClient(acv1):
    pass


class AmberV1Client(acv1):
    pass


# version 2 Amberclient
class AmberV2Client(acv2):
    pass


__pdoc__ = {}
__pdoc__["boonamber.v2.api"] = False
__pdoc__["boonamber.v2.api_client"] = False
__pdoc__["boonamber.v2.rest"] = False
__pdoc__["boonamber.v2.configuration"] = False
__pdoc__["boonamber.util"] = False
__pdoc__["AmberClient"] = False

in_files = glob.glob("boonamber/v2/models/*.py")
for model in in_files:
    tmp_func = os.path.splitext(os.path.basename(model))[0].title().replace("_", "")
    __pdoc__["{}.{}.attribute_map".format(os.path.splitext(model)[0].replace("/", "."), tmp_func)] = False
    __pdoc__["{}.{}.swagger_types".format(os.path.splitext(model)[0].replace("/", "."), tmp_func)] = False

# put model (so not to confuse with update_model)
__pdoc__["boonamber.v2.models.put_model_request"] = False

# post model copy (so as not to confuse with copy_model)
__pdoc__["boonamber.v2.models.post_model_copy_request"] = False

# oauth
__pdoc__["boonamber.v2.models.post_oauth2_access_request"] = False
__pdoc__["boonamber.v2.models.post_oauth2_refresh_request"] = False
__pdoc__["boonamber.v2.models.post_oauth2_access_response"] = False
__pdoc__["boonamber.v2.models.post_oauth2_refresh_response"] = False

# summary
__pdoc__["boonamber.v2.models.get_summary_response"] = False
__pdoc__["boonamber.v2.models.magic_number"] = False
__pdoc__["boonamber.v2.models.version_number"] = False
__pdoc__["boonamber.v2.models.m_buffer_stats"] = False
__pdoc__["boonamber.v2.models.m_autotune"] = False
__pdoc__["boonamber.v2.models.m_streaming_parameters"] = False
__pdoc__["boonamber.v2.models.m_amber_status"] = False
__pdoc__["boonamber.v2.models.m_training"] = False
__pdoc__["boonamber.v2.models.m_recent_samples"] = False
__pdoc__["boonamber.v2.models.m_recent_times"] = False
__pdoc__["boonamber.v2.models.m_recent_floats"] = False
__pdoc__["boonamber.v2.models.m_recent_ids"] = False
__pdoc__["boonamber.v2.models.m_pattern_memory"] = False
__pdoc__["boonamber.v2.models.m_recent_ams"] = False
__pdoc__["boonamber.v2.models.m_recent_analytics"] = False

__pdoc__["boonamber.v2.models.mncp"] = False
__pdoc__["boonamber.v2.models.map"] = False
__pdoc__["boonamber.v2.models.m_nano"] = False
__pdoc__["boonamber.v2.models.m_streaming_parameters"] = False
__pdoc__["boonamber.v2.models.m_nano_backend"] = False
__pdoc__["boonamber.v2.models.m_nano_config"] = False
