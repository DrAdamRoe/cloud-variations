
## Pre-installed Requirements 
- Python 3.8 
- git 
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/quickstart)

## Installation 
- mkdir WORKING_DIR && cd WORKING_DIR
- git clone 
- install venv with python 3.8, e.g. `python3.8 -m venv venv` on POSIX systems (incl. macOS)
- `pip install -r requirements.tst`

## Local Development  

- Activate your virtual environment for this project: 
   
    macOS/Linux: `source venv/bin/activate`
    
    Windows: `venv\Scripts\activate.bat`

- Point Flask to your application: 

    macOS/Linux:  `export FLASK_APP=main.py`
    
    Windows: `set FLASK_APP=main.py`

- run your flask application: 

    `flask run`

Once you are running, you should be able to see a JSON response in the browser by navigating to http://localhost:5000 or by using cURL to GET a response, e.g. `curl localhost:5000`.


## The Cloud Variations 

Now that you have a local version of our highly sophisticated API running, the goal is to deploy it. If you are already familiar with Google Cloud Platform, skip ahead to the deployment part. 

- Make sure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/quickstart) installed already. If you have an older version, be sure to [update it](https://cloud.google.com/sdk/gcloud/reference/components/update)

- You will need to [get class credits]() at this stage, or use credits you already have. That will enable you to actually deploy stuff. 

- If you have never used Google Cloud Before, you might find it easier to first create an account on the browser and [poke around the dashboard](https://console.cloud.google.com/). We will use both the CLI and the Dashboard in these exercises. 

### Prepare your Google Cloud Account
In GCP, a Project is the top-level organizational element. You can learn more about it [here](https://cloud.google.com/storage/docs/projects) or elsewhere. We will use one project for the following examples, but feel free to create more, for instance, one project per variation, if you would like. 


Create a GCP project: 

 `gcloud projects create cloud-variations-fs20201 --name="Cloud Variations"`

You should be able to see this in your dashboard on Google Cloud after a few seconds. Now, we're ready for our first deployment! You can also get information from the CLI using `describe`, e.g. 

`gcloud projects describe cloud-variations-fs20201`

which will show information including status, name, and the projectId, which we will need in the next step. 

Once creating this project, set your local environment to default to using that new project: 

`gcloud config set project cloud-variations-fs20201`

This ensures that it will not conflict with any other projects you may have on GCP.

Before we start deploying, we have to enable the Cloud Build API, which several of the services we will use depend on:

`gcloud services enable cloudbuild.googleapis.com`

Note that this step is a little bit finnicky. If you have errors here, there is likely a problem with the credits or billing. You may have to go into the console and associate the credits you have received with this new project. 

## Variation: Functions-as-a-Service (Google Cloud Functions)

We begin with the most high-level, abstract, hands-of approach to running our service: Functions, also called "Serverless" or "Lambda". We need to provide Google only with our code itself and some basic options, and it will run it for us. 

Enable the cloud functions service on your project:

`gcloud services enable cloudfunctions.googleapis.com`

And now we will deploy a single _function_ from our application, the function `index()` found in the file `api/hello_cloud.py`: 

`gcloud functions deploy hello_cloud --runtime python38 --trigger-http --allow-unauthenticated --max-instances 2 --set-build-env-vars=GOOGLE_FUNCTION_SOURCE=api/hello_cloud.py`

This reads as: "Hey Google, deploy a Cloud Function for me called hello_cloud, which is both the name of the function that I've defined as well as the name that you'll use to identify the function. That function in the file api/hello_cloud.py. It should use the Python 3.8 runtime, anyone can access it on the internet without authentication, but only allow 2 instance to not run up my bill. Run the function if there is an HTTP request to the URI". 

And there we have it. 

## Variation: Platform-as-a-Service (Google App Engine)

In this variation, we will use Google's Platform-as-Service offering, Google App Engine. Our entire Flask app will be built, run, and managed by Google Cloud with minimal configuration on our side. We specify the Python runtime, the size of the target server, and some routing rules -- Google Cloud handles the rest (including things like installing the packages listed in our `requirements.txt` file)

Create an instance of an App, either from the CLI or through the dashboard. Be sure to get the projectId from the previous step: 

`gcloud app create --project=cloud-variations-fs20201 --region=europe-west3`

again, you can check it's status at the CLI or the dashboard: 

`gcloud app describe --project=cloud-variations-fs20201`

Note that at this stage, you have created an application, but there is nothing being served yet. You will automatically have a custom URL for this project, which has the format PROJECT_ID.appspot.com, in my case https://cloud-variations-fs20201.appspot.com. If you navigate to your own URL, you will get a 404: there is nothing being served there yet. 

Now, we can deploy our app! The application configuration is entirely described in a single file, called `app-engine.yaml`. To deploy, we will tell app engine to use the configuration we have detailed in that file: 

`gcloud app deploy app-engine.yaml`

And there we have it: your app is deployed! Look at that yaml file and see what we need to describe the infrastructure: a runtime (python version), an instance class (the size of the VM we will us, in this case, [F2](https://cloud.google.com/appengine/docs/standard), with a half GB of RAM), and some routing rules - similar to what we would need to define for a web server application like nginx, Caddy, or Apache. This tells app engine to respond to any request with the response of our application (as opposed to a redirect request, serving a static file, or an error, for instance.

## Variation: Managed Kubernetes Cluster (GKE)

We've already run some high-level managed versions of our API, and now we are going to take things a bit more into our own hands, running our service in Kubernetes. We will use Google Kubernetes Engine, Google's managed Kubernetes cluster, so we only have to _use_ Kubernetes, not host it ourselves. 

In this version, we will build the container ourselves (using Docker), push it to Google Cloud's container registry, configure and deploy our container to Kubernetes. 

First, make sure that you have [Docker](https://www.docker.com/products/docker-desktop) installed and running locally. 

Build a Docker image, based on the Dockerfile provided for you in this repository: 

`docker build --tag hello-cloud .`

and run it locally: 

`docker run --publish 5000:5000 hello-cloud`

At this point, you should be able to again make a request locally, via `curl localhost:5000` or by going to the browser. 

At this stage it is worth it to have a look at our Dockerfile, even if you aren't very familiar with Docker. We first define which base image we are using - in this case, an imagine provided by the Python Organization built on top of Debian 10 (codename buster). This gives us an operating system and everything we need to run Python 3.8. Then, we copy files from our local development environment into Docker's working area, and after that, we do the same thing as we do locally without Docker: install packages, set an environment variable, and run the app. Just this time, it is running as a Docker container on our own computer. 

Now it's time to run our Docker container on the cloud. 

Start by Enabling the Artifact Registry and Google Kubernetes Engine APIs: 

`gcloud services enable artifactregistry.googleapis.com`
`gcloud services enable container.googleapis.com`

Before we forget, let's push our recently built Docker Image to Google's Artifact Repository, later allowing it to be pulled by the Kubernetes Cluster we are going to set up. 

Use the tool provided by gCloud to authorize yourself on Docker on your machine to push to your Google Cloud Artifact Registry: 

`gcloud auth configure-docker europe-west3-docker.pkg.dev`

Next, create a repository in the Artifact Registry for you to store your image in: 

`gcloud artifacts repositories create hello-cloud --repository-format=docker --location=europe-west3`

Now you can tag your local image to push to a specific location, telling Docker where you will push it -- the repository you just created. You should replace `cloud-variations-fs2021` with your project name: 

`docker tag hello-cloud:latest europe-west3-docker.pkg.dev/cloud-variations-fs20201/hello-cloud/hello-cloud:latest`

And finally, push it to Google's Artifact Repository: 

`docker push europe-west3-docker.pkg.dev/cloud-variations-fs20201/hello-cloud/hello-cloud:latest`

Phew. We've built a Docker image locally and pushed it to Google Cloud. 


Now we can create a Kubernetes cluster: 

`gcloud container clusters create hello-cloud-cluster --num-nodes=1`

Aha, but we crash out with an error that says _Please specify location_. Now that we are taking control of our infrastructure, we have to decide where it runs. Let's set it to Frankfurt: 

`gcloud config set compute/zone europe-west3-b`

and try again to create the cluster with the above command. Now you should get a few yellow warnings, but no red errors. 

! Note at this point that if you have trouble with further installation and configuration, you access the [gCloud Shell](https://cloud.google.com/shell) through your browser, giving you a command line interface allowing you to interact with your project. 

And now we are ready to interact with our Kubernetes cluster!

Of course, we first need to [install kubectl](https://kubernetes.io/docs/tasks/tools/), the command line interface for interacting with Kubernetes itself. 

Use the gcloud-provided tool to configure your kubectl on your machine for interacting with your cluster on gcloud: 

`gcloud container clusters get-credentials hello-cloud-cluster`

Now, try to find out a bit about your cluster using `kubectl describe`, for example `kubectl describe nodes`, which will show a whole lot of hard to understand information about your kubernetes cluster. 

Create a Kubernetes deployment based on our Docker image, effectively declaring that we want our Docker image to run in Kubernetes:

`kubectl create deployment hello-cloud-server --image=europe-west3-docker.pkg.dev/cloud-variations-fs20201/hello-cloud/hello-cloud:latest`

It's running already, but we have to expose it on the network to see it, mapping our local port 5000 to the public port 80 for HTTP: 

`kubectl expose deployment hello-cloud-server --type LoadBalancer --port 80 --target-port 5000`

You can now find the public (external) IP address of your application using: 

`kubectl get service hello-cloud-server`

In my case, I see 34.107.66.217, which I can now access in the browser at http://34.107.66.217 or locally via curl again, `curl 34.107.66.217`.

That's "it"! Your very own Docker container running on your very own Kubernetes Cluster. 

Before you leave: shut off your Kube cluster, otherwise you'll run out of money, shutting off the load balancer and then your cluster: 

`kubectl delete service hello-cloud-server`

`gcloud container clusters delete hello-cloud-cluster`







