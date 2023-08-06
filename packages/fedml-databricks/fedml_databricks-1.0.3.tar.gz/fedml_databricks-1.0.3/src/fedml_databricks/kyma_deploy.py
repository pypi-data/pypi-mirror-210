import json
from .logger import Logger
from pkg_resources import resource_filename
from .acr.acr_kyma_deploy import _acr_kyma_deploy
from .ecr.ecr_kyma_deploy import _ecr_kyma_deploy
from .deployment_helper import _execute_script,_check_file_exists

def _check_key_exist(required_keys,config,config_path):
    logger = Logger.get_instance()
    try:
        for key in required_keys:
            if key not in config:
                raise Exception("The key {} not found in config file {}.".format(key,config_path))
    except Exception as e:
        logger.error(e)
        raise

def _validate_config(config,config_path):
    logger = Logger.get_instance()
    try:
        required_keys=["DATABRICKS_URL","DATABRICKS_ACCESS_TOKEN","MODEL_URI","SERVICE_NAME","KUBECONFIG_PATH","CONTAINER_REGISTRY_TYPE"]
        _check_key_exist(required_keys,config,config_path)

        if not _check_file_exists(config['KUBECONFIG_PATH']):
            raise Exception("The kubeconfig path {} not found. Please validate the 'KUBECONFIG_PATH' value passed in {} ".format(config['KUBECONFIG_PATH'],config_path))

        if config["CONTAINER_REGISTRY_TYPE"].lower()=="acr":
            acr_required_keys=["SERVICE_PRINCIPAL_ID","SERVICE_PRINCIPAL_PASSWORD","ACR"]
            _check_key_exist(acr_required_keys,config,config_path)
        
        elif config["CONTAINER_REGISTRY_TYPE"].lower()=="ecr":
            ecr_required_keys=["PROFILE_NAME"]
            _check_key_exist(ecr_required_keys,config,config_path)
        
        else:raise Exception("The CONTAINER_REGISTRY_TYPE '{}' is not supported. The CONTAINER_REGISTRY_TYPE currently supported are 'ACR','ECR'.".format(config['CONTAINER_REGISTRY_TYPE']))

    except Exception as e:
        logger.error(e)
        raise


def deploy_to_kyma(databricks_config_path):
    logger = Logger.get_instance()
    try:
        if not _check_file_exists(databricks_config_path):
            raise Exception("The databricks config file not found in path {}.".format(databricks_config_path))

        with open(databricks_config_path, 'r') as f:
            databricks_config = json.load(f)
        
        _validate_config(databricks_config,databricks_config_path)
        databricks_cli_configure_script_path = resource_filename(__name__, "databricks_cli_configure.sh")
        configure_databricks=_execute_script(["bash",databricks_cli_configure_script_path,databricks_config["DATABRICKS_URL"],databricks_config["DATABRICKS_ACCESS_TOKEN"]])
        if configure_databricks!=0:raise Exception("Databricks cli configuration failed. Please validate the DATABRICKS_URL and DATABRICKS_ACCESS_TOKEN values passed in {}".format(databricks_config_path))

        overwrite_service=databricks_config['OVERWRITE_SERVICE'] if 'OVERWRITE_SERVICE' in databricks_config else "false"
        install_validate_script_path = resource_filename(__name__, "kubectl_install_validate.sh")
        install_result=_execute_script(["bash",install_validate_script_path,databricks_config['SERVICE_NAME'],databricks_config['KUBECONFIG_PATH'],overwrite_service])
        if install_result==12:
            raise Exception("The service name '{}' already exists. Please provide a different 'SERVICE_NAME' in databricks config path {}. If you want the service and deployment to be replaced, set the key 'OVERWRITE_SERVICE' in the path {} to 'true'".format(databricks_config['SERVICE_NAME'],databricks_config_path,databricks_config_path))
        elif install_result!=0:raise Exception("Please check the error.")

        if databricks_config["CONTAINER_REGISTRY_TYPE"].lower()=="acr":
           return  _acr_kyma_deploy(databricks_config,databricks_config_path)
        
        elif databricks_config["CONTAINER_REGISTRY_TYPE"].lower()=="ecr":
            return  _ecr_kyma_deploy(databricks_config,databricks_config_path)
        
    except Exception as e:
        logger.error(e)
        raise

