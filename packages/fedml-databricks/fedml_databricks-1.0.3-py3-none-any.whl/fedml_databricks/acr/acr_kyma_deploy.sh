#!/usr/bin/env bash

MODEL_URI=$1
SERVICE_NAME=$2
ACR=$3
KUBECONFIG_PATH=$4
SERVICE_PRINCIPAL_ID=$5
SERVICE_PRINCIPAL_PASSWORD=$6
CLUSTER_NAME=$7
NUM_REPLICAS=$8
DATABRICKS_CONFIG_PATH=$9

export KUBECONFIG=${KUBECONFIG_PATH}

function kyma_deploy()
{
cat<< EOF | kubectl apply --validate=false -n $deploy_namespace -f -
apiVersion: v1
kind: Service
metadata:
  name: ${SERVICE_NAME}
  namespace: ${deploy_namespace}
  labels:
    run: ${SERVICE_NAME}
spec:
  ports:
  - name: http
    port: 8080
    protocol: TCP
  selector:
    run: ${SERVICE_NAME}

---

apiVersion: gateway.kyma-project.io/v1alpha1
kind: APIRule
metadata:
  name: ${SERVICE_NAME}-api-rule
spec:
  gateway: kyma-gateway.kyma-system.svc.cluster.local
  service:
    name: ${SERVICE_NAME}
    port: 8080
    host: ${SERVICE_NAME}
  rules:
    - path: /.*
      methods: ["GET", "POST"]
      mutators: []
      accessStrategies:
        - handler: allow
          config: {}
          
---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${SERVICE_NAME}
  namespace: ${deploy_namespace}
spec:
  replicas: ${NUM_REPLICAS}
  ports:
    - name: http
      port: 8080
  selector:
    matchLabels:
      run: ${SERVICE_NAME}
  template:
    metadata:
      labels:
        run: ${SERVICE_NAME}
    spec:
      containers:
        - image: ${acr_image}
          name: ${SERVICE_NAME}
          imagePullPolicy: Always
          ports:
            - containerPort: 8080
      imagePullSecrets:
        - name: ${secret_name}
EOF

kubectl rollout status deployment/${SERVICE_NAME}
if [ $? -ne 0 ]; then
    echo "Deployment failed. Please valide the SERVICE_PRINCIPAL_ID,SERVICE_PRINCIPAL_PASSWORD and ACR values passed in ${DATABRICKS_CONFIG_PATH} file."
    kubectl describe deployment ${SERVICE_NAME}
    exit 1
else
  echo "The scoring uri is https://${SERVICE_NAME}.${CLUSTER_NAME}/invocations"
fi
}

function update_secret()
{
      echo "Updating the secret $secret_name password."
      kubectl -n $deploy_namespace delete secret $secret_name
      kubectl create secret docker-registry ${secret_name} --docker-server=$ACR --docker-username=${SERVICE_PRINCIPAL_ID} --docker-password=${SERVICE_PRINCIPAL_PASSWORD} -n ${deploy_namespace} 
      if [ $? -ne 0 ]; then
          echo "Creation of secret with name $secret_name for acr registry $ACR in the namespace $deploy_namespace failed."
          exit 1
      fi
      echo "Successfully updated $secret $secret_name."
}


function create_secret()
{
    secret_name=$(echo ${ACR}-${SERVICE_PRINCIPAL_ID}-secret)
    echo "Searching if the secret $secret_name exists in namespace $deploy_namespace."
    secret_exists=$(kubectl -n $deploy_namespace get secret -o json | jq -r ".items[].metadata.name" | grep -E "^${secret_name}$")
    if  ! [[ $secret_exists ]]; then
        echo "Creating secret with name $secret_name for acr registry $ACR in the namespace $deploy_namespace."
        kubectl create secret docker-registry ${secret_name} --docker-server=${ACR} --docker-username=${SERVICE_PRINCIPAL_ID} --docker-password=${SERVICE_PRINCIPAL_PASSWORD}  -n ${deploy_namespace} 
        if [ $? -ne 0 ]; then
          echo "Creation of secret with name $secret_name for acr registry $ACR in the namespace $deploy_namespace failed."
          exit 1
        fi
        echo "Secret $secret_name for acr registry $ACR created in the namespace $deploy_namespace."
    else
        dockerconfig=$(kubectl -n $deploy_namespace get secret $secret_name -o json | jq '.data[".dockerconfigjson"]'| base64 -di)
        if [ $? -ne 0 ]; then
            echo "Could not retrieve the secret $secret_name credentials. Updating the secret with current password."
            update_secret
            return 0
        fi
        sp_password=$(echo $dockerconfig | jq --arg acr $ACR '.auths[$acr]["password"]')
        if [ $? -ne 0 ]; then
            echo "Could not retrieve the secret $secret_name password. Updating the secret with current password."
            update_secret
            return 0
        fi
        
        if [ \"${SERVICE_PRINCIPAL_PASSWORD}\" == "$sp_password" ]; then
          echo "Using the same secret $secret_name for the deployment."
        else
            update_secret
        fi
    fi
    return 0
}
timestamp=$(date +%s%3N)
acr_image=$(echo ${ACR}/fedml/${SERVICE_NAME}:${timestamp})
echo "Building docker image ${acr_image}"
export MLFLOW_TRACKING_URI='databricks'
mlflow models build-docker --model-uri $MODEL_URI --name $acr_image
if [ $? -ne 0 ]; then
  echo "Mlflow model build failed. Please validate DATABRICKS_URL,DATABRICKS_ACCESS_TOKEN and MODEL_URI values passed in the ${DATABRICKS_CONFIG_PATH} file."
  exit 1
fi


echo "Authenticating to Azure Container registry ${ACR}"
echo "$SERVICE_PRINCIPAL_PASSWORD" | docker login $ACR --username $SERVICE_PRINCIPAL_ID --password-stdin
if [ $? -ne 0 ]; then
  echo "Authentication to Azure Container registry ${ACR} failed. Please validate ACR, SERVICE_PRINCIPAL_ID and SERVICE_PRINCIPAL_PASSWORD  values passed in the ${DATABRICKS_CONFIG_PATH} file and ensure that the Service Principal ${SERVICE_PRINCIPAL_ID} has 'AcrPush' role in the Azure Container Registry ${ACR}."
  exit 1
fi
echo "Pushing the docker image ${acr_image} to Azure container registry ${ACR}"
docker push $acr_image
if [ $? -ne 0 ]; then
  echo "Pushing image to ACR failed. Please validate ACR, SERVICE_PRINCIPAL_ID and SERVICE_PRINCIPAL_PASSWORD  values passed in the ${DATABRICKS_CONFIG_PATH} file and ensure that the Service Principal ${SERVICE_PRINCIPAL_ID} has 'AcrPush' role in the Azure Container Registry ${ACR}."
  exit 1
fi

#Getting the namespace and current context to deploy to
deploy_namespace=$(kubectl config view --minify --output 'jsonpath={..namespace}'; echo)
if [ $? -ne 0 ]; then
  echo "Failed to retrieve the kubectl config."
  exit 1
fi
[ -z "$deploy_namespace" ] && deploy_namespace=$(echo 'default')

#check if a deploy namespace exists if not creates it
echo "Checking if the deploy namespace $deploy_namespace exists."
deploy_namespace_exists=$(kubectl get namespaces -o json | jq -r ".items[].metadata.name" | grep -E "^${deploy_namespace}$")
if [ $? -ne 0 ]; then
  echo "Failed to check if the deploy namespace exists."
  exit 1
fi

if  ! [[ $deploy_namespace_exists ]]; then
    echo "Creating deploy namespace $deploy_namespace."
    kubectl create namespace $deploy_namespace
    if [ $? -ne 0 ]; then
      echo "Failed to create namespace $deploy_namespace."
      exit 1
    fi
    echo "Namespace deploy $deploy_namespace created."
else
  echo "Using existing deploy namespace $deploy_namespace."
fi


#Check if the secret exists. if it exists use it or create a new secret. If the updated secret password is passed then it is updated.
create_secret

#deploy to kyma
kyma_deploy
exit 0



    


  




