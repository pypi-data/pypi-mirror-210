from ..logger import Logger
from ruamel.yaml import YAML
from pkg_resources import resource_filename
from ..deployment_helper import _execute_script,_check_file_exists

def _get_server_url(kubeconfig_path):
    logger = Logger.get_instance()
    try:
        with open(kubeconfig_path,'r') as fp:
            kubeconfig_details = YAML().load(fp)
        return kubeconfig_details['clusters'][0]['cluster']['server']
    except Exception as e:
        logger.error(e)
        raise


def _acr_kyma_deploy(databricks_config,databricks_config_path):
    logger = Logger.get_instance()
    try:
        server_url=_get_server_url(databricks_config['KUBECONFIG_PATH'])
        kyma_server_url = ".".join(server_url.split(".")[1:])
        num_replicas=str(databricks_config['NUM_REPLICAS']) if 'NUM_REPLICAS' in databricks_config else "1"
        acr_kyma_deploy_script_path = resource_filename(__name__, "acr_kyma_deploy.sh")
        deploy_result=_execute_script(['bash',acr_kyma_deploy_script_path,databricks_config["MODEL_URI"],databricks_config["SERVICE_NAME"],databricks_config["ACR"],databricks_config["KUBECONFIG_PATH"],databricks_config["SERVICE_PRINCIPAL_ID"],databricks_config["SERVICE_PRINCIPAL_PASSWORD"],kyma_server_url,num_replicas,databricks_config_path])
        if deploy_result==0:
            endpoint_url=" https://"+databricks_config['SERVICE_NAME']+"."+kyma_server_url+"/invocations"
            logger.info("The inference endpoint is:  {}".format(endpoint_url))
            return endpoint_url
        else:
            raise Exception("Deployment to kyma failed. Refer the deployment logs for more details.")

    except Exception as e:
        logger.error(e)
        raise