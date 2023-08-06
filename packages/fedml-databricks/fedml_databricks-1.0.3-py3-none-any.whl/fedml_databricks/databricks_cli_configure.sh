#!/usr/bin/env bash
DATABRICKS_URL=$1
DATABRICKS_ACCESS_TOKEN=$2

echo "Configuring databricks-cli."
echo "populating [~/.databrickscfg]"
> ~/.databrickscfg
echo "[DEFAULT]" >> ~/.databrickscfg
echo "host = $DATABRICKS_URL" >> ~/.databrickscfg
echo "token = $DATABRICKS_ACCESS_TOKEN" >> ~/.databrickscfg
echo "" >> ~/.databrickscfg
