import datetime
import json
import logging
import os
import traceback

from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from texttable import Texttable


def except_block(exception: Exception, exception_message="No message"):
    """
    Log the details of an exception, including module name, function name, custom message,
    time of occurrence, exception type, arguments, instance, stack trace, and local variables.

    :param exception: The exception instance.
    :type exception: Exception
    :param exception_message: A custom message for the exception, defaults to "No message".
    :type exception_message: str, optional
    """
    exception_timne = str(datetime.datetime.now())
    exception_type = str(type(exception))
    exception_argument = str(exception.args)
    exception_instance = str(exception)

    stack_trace = traceback.format_exc()
    logging.log(
        msg="Exception message: {message}".format(message=exception_message),
        level=logging.ERROR,
    )
    logging.log(
        msg="Exception occured at: {message}".format(message=exception_timne),
        level=logging.ERROR,
    )
    logging.log(
        msg="Exception instance type: {message}".format(message=exception_type),
        level=logging.ERROR,
    )
    logging.log(
        msg="Exception argument: {message}".format(message=exception_argument),
        level=logging.ERROR,
    )
    logging.log(
        msg="Exception instance: {message}".format(message=exception_instance),
        level=logging.ERROR,
    )
    logging.log(
        msg="Exception stack trace: {message}".format(message=stack_trace),
        level=logging.ERROR,
    )


def _keyVaultAccess(key):
    try:
        key_vault_uri = str(key["uri"]).split("/secrets/")[0]
        secret_name = str(key["uri"]).split("/secrets/")[1]
        credential = DefaultAzureCredential(
            exclude_interactive_browser_credential=False
        )
        client = SecretClient(vault_url=key_vault_uri, credential=credential)
        retrieved_secret = client.get_secret(secret_name)
    except Exception as e:
        exception_message = "KeyVault access failed"
        except_block(exception=e, exception_message=exception_message)
    return retrieved_secret.value


def listConfig():
    output_table = Texttable()
    table = [
        ["key", "last_modified", "content_type", "keyVault_reference", "access_level"]
    ]
    appConfigurationConnectionString = os.environ["APPCONFIGURATION_CONNECTION_STRING"]
    app_config_client = AzureAppConfigurationClient.from_connection_string(
        appConfigurationConnectionString
    )
    for config in app_config_client.list_configuration_settings():
        config = config.as_dict()
        try:
            resource_type_definition = config["tags"]["type"]
            resource_base_type = resource_type_definition.split(".")[1].split("/")[0]

            config_type = str(config["content_type"]).lower()
            if "keyvaultref" in config_type:
                is_keyvault_ref = "True"
            else:
                is_keyvault_ref = "False"
            table.append(
                [
                    config["key"],
                    config["last_modified"],
                    resource_base_type,
                    is_keyvault_ref,
                    config["read_only"],
                ]
            )
            line = "key: {key}, last_modified: {last_modified}, read_only: {read_only}".format(
                key=config["key"],
                last_modified=config["last_modified"],
                read_only=config["read_only"],
            )
            logging.info(line)
        except Exception as e:
            exception_message = "feature_flag: {feature_id}, last_modified: {last_modified}, value: {value}".format(
                feature_id=config["feature_id"],
                last_modified=config["last_modified"],
                value=str(config["value"]),
            )
            except_block(exception=e, exception_message=exception_message)
    output_table.add_rows(table)
    logging.info(output_table.draw())


def getValue(key, deactivate_kv_access=False, label=None):
    response = ""
    appConfigurationConnectionString = os.environ["APPCONFIGURATION_CONNECTION_STRING"]
    app_config_client = AzureAppConfigurationClient.from_connection_string(
        appConfigurationConnectionString
    )
    try:
        retrieved_config_setting = app_config_client.get_configuration_setting(
            key=str(key), label=label
        )
        config_type = retrieved_config_setting.as_dict()["content_type"]
        if (deactivate_kv_access == False) and ("keyvaultref" in config_type):
            response = _keyVaultAccess(key=json.loads(retrieved_config_setting.value))
        else:
            response = retrieved_config_setting.value
        logging.info("Key: " + retrieved_config_setting.key + ", Value: " + response)
    except:
        for config in app_config_client.list_configuration_settings():
            retrieved_config_setting = config.as_dict()
            if "feature_id" in retrieved_config_setting.keys():
                if retrieved_config_setting["feature_id"] == key:
                    logging.info(
                        "Key: "
                        + retrieved_config_setting["feature_id"]
                        + ", Value: "
                        + retrieved_config_setting["value"]
                    )
                    response = json.loads(retrieved_config_setting["value"])["enabled"]
    return response


def setValue(
    key,
    value=None,
    content_type="charset=utf-8",
    tags: dict = {},
    label=None,
    deactivate_kv_access=False,
):
    config_setting = ConfigurationSetting(
        key=key, label=label, value=value, content_type=content_type, tags=tags
    )
    response = ""
    appConfigurationConnectionString = os.environ["APPCONFIGURATION_CONNECTION_STRING"]
    app_config_client = AzureAppConfigurationClient.from_connection_string(
        appConfigurationConnectionString
    )
    try:
        retrieved_config_setting = app_config_client.get_configuration_setting(
            key=str(key), label=label
        )
        config_type = retrieved_config_setting.as_dict()["content_type"]
        if (deactivate_kv_access == False) and ("keyvaultref" in config_type):
            response = _keyVaultAccess(key=json.loads(retrieved_config_setting.value))
        else:
            response = retrieved_config_setting.value
        logging.info(
            "Key: "
            + retrieved_config_setting.key
            + ", Value: "
            + response
            + " already present, starting override"
        )
    except:
        response = app_config_client.set_configuration_setting(config_setting)
        logging.info("Key: " + key + ", Value: " + value + " has been set")
    return response
