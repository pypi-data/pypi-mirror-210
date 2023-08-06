#!/usr/bin/env bash
service_name=$1
kubeconfig_path=$2
overwrite_service=$3

echo "Installing Kubectl"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(<kubectl.sha256)  kubectl" | sha256sum --check
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client

echo "Installing jq"
wget -O jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
chmod +x ./jq
sudo cp jq /usr/bin

export KUBECONFIG=${kubeconfig_path}
deploy_namespace=$(kubectl config view --minify --output 'jsonpath={..namespace}'; echo)
[ -z "$deploy_namespace" ] && deploy_namespace=$(echo 'default')
echo "The deploy namespace is ${deploy_namespace}."

deploy_namespace_exists=$(kubectl get namespaces -o json | jq -r ".items[].metadata.name" | grep -E "^${deploy_namespace}$")
if  [[ $deploy_namespace_exists ]]; then
    service_name_exists=$(kubectl -n ${deploy_namespace} get deployments -o json | jq -r ".items[].metadata.name"| grep -E "^${service_name}$")
    if  [[ $service_name_exists ]]; then
        if [ "$overwrite_service" = "true" ] ; then
            echo "Service and deployment with $service_name already exists. As the deploy_args['overwrite_service'] parameter is set to 'True', the existing service and deployment will be replaced."
        else
            echo "Service and deployment with $service_name already exists. Provide a different service name in deploy_args['name']. If you want the service and deployment to be replaced, set the parameter deploy_args['overwrite_service']  to 'True'."
            exit 12
        fi
    fi
fi

exit 0


