import os
import time
import json
import numpy as np
import base64
from functools import wraps
from .api_client import ApiClient
from .configuration import Configuration
from .rest import ApiException
from .api.default_api import DefaultApi
from .models import *


class AmberV2Client:
    def __init__(
        self,
        license_id: str = None,
        license_file: str = "~/.Amber.license",
        verify: bool = False,
        timeout: int = 300,
    ):
        """Main client which interfaces with the Amber cloud. Amber account
        credentials are discovered within a .Amber.license file located in the
        home directory, or optionally overridden using environment variables.

        Args:
            license_id: (type: str) license identifier label found within .Amber.license file
            license_file: (type: str) path to .Amber.license file
            verify: (type: boolean) Boolean, controls whether we verify the server’s TLS certificate
            timeout: (type: int) number of seconds to allow API call to wait

        Environment:

            `AMBER_V2_LICENSE_FILE`: sets license_file path

            `AMBER_V2_LICENSE_ID`: sets license_id

            `AMBER_V2_SERVER`: overrides the server as found in .Amber.license file

            `AMBER_V2_OAUTH_SERVER`: overrides the oauth server as found in .Amber.license file

            `AMBER_V2_LICENSE_KEY`: overrides the license key as found in .Amber.license file

            `AMBER_V2_SECRET_KEY`: overrides the secret key as found in .Amber.license file

        Raises:
            ApiException: if error supplying authentication credentials
        """
        self.access_token = ""
        self.refresh_token = ""
        self.reauth_time = 0
        self.server = ""
        self.oauth_server = ""
        self.profile = os.environ.get("AMBER_V2_LICENSE_FILE", license_file)
        self.profile_id = os.environ.get("AMBER_V2_LICENSE_ID", license_id)
        self.api = None
        self.license = ""
        self.secret = ""
        file_data = ""

        if self.profile is not None:
            self.profile = os.path.expanduser(self.profile)
            if os.path.exists(self.profile):
                try:
                    with open(self.profile, "r") as f:
                        file_data = json.load(f)
                except json.JSONDecodeError as e:
                    raise ApiException("JSON formatting error in license file: {}, line: {}, col: {}".format(e.msg, e.lineno, e.colno))
                try:
                    self.server = file_data[self.profile_id]["server"]
                except KeyError:
                    # raise ApiException('profile_id "{} server" not found in license file'.format(self.profile_id))
                    # server not found but continue incase the env variable is set instead
                    self.server = ""
                try:
                    self.oauth_server = file_data[self.profile_id]["oauth-server"]
                except KeyError:
                    # raise ApiException('profile_id "{} oauth-server" not found in license file'.format(self.profile_id))
                    # server not found but continue incase the env variable is set instead
                    self.oauth_server = ""
            else:
                raise ApiException('Amber license file "{}" not found'.format(self.profile))

        self.configuration = Configuration()

        self.server = os.environ.get("AMBER_V2_SERVER", self.server)
        if self.server == "":
            raise ApiException('server not set: add "server" key to license file or set AMBER_V2_SERVER environment variable')
        # server is set if it reaches this point
        self.configuration.host = self.server

        # oauth server
        self.oauth_server = os.environ.get("AMBER_V2_OAUTH_SERVER", self.oauth_server)
        if self.oauth_server == "":
            # oauth_server gets assigned to server when not directly configured
            self.oauth_server = self.server

        try:
            self.license = file_data[self.profile_id]["license"]
            self.secret = file_data[self.profile_id]["secret"]
        except KeyError as e:
            # do nothing here
            self.license = ""
            self.secret = ""

        self.license = os.environ.get("AMBER_V2_LICENSE_KEY", self.license)
        self.secret = os.environ.get("AMBER_V2_SECRET_KEY", self.secret)

        if self.license == "" or self.secret == "":
            raise ApiException("need license and secret keys set in either the environment or the .Amber.license file")

        self.api = DefaultApi(ApiClient(self.configuration))

    def __authenticate(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            if time.time() <= self.reauth_time:
                return f(self, *args, **kwargs)

            try:
                if self.access_token == "":
                    # initial authentication, use license and secret key
                    body = PostOauth2AccessRequest(self.license, self.secret)
                    response = self.api.post_oauth2_access(body)
                    self.access_token = response.id_token
                    self.refresh_token = response.refresh_token
                    self.expires_in = int(response.expires_in)
                    self.secret = ""  # clear the secret from plain site
                else:
                    # we have authenticated once, use the refresh token
                    body = PostOauth2RefreshRequest(self.refresh_token)
                    response = self.api.post_oauth2_refresh(body)
                    self.access_token = response.id_token
                    self.refresh_token = response.refresh_token
                    self.expires_in = int(response.expires_in)

            except ApiException as e:
                raise ApiException("Authentication failed: invalid credentials")

            self.configuration.api_key["Authorization"] = self.access_token
            self.configuration.api_key_prefix["Authorization"] = "Bearer"
            self.reauth_time = time.time() + self.expires_in - 60

            return f(self, *args, **kwargs)

        return inner

    @__authenticate
    def get_version(self) -> GetVersionResponse:
        """

        Return version information for the API.

        Returns:
            `boonamber.v2.models.get_version_response.GetVersionResponse`

        Example:
            ```
            amber = AmberClientV2()
            version = amber.get_version()
            print(version.to_dict())
            ```

        """
        try:
            # get version
            return self.api.get_version()
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def delete_model(self, model_id: str):
        """

        Permanently delete the specified model.

        Args:
            model_id: (type: str) (required)

        """
        try:
            # delete model
            self.api.delete_model(model_id=model_id)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def get_root_cause(self, model_id: str, **kwargs) -> GetRootCauseResponse:
        """

        Return a measure of the significance of each feature in the creation of a cluster. The values range from 0 to 1 where a relatively high value represents a feature that was influential in creating the new cluster. No conclusions can be drawn from values close to zero. This measure can be computed for existing clusters or for individual vectors directly.

        Args:
            model_id: (type: str) (required)
            clusters: (type: str or array-like) Clusters to analyze (list of comma-separated integers).
            vectors: (type: str or array-like) Vectors to analyze, as a flat list of comma-separated floats. Number of values must be a multiple of the configured number of features.

        Returns:
            `boonamber.v2.models.get_root_cause_response.GetRootCauseResponse`

        """
        import numpy as np

        # vectors
        if "vectors" in kwargs.keys():
            if isinstance(kwargs["vectors"], (list, np.ndarray, tuple)):
                dimensions = len(np.asarray(kwargs["vectors"]).shape)
                # 1 vector given
                if dimensions == 1:
                    kwargs["vectors"] = ",".join([str(v) for v in kwargs["vectors"]])
                # 2d array of vectors
                elif dimensions == 2:
                    kwargs["vectors"] = [",".join([str(v) for v in row]) for row in kwargs["vectors"]]
                    kwargs["vectors"] = "],[".join(kwargs["vectors"])
                else:
                    raise ApiException("401: invalid dimensions of vectors given: should be 1 or 2D but got {}D".format(len(np.asarray(kwargs["vectors"]).shape)))
                kwargs["vectors"] = "[[{}]]".format(kwargs["vectors"])
            # not a string or not formatted as a string list
            elif not isinstance(kwargs["vectors"], str):
                raise ApiException("401: invalid formatting of vectors. Expecting a array-type or numbers or string")
        # clusters
        if "clusters" in kwargs.keys():
            if isinstance(kwargs["clusters"], (list, np.ndarray, tuple, str, int, float)):
                dimensions = len(np.asarray(kwargs["clusters"]).shape)
                # 1 value
                if dimensions == 0:
                    kwargs["clusters"] = f"[{kwargs['clusters']}]"
                # list of clusters
                elif dimensions == 1:
                    kwargs["clusters"] = "[{}]".format(",".join([str(c) for c in kwargs["clusters"]]))
                else:
                    raise ApiException("401: invalid dimensions of clusters given: should be 0 or 1D but got {}D".format(len(np.asarray(kwargs["clusters"]).shape)))
            else:
                raise ApiException("401: invalid formatting of clusters. Expecting a array-type or numbers or string")

        try:
            # get root cause
            if "clusters" in kwargs.keys():
                return self.api.get_model_root_cause(model_id=model_id, clusters=kwargs["clusters"])
            if "vectors" in kwargs.keys():
                return self.api.get_model_root_cause(model_id=model_id, vectors=kwargs["vectors"])
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def get_config(self, model_id: str) -> PostConfigResponse:
        """

        Get the configuration of the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.post_config_response.PostConfigResponse`

        """
        try:
            # get config
            return self.api.get_model_config(model_id=model_id)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def get_model(self, model_id: str) -> PostModelResponse:
        """

        Return metadata for the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """
        try:
            # get model
            return self.api.get_model(model_id=model_id)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def get_models(self) -> GetModelsResponse:
        """

        Return `id` and `label` for all models belonging to the user.

        Returns:
            `boonamber.v2.models.get_models_response.GetModelsResponse`

        """
        try:
            # get list of models
            return self.api.get_models()
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def get_pretrain(self, model_id: str) -> GetPretrainResponse:
        """

        Get the pretraining status of the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.get_pretrain_response.GetPretrainResponse`

        """
        try:
            # get pretrain state
            return self.api.get_model_pretrain(model_id=model_id)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def get_status(self, model_id: str) -> GetStatusResponse:
        """

        Get the current state and learning progress of the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.get_status_response.GetStatusResponse`

        """
        try:
            # get status
            return self.api.get_model_status(model_id=model_id)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def get_nano_status(self, model_id: str) -> GetNanoStatusResponse:
        """

        Get the current nano status of the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.get_nano_status_response.GetNanoStatusResponse`

        """
        try:
            # get status
            return self.api.get_model_nano_status(model_id=model_id)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def get_diagnostic(self, model_id: str, dir: str) -> str:
        """

        Get the current summation of the specified model

        Args:
            model_id: (type: str) (required)
            dir: (type: str) (required) path to save the diagnostic tar file

        Returns:
            str

        """
        import os

        if not os.path.exists(dir):
            raise ApiException("target directory does not exist")
        dir = os.path.expanduser(dir)
        path = f"{dir}/{model_id}-diagnostic.tar"
        try:
            # get diagnostic
            results = self.api.get_model_diagnostic(model_id=model_id)

            with open(path, "wb") as fp:
                fp.write(results)
            return path
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def post_config(self, model_id: str, body: PostConfigRequest) -> PostConfigResponse:
        """

        Configure the specified model. Wipes all progress and puts the model in the `Buffering` state.

        Args:
            model_id: (type: str) (required)
            body: (type: `boonamber.v2.models.post_config_request.PostConfigRequest`) configuration to apply

        Returns:
            `boonamber.v2.models.post_config_response.PostConfigResponse`

        """

        try:
            # post config
            return self.api.post_model_config(model_id=model_id, body=body)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def post_data(self, model_id: str, data, save_image: bool = True) -> PostDataResponse:
        """

        Send data to the specified model, and get back the resulting analytics and model status.

        Args:
            model_id: (type: str) (required)
            data: (type: str or array-like) (required) data vector or vectors as a flattened list of comma-separated values
            save_image: (type: boolean) whether or not to save the model (only applies to on prem)

        Returns:
            `boonamber.v2.models.post_data_response.PostDataResponse`

        """

        try:
            # accept data as a list
            if isinstance(data, (list, np.ndarray)):
                data = np.array(data, dtype=str).flatten()
                data = ",".join(data)
            elif not isinstance(data, str):
                raise ApiException("invalid data: {}".format(type(data)))
            # post data
            body = PostDataRequest(data=data, save_image=save_image)
            return self.api.post_model_data(model_id=model_id, body=body)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def post_model(self, metadata: PostModelRequest) -> PostModelResponse:
        """

        Create a new model and return its unique identifier.

        Args:
            metadata: (type: `boonamber.v2.models.post_model_request.PostModelRequest`) (required) initial metadata for new model

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """
        try:
            # post new model
            return self.api.post_model(body=metadata)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def copy_model(self, model_id: str, label: str = None) -> PostModelResponse:
        """

        Copy a model and return the new model information.

        Args:
            model_id: (type: str) (required)
            label: (type: str) label for new model (uses previous label if unspecified)

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """
        kwargs = {}
        if label:
            kwargs["body"] = PostModelCopyRequest(label=label)

        try:
            # copy a model
            return self.api.post_model_copy(model_id, **kwargs)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def post_outage(self, model_id: str):
        """

        Resets the streaming window generated by `streamingWindow`. This endpoint should be called after a data outage before resuming streaming.

        Args:
            model_id: (type: str) (required)

        """
        try:
            # post outage
            self.api.post_model_outage(model_id=model_id)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def migrate_model(self, v1_model_id: str):
        """migrate a v1 sensor to a v2 model


        Args:
            v1_model_id: (type: str) version 1 sensor id (required)

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """

        try:
            # post migrate
            return self.api.post_model_migrate(v1_model_id=v1_model_id)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def post_pretrain(self, model_id: str, data, chunk_size: int = 400000, block: bool = True, **kwargs) -> PostPretrainResponse:
        """pretrain model with an existing dataset

        Args:
            model_id: (type: str) (required)
            data: (type: str or array like) data to process
            chunk_size: (type: int) number of portions to send the data over
            block: (type: boolean) wait until pretraining finishes before returning

        Returns:
            `boonamber.v2.models.post_pretrain_response.PostPretrainResponse`

        """
        try:
            # Server expects data as a plaintext string of comma-separated values.
            try:
                if isinstance(data, str):
                    data = data.split(",")

                data = np.array(data, dtype="float32")
                data = data.flatten()
                data = data.tobytes()
            except ValueError as e:
                raise ApiException("invalid data: {}".format(e))

            # headers = {"content-type": "application/octet-stream"
            param = PostPretrainRequest(data="", format="packed-float")

            # compute number of chunks to send
            num_chunks = int(len(data) / chunk_size)
            if len(data) % chunk_size != 0:
                num_chunks += 1

            txn_id = ""
            for chunk_num in range(0, num_chunks):
                # create chunk specifier, .ie 1:3, 2:3, 3:3
                chunkspec = "{}:{}".format(chunk_num + 1, num_chunks)

                # construct next chunk
                start = chunk_num * chunk_size
                end = start + chunk_size
                if end > len(data):
                    end = len(data)
                param.data = base64.b64encode(data[start:end]).decode("ascii")

                try:
                    response = self.api.post_model_pretrain(
                        model_id=model_id,
                        chunkspec=chunkspec,
                        txn_id=txn_id,
                        body=param,
                    )
                    txn_id = response.txn_id
                except Exception as e:
                    raise (ApiException(e))

            if not block:
                return response

            while response.status == "Pretraining":
                time.sleep(3)
                response = self.get_pretrain(model_id=model_id)

            return response

        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def enable_learning(self, model_id: str, **kwargs) -> PostLearningResponse:
        """

        Update model configuration and re-enable learning

        Args:
            model_id: (type: str) (required)
            training: (type: `boonamber.v2.models.training_config.TrainingConfig`) updates to apply

        Returns:
            `boonamber.v2.models.post_learning_response.PostLearningResponse`

        """
        if "training" in kwargs:
            kwargs["body"] = PostLearningRequest(training=kwargs["training"])
            del kwargs["training"]
        try:
            # start learning again
            return self.api.post_model_learning(model_id=model_id, **kwargs)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def put_data(self, model_id: str, body: PutDataRequest) -> PutDataResponse:
        """update fusion vector and get back results

        Args:
            model_id: (type: str) (required)
            body: (type: `boonamber.v2.models.put_data_request.PutDataRequest`) (required) updates to the fusion vector

        Returns:
            `boonamber.v2.models.put_data_response.PutDataResponse`

        """
        try:
            # put data
            return self.api.put_model_data(model_id=model_id, body=body)
        except Exception as e:
            raise ApiException(e)

    @__authenticate
    def update_label(self, model_id: str, label: str) -> PostModelResponse:
        """

        Update metadata for the specified model.

        Args:
            model_id: (type: str) (required)
            label: (type: str) (required) updates to apply

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """
        try:
            # update model metadata
            metadata = PutModelRequest(label=label)
            return self.api.put_model(model_id=model_id, body=metadata)
        except Exception as e:
            raise ApiException(e)
