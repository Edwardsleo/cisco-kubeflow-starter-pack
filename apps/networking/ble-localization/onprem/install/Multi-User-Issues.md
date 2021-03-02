# List of issues/resolutions for KF 1.0 & 1.1.    
     

# Non-Dex/Regular 1.0 

1. Prometheus
     - Prometheus monitoring default manifest(istio ns) didnt work in 1.0 - worked with istio injection disabled on dcgm exporter
     - Also, Prometheus operator was installed in kubeflow namespace to enable monitoring - working
     - virtual service working
2. https/TLS
     - https redirect for http traffic *not working* on KF 1.0 - 301 redirect is happening on the same HOST:PORT which is causing the issue
     - https working directly
     - mlflow & visualization virtual service with https working
     
3. Katib 
     - Refactor component to enable all possible hyperparameter tuning - katib component changes are done, backward compatible
     - train component changes for accepting possible hyperparameters is complete
     - nfs install move to computer-vision app & update Readme

4. Grafana
     - grafana pod is running in istio-system ns, and able to render metrics from prometheues installed in kubeflow
     - virtual service didnt work - https://github.com/kubeflow/kubeflow/issues/5051, resolved with grafana-vs ini, matching method regex: GET|POST|PUT|DELETE
     - port forwarding also worked.
     
5.  Mlflow
     - mlflow deployment needs to read k8s secret - done
     - virtual svc done, code merged.

6. TF SSD Mobilenet v2 based pipeline
     - model inference graph script, export_tflite_graph_tf2.py, working
     - inference on model built of checkpoints is working, inference_tf2_colab.ipynb
     - tflite based inferencing verified.
     - meraki folks had completed a TF pipeline, not SSD.
     - pipeline in progress
 
 7. AWS RDS prototype
     - basic things are working, but from lab access issues are observed - could be firewall issue, try with different port.
     - componentization
     - ApertureDB ??
 8. Gitlab code move/CI
     - first cut done
     - compiling pipelines and uploading code is done
     - webhooks/Gitlab CI exploration
     - verifying pipelines with Gitlab CI?
 
 9. cert-manager?
 


# Non-Dex/Regular 1.1 

1. Pipelines 
     - 1.0/existing pipeline couldnt be triggered from user notebooks due to RBAC, pipeline api server restrictions in 1.1
     - could resolve with clusterRBAC OFF & also with ON_WITH_EXCLUSION using the below workarounds
          - https://github.com/kubeflow/pipelines/issues/4440#issuecomment-687689294 - service role binding
          - https://github.com/kubeflow/pipelines/issues/4440#issuecomment-687703390 - envoy filter
     - KFP SDK now needs to be passed with user namespace, which creates the pipelines in *user namespace* vs earlier KF namespace
     - changed the pipeline components download, katib, train to enable them run in user namespace
     - kubeflow nfs is no more required.
     - custom visualization is also served from anonymous namespace
     - visulization virtual service is also working.
     - local path PV also works
     
2. Notebooks are working
     - kubectl commands are working for both admin namespace and user namespace
 
3. Katib working in user namespace

4. nfs server backed by local path PV working

5. Prometheus
     - Prometheus monitoring default manifest(istio-system ns) didnt work in 1.0 - worked with istio injection disabled at deployment
     - Prometheus operator was installed in kubeflow namespace to enable monitoring, scraping is working
     - virtual service working
     
6. https/TLS
     - https redirect for http traffic *not working* on KF 1.1 - - 301 redirect is happening on the same HOST:PORT which is causing the issue
     - https working directly
     - mlflow & visualization virtual service working
     
7. Grafana
     - grafana pod is not running in istio-system ns, grafana isnt included in istio manifest (istio version => 1.3)
     - verified std grafana helm chart in kubeflow namespace, it works.
     - try regular istio instead of istio crd/install 1.3?
     - try our own custom dashboard.json

9. Cert-manager
     - exploration for intra service connections - mTLS??
     - we use openssl certificates as secrets for external connections?? investigation
     
11. Istio
     - api-server config required for 1.1?
     ```
     --service-account-signing-key-file=/etc/kubernetes/pki/sa.key - --service-account-issuer=kubernetes.default.svc needs to be added to /etc/kubernetes/manifests/kube-apiserver.yaml

## Dex/Multi-user issues


1. Istio
     - api-server config required for Dex 1.0 & 1.1
     ```
     --service-account-signing-key-file=/etc/kubernetes/pki/sa.key - --service-account-issuer=kubernetes.default.svc needs to be added to /etc/kubernetes/manifests/kube-apiserver.yaml
     ```
     
2. NFS/Profiles/namespaces/resourcequota
     - nfs/profiles provisioning scripts completed.
     - Not able to mount NFS volumes with dex 1.1 in user namespace - Resolved with istio-injection disabled in user namespace? by default enabled.
     - the code is in dex1.1 branch

3. Notebooks
      - Dex 1.1 - Working

4. Pipelines
     - local path PV for components - working
     - Dex 1.1 - pipelines not working, RBAC issue hit - #, resolved using servicerolebinding & envoyfilter

5. Katib 
     - Dex + 1.0/1.1 - working
     - local path PV - working
     - Tekton Pipelines?
           
6. Grafana
     - Grafana pod not running, grafana manifest isnt included (istio-grafana)

7. Prometheus
     - Prometheus monitoring default manifest(istio ns) didnt work in 1.0 (dex & non-dex both)
     - Prometheus operator was installed in kubeflow to enable monitoring
     - more issues with virtual service
     
8. https/TLS
     - https redirect not working on KF 1.0 + Dex

9. test servicerolebinding/.. scripts from inside the notebook, multi user - double check testing.
9. Argo Workflows??


     
