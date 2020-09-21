## Accessing the Katib UI

* You can access Kubeflow Dashboard using the Ingress IP, provided while running [nfs-installation](./../install#-provide-ucs-cluster-ip) script, and _31380_ port. For example, http://<INGRESS_IP:31380>

* Select _anonymous_ namespace and click Katib in the left panel of the Kubeflow Dashboard.

![COVID katib dashboard](pictures/27_katib_dashboard.png)

* You can use the Katib user interface (UI) to submit experiments and to monitor your results. The Katib home page within Kubeflow looks like

![COVID katib homepage](pictures/28_katib_homepage.PNG)

* Click Hyperparameter Tuning on the Katib home page.

* Open the Katib menu panel on the left, then open the **HP** section and click **Monitor**

![COVID katib monitor](pictures/29_katib_monitor.PNG)

* Click on the right-hand panel to close the menu panel. You should see the list of experiments.

![COVID katib list experiments](pictures/30_katib_list_experiments.PNG)

* Click the name of the experiment, **covid**

* You should see a graph showing the level of accuracy for various combinations of the hyperparameter values (batch size, optimizer).

![COVID katib experiment graph](pictures/31_katib_experiment_graph.PNG)

* Below the graph is a list of trials that ran within the experiment.

![COVID katib experiment trials](pictures/32_katib_experiment_trials.PNG)
