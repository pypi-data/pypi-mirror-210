import logging
import json
import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import logging    
import datetime
from texttable import Texttable

def exceptBlock(inst, exceptionMessage="No message"):
    exceptionMessage = exceptionMessage
    exceptionTimne = str(datetime.datetime.now())
    exceptionType = str(type(inst))
    exceptionArgument = str(inst.args)
    exceptionInstance = str(inst)
    logging.info("Exception message: {message}".format(message=exceptionMessage))
    logging.info("Exception occured at: {message}".format(message=exceptionTimne))
    logging.info("Exception instance type: {message}".format(message=exceptionType))
    logging.info("Exception argument: {message}".format(message=exceptionArgument))
    logging.info("Exception instance: {message}".format(message=exceptionInstance))

def _keyVaultAccess(key):
    try:
        key_vault_uri = str(key["uri"]).split('/secrets/')[0]
        secret_name = str(key["uri"]).split('/secrets/')[1]
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        client = SecretClient(vault_url=key_vault_uri, credential=credential)
        retrieved_secret = client.get_secret(secret_name)
    except Exception as inst:
        exceptionMessage="KeyVault access failed"
        exceptBlock(inst=inst, exceptionMessage=exceptionMessage)
    return retrieved_secret.value



def listConfig():
    output_table = Texttable()
    table = [['key', 'last_modified', 'content_type', 'keyVault_reference', 'access_level']]
    appConfigurationConnectionString = os.environ["APPCONFIGURATION_CONNECTION_STRING"]
    app_config_client = AzureAppConfigurationClient.from_connection_string(appConfigurationConnectionString)
    for config in app_config_client.list_configuration_settings():
        config = config.as_dict()
        try:
            resource_type_definition = config['tags']['type']
            resource_base_type = resource_type_definition.split(".")[1].split("/")[0]

            config_type = str(config['content_type']).lower()
            if "keyvaultref" in config_type:
                is_keyvault_ref = "True"
            else:
                is_keyvault_ref = "False"
            table.append([config['key'], config['last_modified'], resource_base_type, is_keyvault_ref, config['read_only']])
            line = "key: {key}, last_modified: {last_modified}, read_only: {read_only}".format(
                key=config['key'], last_modified=config['last_modified'], read_only=config['read_only'])
            logging.info(line)
        except Exception as inst:
            exceptionMessage = "feature_flag: {feature_id}, last_modified: {last_modified}, value: {value}".format(
                feature_id=config['feature_id'], last_modified=config['last_modified'], value=str(config['value']))
            exceptBlock(inst=inst, exceptionMessage=exceptionMessage)
    output_table.add_rows(table)
    logging.info(output_table.draw())
            



def getValue(key, deactivate_kv_access=False, label=None):
    response = ""
    appConfigurationConnectionString = os.environ["APPCONFIGURATION_CONNECTION_STRING"]
    app_config_client = AzureAppConfigurationClient.from_connection_string(appConfigurationConnectionString)
    try:
        retrieved_config_setting = app_config_client.get_configuration_setting(key=str(key), label=label)
        config_type = retrieved_config_setting.as_dict()['content_type']
        if (deactivate_kv_access==False) and ("keyvaultref" in config_type):
            response =  _keyVaultAccess(key=json.loads(retrieved_config_setting.value))    
        else:        
            response =  retrieved_config_setting.value
        logging.info("Key: " + retrieved_config_setting.key + ", Value: " + response)
    except:
        for config in app_config_client.list_configuration_settings():
            retrieved_config_setting = config.as_dict()
            if "feature_id" in retrieved_config_setting.keys():
                if retrieved_config_setting["feature_id"] == key:
                    logging.info("Key: " + retrieved_config_setting["feature_id"] + ", Value: " + retrieved_config_setting["value"])
                    response = json.loads(retrieved_config_setting["value"])["enabled"]
    return response

def setValue(key, value=None, content_type='charset=utf-8', tags: dict={}, label=None, deactivate_kv_access=False):
    config_setting = ConfigurationSetting(
        key=key,
        label=label,
        value=value,
        content_type=content_type,
        tags=tags
    )
    response = ""
    appConfigurationConnectionString = os.environ["APPCONFIGURATION_CONNECTION_STRING"]
    app_config_client = AzureAppConfigurationClient.from_connection_string(appConfigurationConnectionString)
    try:
        retrieved_config_setting = app_config_client.get_configuration_setting(key=str(key), label=label)
        config_type = retrieved_config_setting.as_dict()['content_type']
        if (deactivate_kv_access==False) and ("keyvaultref" in config_type):
            response =  _keyVaultAccess(key=json.loads(retrieved_config_setting.value))    
        else:        
            response =  retrieved_config_setting.value
        logging.info("Key: " + retrieved_config_setting.key + ", Value: " + response + " already present, starting override")
    except:
        response = app_config_client.set_configuration_setting(config_setting)    
        logging.info("Key: " + key + ", Value: " + value + " has been set")
    return response