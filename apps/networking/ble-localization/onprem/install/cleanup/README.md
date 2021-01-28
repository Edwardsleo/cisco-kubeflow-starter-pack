# Resource Cleanup 

We are deleting unused docker images, stopped containers and deleting files from nfs volume, katib experiments, workflows that are older than 'X' days.
Cron job approach was shown below, though one may try other approaches.

## Creating a Cron Job

CronJob runs a job periodically on a given schedule, written in Cron format.

Create a Cron job using [cronjob.yaml](cronjob.yaml) config file

```
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: clean-up
  namespace: kubeflow
spec:
  schedule: "0 0 */3 * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: samba07/cronjob:0.2
            imagePullPolicy: IfNotPresent
            args: ["--age",  "40d",
                   "--days", "10"
                  ]
            volumeMounts:
            - mountPath: "/var/run"
              name: docker-daemon
          restartPolicy: OnFailure
          volumes:
          - name: docker-daemon
            hostPath:
              path: /var/run
              type: Directory
```
* `schedule`: CronJob schedule expression. To generate CronJob schedule expressions, you can also use web tools like [crontab.guru](https://crontab.guru/).
* `age` : Provide number of older days to delete katib experiments and workflows.
* `days` : Provide number of older days to delete files from nfs volume

Run the CronJob by using this command

```
kubectl create -f cronjob.yaml
```
Expected Output

```
cronjob.batch/clean-up created
```

After creating the cron job, get its status using following command

```
kubectl get cronjob  -n kubeflow
```
Expected Output

```
NAME       SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
clean-up   */1 * * * *   False     1        4s              8s
```

```
kubectl get jobs -n kubeflow
```
Expected Output

```
NAME               COMPLETIONS   DURATION   AGE
clean-up-1611049680   0/1                      0s
clean-up-1611049680   0/1           0s         0s
clean-up-1611049680   1/1           5s         5s
```
Show pod log

```
pods=$(kubectl -n kubeflow get pods --selector=job-name=clean-up-1611049680 --output=jsonpath={.items[*].metadata.name})
kubectl logs $pods -n kubeflow
```

## Deleting a Cron Job

When you don't need a cron job any more, delete it with following command

```
kubectl delete cronjob clean-up -n kubeflow
```
