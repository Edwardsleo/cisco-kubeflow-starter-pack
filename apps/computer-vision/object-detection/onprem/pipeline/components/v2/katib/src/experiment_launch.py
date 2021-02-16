#Script to launch Katib experiment based on JSON experiment spec object

import argparse
import json
import yaml
from kubernetes.client import V1ObjectMeta
from kubeflow.katib import KatibClient
from kubeflow.katib import ApiClient
from kubeflow.katib import V1alpha3Experiment


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Katib Experiment launcher')

    parser.add_argument('--timestamp', type=str,
                        help='Experiment timestamp')
						
    parser.add_argument('--user_namespace', type=str, default='anonymous',
                        help='Experiment namespace')
						
    parser.add_argument('--image', type=str, default='',
                        help='training image for Katib')

    parser.add_argument('--nfs_path', type=str,
                        help='NFS path')
						
    parser.add_argument('--trials', type=int, 
                        help='No of trials to be run under the experiment')
						
    parser.add_argument('--weights', type=str, 
                        help='Pretrained weights')
						
    parser.add_argument('--cfg_file', type=str, 
                        help='The config file used to darknet training')

    parser.add_argument('--cfg_data', type=str, 
                        help='The config file containing data paths used for darknet training')
						
    parser.add_argument('--gpus', type=int, 
                        help='No of GPUs utilized to run a trial')
					
					
    parser.add_argument('--component_type', type=str, 
                        help='Will be either katib or train')
						
	
    parser.add_argument('--experiment_spec', type=str,
                        help='experiment specifications passed as a string')
					
					
						
    args = parser.parse_args()


   
    trial_template={"trialTemplate":{"goTemplate":{"rawTemplate":"apiVersion: batch/v1\nkind: Job\nmetadata:\n  name: {{.Trial}}\n  namespace: {{.NameSpace}}\nspec:\n  template:\n    spec:\n      containers:\n      - name: {{.Trial}}\n        image: %s\n        command:\n        - \"/opt/deploy.sh\"\n        - \"--nfs-path\"\n        - \"%s\"\n        - \"--weights\"\n        - \"%s\"\n        - \"--cfg_data\"\n        - \"%s\"\n        - \"--cfg_file\"\n        - \"%s\"\n        - \"--gpus\"\n        - \"%s\"\n        - \"--component\"\n        - \"%s\"\n        {{- with .HyperParameters}}\n        {{- range .}}\n        - \"{{.Name}}\"\n        - \"{{.Value}}\"\n        {{- end}}\n        {{- end}}\n        volumeMounts:\n        - mountPath: /mnt\n          name: nfs-volume\n        resources:\n          limits:\n            nvidia.com/gpu: %s\n      restartPolicy: Never\n      volumes:\n      - name: nfs-volume\n        persistentVolumeClaim:\n          claimName: nfs1"}}}

    raw_temp = trial_template['trialTemplate']['goTemplate']['rawTemplate']
     
    mod_raw_temp = raw_temp %(args.image, args.nfs_path,args.weights, args.cfg_data, args.cfg_file, args.gpus, args.component_type, args.gpus)
    
    trial_template['trialTemplate']['goTemplate']['rawTemplate'] = mod_raw_temp

    param_spec = args.experiment_spec

    param_spec = eval(param_spec)

    param_spec["maxTrialCount"] = args.trials

    param_spec.update(trial_template)

    param_spec_obj = json.dumps(param_spec,separators=(',',':'))

    class JSONObject(object):
         """ This class is needed to deserialize input JSON.
             Katib API client expects JSON under .data attribute.
         """

         def __init__(self, json):
             self.data = json
		
    
    # Create JSON object from experiment spec
    experiment_spec = JSONObject(param_spec_obj)

    #experiment_spec = ApiClient().sanitize_for_serialization(experiment_spec)
    
	
    # Deserialize JSON to ExperimentSpec
    experiment_spec = ApiClient().deserialize(experiment_spec, "V1alpha3ExperimentSpec")
    
    experiment_name = 'object-detection-' + args.timestamp

    timestamp = 'ts-' + args.timestamp

    # Create Experiment object.
    experiment = V1alpha3Experiment(
            api_version="kubeflow.org/v1alpha3",
            kind="Experiment",
            metadata=V1ObjectMeta(
                   name=experiment_name,
                   namespace=args.user_namespace,
                   labels={ 'controller-tools.k8s.io' : '1.0',
                            'timestamp' : timestamp }
                    ),
                  spec=experiment_spec
            )

    # Create Katib client.
    katib_client = KatibClient()
	
    # Create Experiment in Kubernetes cluster.
    output = katib_client.create_experiment(experiment, namespace=args.user_namespace)	
    print("*******Katib Experiment created successfully********")	

    json_serialise = json.dumps(output)


    # Write experiment spec to files
    ## JSON form

    with open((experiment_name + '.json'),'w') as file:
                   file.write(json_serialise)

    ## YAML form

    yaml_stream = yaml.dump(output)

    with open((experiment_name + '.yaml'),'w') as file:
                   file.write(yaml_stream)


