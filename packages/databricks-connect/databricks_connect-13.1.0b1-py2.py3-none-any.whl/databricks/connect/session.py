#
# DATABRICKS CONFIDENTIAL & PROPRIETARY
# __________________
#
# Copyright 2020-present Databricks, Inc.
# All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains the property of Databricks, Inc.
# and its suppliers, if any.  The intellectual and technical concepts contained herein are
# proprietary to Databricks, Inc. and its suppliers and may be covered by U.S. and foreign Patents,
# patents in process, and are protected by trade secret and/or copyright law. Dissemination, use,
# or reproduction of this information is strictly forbidden unless prior written permission is
# obtained from Databricks, Inc.
#
# If you view or obtain a copy of this information and believe Databricks, Inc. may not have
# intended it to be made available, please promptly report it to Databricks Legal Department
# @ legal@databricks.com.
#

from importlib.metadata import version
import logging
import os
from pyspark.version import __version__
from typing import Any, Optional

from databricks.sdk.core import Config
from .auth import DatabricksChannelBuilder
from pyspark.sql import SparkSession
from pyspark.sql.connect.session import SparkSession as RemoteSparkSession


# This class can be dropped once support for Python 3.8 is dropped
# In Python 3.9, the @property decorator has been made compatible with the
# @classmethod decorator (https://docs.python.org/3.9/library/functions.html#classmethod)
#
# @classmethod + @property is also affected by a bug in Python's docstring which was backported
class classproperty(property):
    def __get__(self, instance: Any, owner: Any = None) -> "DatabricksSession.Builder":
        # The "type: ignore" below silences the following error from mypy:
        # error: Argument 1 to "classmethod" has incompatible
        # type "Optional[Callable[[Any], Any]]";
        # expected "Callable[..., Any]"  [arg-type]
        return classmethod(self.fget).__get__(None, owner)()  # type: ignore


class DatabricksSession:
    """
    The entry point for Databricks Connect.
    Create a new Pyspark session which connects to a remote Spark cluster and executes specified
    DataFrame APIs.

    Examples
    --------
    >>> spark = DatabricksSession.builder.getOrCreate()
    >>> df = spark.range(10)
    >>> print(df)
    """

    class Builder:
        """
        Builder to construct connection parameters.
        An instance of this class can be created using DatabricksSession.builder.
        """

        def __init__(self):
            self._conn_string: Optional[str] = None
            self._host: Optional[str] = None
            self._cluster_id: Optional[str] = None
            self._token: Optional[str] = None
            self._config: Optional[Config] = None
            self._user_agent: str = ""

        def remote(
            self, conn_string=None, *, host=None, cluster_id=None, token=None, user_agent=""
        ) -> "DatabricksSession.Builder":
            """
            Specify connection and authentication parameters to connect to the remote Databricks
            cluster. Either the conn_string parameter should be specified, or a combination of the
            host, cluster_id and token parameters, but not both.

            Parameters
            ----------
            conn_string : str, optional
                The full spark connect connection string starting with "sc://".
                See https://github.com/apache/spark/blob/master/connector/connect/docs/client-connection-string.md # noqa: E501
            host : str, optional
                The Databricks workspace URL
            cluster_id: str, optional
                The cluster identifier where the Databricks connect queries should be executed.
            token: str, optional
                The Databricks personal access token used to authenticate into the cluster and on
                whose behalf the queries are executed.
            user_agent: str, optional
                A user agent string identifying the application using the Databricks Connect module.
                Databricks Connect sends a set of standard information, such as, OS, Python version
                and the version of Databricks Connect included as a user agent to the service.
                The value provided here will be included along with the rest of the information.
                It is recommended to provide this value in the format "<product-name>/<version>"
                as described in https://datatracker.ietf.org/doc/html/rfc7231#section-5.5.3, but is
                not required.

            Returns
            -------
            DatabricksSession.Builder
                The same instance of this class with the values configured.

            Examples
            --------
            Using a simple conn_string
            >>> conn = "sc://foo-workspace.cloud.databricks.com/;token=dapi1234567890;x-databricks-cluster-id=0301-0300-abcdefab" # noqa: E501
            >>> spark = DatabricksSession.builder.remote(conn).getOrCreate()

            Using keyword parameters
            >>> conn = "sc://foo-workspace.cloud.databricks.com/;token=dapi1234567890;x-databricks-cluster-id=0301-0300-abcdefab" # noqa: E501
            >>> spark = DatabricksSession.builder.remote(
            >>>     host="foo-workspace.cloud.databricks.com",
            >>>     token="dapi1234567890",
            >>>     cluster_id="0301-0300-abcdefab"
            >>> ).getOrCreate()
            """
            self._conn_string = conn_string
            self.host(host)
            self.clusterId(cluster_id)
            self.token(token)
            self.userAgent(user_agent)
            return self

        def host(self, host: str) -> "DatabricksSession.Builder":
            """
            The Databricks workspace URL.

            Parameters
            ----------
            host: str
                The Databricks workspace URL.

            Returns
            -------
            DatabricksSession.Builder
                The same instance of this class with the host configured.
            """
            self._host = host
            return self

        def clusterId(self, clusterId: str) -> "DatabricksSession.Builder":
            """
            The cluster identifier where the Databricks connect queries should be executed.

            Parameters
            ----------
            clusterId: str
                The cluster identifier where the Databricks connect queries should be executed.

            Returns
            -------
            DatabricksSession.Builder
                The same instance of this class with the clusterId configured.
            """
            self._cluster_id = clusterId
            return self

        def token(self, token: str) -> "DatabricksSession.Builder":
            """
            The Databricks personal access token used to authenticate into the cluster and on whose
            behalf the queries are executed.

            Parameters
            ----------
            token: str
                The Databricks personal access token used to authenticate into the cluster and on
                whose behalf the queries are executed.

            Returns
            -------
            DatabricksSession.Builder
                The same instance of this class with the token configured.
            """
            self._token = token
            return self

        def sdkConfig(self, config: Config) -> "DatabricksSession.Builder":
            """
            The Databricks SDK Config object that should be used to pick up connection and
            authentication parameters.
            See https://pypi.org/project/databricks-sdk/#authentication for how to configure
            connection and authentication parameters with the SDK.

            Parameters
            ----------
            config: Config
                The Databricks SDK Config object that contains the connection and authentication
                parameters.

            Returns
            -------
            DatabricksSession.Builder
                The same instance of this class with the token configured.
            """
            self._config = config
            return self

        def userAgent(self, userAgent: str):
            """
            A user agent string identifying the application using the Databricks Connect module.
            Databricks Connect sends a set of standard information, such as, OS, Python version and
            the version of Databricks Connect included as a user agent to the service.
            The value provided here will be included along with the rest of the information.
            It is recommended to provide this value in the format "<product-name>/<product-version>"
            as described in https://datatracker.ietf.org/doc/html/rfc7231#section-5.5.3, but is not
            required.
            Parameters
            ----------
            userAgent: str
                The user agent string identifying the application that is using this module.
            Returns
            -------
            DatabricksSession.Builder
                The same instance of this class with the user agent configured.
            """
            if len(userAgent) > 2048:
                raise Exception("user agent should not exceed 2048 characters.")
            self._user_agent = userAgent
            return self

        def getOrCreate(self) -> RemoteSparkSession:
            """
            Create a new :class:SparkSession that can then be used to execute DataFrame APIs on.

            Returns
            -------
            SparkSession
                A spark session initialized with the provided connection parameters. All DataFrame
                queries to this spark session are executed remotely.
            """
            if self._conn_string is not None:
                logging.debug("Parameter conn_string is specified")
                if (
                    self._host is not None
                    or self._token is not None
                    or self._cluster_id is not None
                ):
                    # conn_string and other parameters should not both be specified
                    raise Exception(
                        "Either conn_string or (host, token and cluster_id) but not both must be specified."  # noqa: E501
                    )
                logging.debug(f"Using connection string: {self._conn_string}")
                return SparkSession.builder.remote(self._conn_string).getOrCreate()

            if self._host is not None or self._token is not None or self._cluster_id is not None:
                logging.debug(
                    "Some parameters detected during initialization. " +
                    f"host={self._host} | token={self._token} | cluster id={self._cluster_id}")
                if self._config is not None:
                    # both sdk config and parameters cannot be both specified
                    raise Exception(
                        "Either sdkConfig or (host, token and cluster_id) " +
                        "but not both must be specified."
                    )
                config = Config(host=self._host, token=self._token, cluster_id=self._cluster_id)
                return self._from_sdkconfig(config)

            if self._config is not None:
                # if the SDK config is explicitly configured
                logging.debug("SDK Config is explicitly configured.")
                return self._from_sdkconfig(self._config)

            if "SPARK_REMOTE" in os.environ:
                logging.debug(f"SPARK_REMOTE configured: {os.getenv('SPARK_REMOTE')}")
                return SparkSession.builder.getOrCreate()

            # use the default values that may be supplied from the SDK Config
            logging.debug("Falling back to default configuration from the SDK.")
            return self._from_sdkconfig(Config())

        def _from_sdkconfig(self, config: Config) -> RemoteSparkSession:
            cluster_id = config.cluster_id

            if cluster_id is None:
                # host and token presence are validated by the SDK. cluster id is not.
                raise Exception("Cluster id is required but was not specified.")

            logging.debug(f"Using SDK config: {config}")
            channel_builder = DatabricksChannelBuilder(config, self._gen_user_agent())
            return RemoteSparkSession.builder.channelBuilder(channel_builder).getOrCreate()

        def _gen_user_agent(self) -> str:
            # In DB Connect, Pyspark version is overridden by DB Connect version during packaging.
            # See packaging code.
            dbconnect_ver = __version__

            # From https://datatracker.ietf.org/doc/html/rfc7231#section-5.5.3,
            # > By convention, the product identifiers are listed in decreasing order of their
            # > significance for identifying the user agent software.
            user_agent = " ".join([
                f"{self._user_agent}",
                f"dbconnect/{dbconnect_ver}",
                f"databricks-sdk/{version('databricks-sdk')}",
            ])
            return user_agent.strip()

    @classproperty
    def builder(cls) -> "DatabricksSession.Builder":
        """Create a new instance of :class:DatabricksSession.Builder"""
        return cls.Builder()
