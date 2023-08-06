#!/usr/bin/env bash

service_name=$1
profile_name=$2
num_instances=$3
kubeconfig_path=$4
model_uri=$5
databricks_config_path=$6

function kyma_deploy()
{
cat<< EOF | kubectl apply --validate=false -n $deploy_namespace -f -
apiVersion: v1
kind: Service
metadata:
  name: ${service_name}
  labels:
    run: ${service_name}
spec:
  ports:
  - name: http
    port: 8080
  selector:
    run: ${service_name}

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${service_name}
  labels:
    run: ${service_name}
spec:
  selector:
    matchLabels:
      run: ${service_name}
  replicas: ${num_instances}
  template:
    metadata:
      labels:
        run: ${service_name}
    spec:
      imagePullSecrets:
        - name: ${profile_name}-aws-ecr
      containers:
        - image: ${fullname}
          name: ${service_name}
          ports:
          - containerPort: 8080

---

apiVersion: gateway.kyma-project.io/v1alpha1
kind: APIRule
metadata:
  name: foldername
spec:
  gateway: kyma-gateway.kyma-system.svc.cluster.local
  service:
    name: ${service_name}
    port: 8080
    host: ${service_name}
  rules:
    - path: /.*
      methods: ["GET", "POST"]
      mutators: []
      accessStrategies:
        - handler: noop
          config: {}
EOF

kubectl rollout status deployment/${service_name}
if [ $? -ne 0 ]; then
    echo 'ERROR: model deployment failed!'    
    exit 1
fi
}

export MLFLOW_TRACKING_URI='databricks'
mlflow models build-docker --model-uri $model_uri --name ${service_name}
if [ $? -ne 0 ]; then
  echo "Mlflow model build failed. Please validate DATABRICKS_URL,DATABRICKS_ACCESS_TOKEN and MODEL_URI values passed in the ${databricks_config_path}  file."
  exit 1
fi

export AWS_PROFILE=${profile_name}
export KUBECONFIG=${kubeconfig_path}

#Getting the namespace and current context to deploy to
deploy_namespace=$(kubectl config view --minify --output 'jsonpath={..namespace}'; echo)
if [ $? -ne 0 ]; then
  echo "Failed to retrieve the kubectl config."
  exit 1
fi
[ -z "$deploy_namespace" ] && deploy_namespace=$(echo 'default')

# If the repository doesn't exist in ECR, create it.
aws ecr describe-repositories --repository-names "${service_name}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${service_name}" > /dev/null
    if [ $? -ne 0 ]
    then
        echo "Error creating repository. Please ensure 'aws configure --profile' is run with the named profile (${profile_name}) and also validate the PROFILE_NAME (${profile_name}) value passed in the ${databricks_config_path} file."    
        exit 1
    fi
fi

# Get the region defined in the current configuration (default to us-west-2 if none defined)
region=$(aws configure get region --profile ${profile_name})
if [ $? -ne 0 ]
then
    echo "Error obtaining the region. Please ensure 'aws configure --profile' is run with the named profile (${profile_name}) and also validate the PROFILE_NAME (${profile_name}) value passed in the ${databricks_config_path} file."    
    exit 1
fi
# Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]
then
    echo "Error obtaining the account id. Please ensure 'aws configure --profile' is run with the named profile (${profile_name}) and also validate the PROFILE_NAME (${profile_name}) value passed in the ${databricks_config_path} file."    
    exit 1
fi

#get login command form ECR and execute it directly. and store password as secret.
kubectl delete secret "${profile_name}-aws-ecr" --ignore-not-found
password=$(aws ecr get-login-password --region ${region} --profile ${profile_name})
if [ $? -ne 0 ]
then
    echo "Error obtaining the aws ecr password. Please ensure 'aws configure --profile' is run with the named profile (${profile_name}) and also validate the PROFILE_NAME (${profile_name}) value passed in the ${databricks_config_path} file."    
    exit 1
fi
kubectl create secret docker-registry "${profile_name}-aws-ecr" --docker-server="${account}".dkr.ecr."${region}".amazonaws.com --docker-username='AWS' --docker-password=${password}
if [ $? -ne 0 ]; then
    echo "ERROR: couldn't create secret in Kyma!"  
    exit 1
fi

aws ecr get-login-password --region ${region}  --profile ${profile_name} | docker login --username AWS --password-stdin "${account}".dkr.ecr."${region}".amazonaws.com
if [ $? -ne 0 ]; then
    echo "ERROR: docker login aws failed!. Please ensure 'aws configure --profile' is run with the named profile (${profile_name}) and also validate the PROFILE_NAME (${profile_name}) value passed in the ${databricks_config_path} file."    
    exit 1
fi
timestamp=$(date +%s%3N)
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${service_name}:${timestamp}"
docker tag ${service_name} ${fullname}
if [ $? -ne 0 ]; then
    echo "ERROR: docker tag failed!"    
    exit 1
fi

docker push ${fullname}
if [ $? -ne 0 ]; then
    echo "ERROR: docker push failed!"    
    exit 1
fi

kyma_deploy
