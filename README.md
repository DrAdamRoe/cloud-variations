
# The Cloud Variations 

This repository represents multiple ways to run a very simple server application on The Cloud. The goal is to get a feeling for different ways of operating (running) this simple application. The app itself is a hello world REST API with a JSON response, written in Python using Flask. The app itself is irrelevant, the ways of running it are the interested part. This repository accompanies a class at CODE University of Applied Sciences, taught in Autumn 2021. 

Pull Requests are highly welcome, for example for corrections, clarifications, or maintenance. 

## Table Of Contents
1. [The Cloud Variations](#the-cloud-variations)
1. [Local Installation and Operations](#Local-Installation-and-Operations)
1. [Starting on the Cloud](#Starting-on-The-Cloud)
1. [Variation: Functions-as-a-Service](#Variation-Functions-as-a-Service)
1. [Variation: Platform-as-a-Service](#Variation-Platform-as-a-Service)
1. [Intermission: Containerize the Application](#Intermission-Containerize-the-Application)
1. [Variation: Serverless Container Management](#Variation-Serverless-Container-Management)
1. [Variation: Managed Kubernetes Cluster](#Variation-Managed-Kubernetes-Cluster)
1. [Make This Your Own](#make-this-your-own)

## Local Installation and Operations 
The goal of this section is to install and run our little web server locally on your own computer, and get set up with the Google Cloud SDK and Account for the next steps. 

### Pre-Installed Requirements 
Before you get started, you are expected to have some other software on your computer

- Python 3.8 (tested with 3.8.6)
- git 
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/quickstart), (tested with version 357.0.0)
- An integrated development environment, like VS Code. 
- [Docker](https://www.docker.com/products/docker-desktop) for building and running docker images locally

### Install Locally   
- mkdir WORKING_DIR && cd WORKING_DIR, with a directory name of your choice (e.g. cloud2021). 
- git clone this repository locally

- Install a local python virtual environment with python 3.8 to work with, 

    macOS/Linux: `python3.8 -m venv venv` 
    
    Windows: `c:\Python38\python -m venv c:\path\to\myenv`

- Activate your virtual environment for this project: 
   
    macOS/Linux: `source venv/bin/activate`
    
    Windows: `venv\Scripts\activate.bat`

- Install packages: `pip install -r requirements.txt`


- Point Flask to your application: 

    macOS/Linux:  `export FLASK_APP=main.py`
    
    Windows: `set FLASK_APP=main.py`

- run your flask application: 

    `flask run`

Once you are running, you should be able to see a JSON response in the browser by navigating to http://localhost:5000 or by using cURL to GET a response, e.g. `curl localhost:5000`. You should now be able to see our message, `{"message": "Hello, Cloud!"}`, served locally.  

### Restarting your Local Development Environment

Note that every time you re-open your local development environment, you will have to navigate to your local directory, activate the virtual environment, and set the FLASK_APP environment variable in order to start flask 
 

## Starting on The Cloud

Now that you have a local version of our highly sophisticated API running, the goal is to deploy it. If you are already familiar with Google Cloud Platform, skip ahead to the deployment part. 

- Make sure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/quickstart) installed already. If you have an older version, be sure to [update it](https://cloud.google.com/sdk/gcloud/reference/components/update)

- You will need to [get class credits]() at this stage, or use credits you already have. That will enable you to actually deploy stuff. 

- If you have never used Google Cloud Before, you might find it easier to first create an account on the browser and [poke around the dashboard](https://console.cloud.google.com/). We will use both the CLI and the Dashboard in these exercises, but mostly the CLI. 

- If you have trouble with the local setup of the gCloud SDK, it is worth it to note that everything done here can be done in the browser, as well. You can still participate in the class and learn a lot, but the steps are not documented here -- you'll have to find that in the documentation online. 

### Prepare your Google Cloud Account
In GCP, a Project is the top-level organizational element. You can learn more about it [here](https://cloud.google.com/storage/docs/projects) or elsewhere. We will use one project for the following examples, but feel free to create more, for instance, one project per variation, if you would like. The names are entirely up to you; you are encouraged to customize them to your liking. 


Create a project on Google Cloud Platform: 

 `gcloud projects create cloud-variations-fs2021 --name="Cloud Variations"`

You should be able to see this in your dashboard on Google Cloud after a few seconds. Now, we're ready for our first deployment! You can also get information from the CLI using `describe`, e.g. 

`gcloud projects describe cloud-variations-fs2021`

which will show information including status, name, and the projectId, which we will need in the next step. 

Once creating this project, set your local environment to default to using that new project: 

`gcloud config set project cloud-variations-fs2021`

This ensures that it will not conflict with any other projects you may have on GCP.

Before we start deploying, we have to enable the Cloud Build API, which several of the services we will use depend on:

`gcloud services enable cloudbuild.googleapis.com`

Note that this step is a little bit finnicky. If you have errors here, there is likely a problem with the credits or billing. You may have to go into the console and associate the credits you have received with this new project. 

![gcloud billing account for project not found](./documentation/glcoud-projects-enable-cloudbuild.png) 

The goal is to associate the Education Credits you have received with this project. The easiest way to do this is [on the dashboard in the browser](https://cloud.google.com/billing/docs/how-to/modify-project#to_change_the_projects_account_do_the_following), but it can be done via the CLI as well. 

As of writing, there are [commands in the beta version of the gcloud SDK API](https://cloud.google.com/sdk/gcloud/reference/billing) which allow you to do this from the command line. First, use `gcloud beta billing accounts list` to get the ACCOUNT_ID of the account you want to use; if you are new to gCloud it should be the only account listed. The ID has a format like 0X0X0X-0X0X0X-0X0X0X. Then, link that billing account to your project, e.g. 

`gcloud beta billing projects link cloud-variations-fs2021 --billing-account 0X0X0X-0X0X0X-0X0X0X`

Now you should be able to enable the cloud build API without running into errors: 

`gcloud services enable cloudbuild.googleapis.com`

With that, we are all set up and ready to go! Finally, we can run something on the the cloud. I encourage you to poke around the [cloud console dashboard](https://console.cloud.google.com/) and find the services you have already enabled and the project you have created. 

## Variation: Functions-as-a-Service 

We begin with the most high-level, abstract, hands-of approach to running our service: Functions, also sometime slightly incorrectly called "Serverless" or "Lambda". We need to provide Google Cloud Functions only with the code of a function and some basic options, and it will run it for us. 

Enable the cloud functions service on your project:

`gcloud services enable cloudfunctions.googleapis.com`

And now we will deploy a single _function_ from our application, the function `index()` found in the file `api/hello_cloud.py`: 

`gcloud functions deploy hello_cloud --runtime python38 --trigger-http --allow-unauthenticated --max-instances 2 --set-build-env-vars=GOOGLE_FUNCTION_SOURCE=api/hello_cloud.py --region=europe-west3`

This reads as: "Hey Google, deploy a Cloud Function for me called hello_cloud, which is both the name of the function that I've defined as well as the name that you'll use to identify the function. That function in the file api/hello_cloud.py. It should use the Python 3.8 runtime, anyone can access it on the internet without authentication, but only allow 2 instance to not run up my bill. Run the function if there is an HTTP request to the URL". 

You should be able to now see your function running live on the internet now, at the url listed in the output of the command or in the console. It has a format like https://{Region}-{ProjectID}.cloudfunctions.net/{function-name}, in my case https://europe-west3-cloud-variations-fs2021.cloudfunctions.net/hello_cloud. 

And there we have it: you can run a function on Google's Cloud without any concern for how to manage the server, just setting a few basic parameters.  

## Variation: Platform-as-a-Service

In this variation, we will use Google's Platform-as-Service offering, Google App Engine. Our entire Flask app will be built, run, and managed by Google Cloud with minimal configuration on our side. We specify the Python runtime, the size of the target server, and some routing rules, and Google Cloud handles the rest (including things like installing the packages listed in our `requirements.txt` file). 

Create an instance of an App, either from the CLI or through the dashboard. Be sure to get the projectId from the previous step: 

`gcloud app create --project=cloud-variations-fs2021 --region=europe-west3`

again, you can check it's status at the CLI or the dashboard: 

`gcloud app describe --project=cloud-variations-fs2021`

Note that at this stage, you have created an "application", but there is nothing being served yet. You will automatically have a custom URL for this project, which has the format PROJECT_ID.appspot.com, in my case https://cloud-variations-fs2021.appspot.com. If you navigate to your own URL, you will get a 404: there is nothing being served there yet. 

Now, we can deploy our app! The application configuration is entirely described in a single file, called `app-engine.yaml`. To deploy, we will tell app engine to use the configuration we have detailed in that file: 

`gcloud app deploy app-engine.yaml`

And there we have it: your app is deployed! Look at that yaml file and see what we need to describe the infrastructure: a runtime (Python version), an instance class (the size of the VM we will us, in this case, [F2](https://cloud.google.com/appengine/docs/standard), with a half GB of RAM), and some routing rules - similar to what we would need to define for a web server application like nginx, Caddy, or Apache. This tells app engine to respond to any request with the response of our application (as opposed to a redirect request, serving a static file, or an error, for instance. In this variation, we are able to specify resources (like the compute instance size), but still are not concerned with things like the underlying operating system. 

## Intermission: Containerize the Application

In order to prepare for the next variations of running our app, we will first build the container ourselves (using Docker) and push it to Google Cloud's container registry, allowing us to use that container on various managed services. 

### Build and Run the container locally 

To start, build a Docker image, based on the Dockerfile provided for you in this repository: 

`docker build --tag hello-cloud .`

and run it locally: 

`docker run --publish 5000:5000 hello-cloud`

At this point, you should be able to again make a request locally, via `curl localhost:5000` or by going to the browser. 

At this stage it is worth it to have a look at our Dockerfile, even if you aren't very familiar with Docker. We first define which base image we are using - in this case, an imagine provided by the Python Organization built on top of Debian 10 (codename buster). This gives us an operating system and everything we need to run Python 3.8. Then, we copy files from our local development environment into Docker's working area, and after that, we do the same thing as we do locally without Docker: install packages, set an environment variable, and run the app. Just this time, it is running as a Docker container on our own computer. 

### Push the Image to Google Cloud 

In this step, we will push our image to Google Artifact Registry -- a dedicated type of storage which we will configure to store Docker images (similar to Docker Hub, if you are familiar with it). 

Start by Enabling the Artifact Registry:

`gcloud services enable artifactregistry.googleapis.com`

Now, we'll push your Docker Image to Google's Artifact Repository. To do this, we will use the tool provided by gCloud to authorize yourself on Docker on your machine giving you permissions to push to your Google Cloud Artifact Registry: 

`gcloud auth configure-docker europe-west3-docker.pkg.dev`

Next, create a repository in the Artifact Registry for you to store your image in: 

`gcloud artifacts repositories create hello-cloud --repository-format=docker --location=europe-west3`

Note that the format "Docker" specifies that what type of artifact the repository should expect, a Docker Image. 

Now you can tag your local image to push to a specific location, telling Docker where you will push it: to the repository you just created. You should replace `cloud-variations-fs2021` with your project name: 

`docker tag hello-cloud:latest europe-west3-docker.pkg.dev/cloud-variations-fs2021/hello-cloud/hello-cloud:latest`

And finally, push it to Google's Artifact Repository: 

`docker push europe-west3-docker.pkg.dev/cloud-variations-fs2021/hello-cloud/hello-cloud:latest`

Phew. We've built a Docker image locally and pushed it to Google Cloud. You can see the fruits of your labors (and browse the directory structure) over on the dashboard at https://console.cloud.google.com/gcr/images/{your-project-name}. 

## Variation: Serverless Container Management 

Sometimes cloud services feels like they were generated by putting random buzzwords together, and Cloud Run is no exception. In this variation, we will run our custom-built container on a platform managed by our cloud provider. We can will use a service which conforms to the [knative](https://knative.dev/) standard, giving us more flexibility than a Functions-as-a-Service offering but without the need to provision an entire Kubernetes cluster. This is considered "serverless" because you don't need to manage any servers, even if it is not a "Function-as-a-Service" offering. 

First, enable the Google Cloud Run API: 

`gcloud services enable run.googleapis.com`

Then, we will create and deploy our new _service_, which will tell Cloud Run to run between 2 and 5 instances of our container based on the image we have built and pushed already. 

`gcloud run deploy hello-cloud-run --image=europe-west3-docker.pkg.dev/cloud-variations-fs2021/hello-cloud/hello-cloud:latest --port=5000 --region=europe-west3 --allow-unauthenticated --min-instances=2 --max-instances=5`

This command should feel a bit like the one we used for the FaaS offering at the start, but with a bit more control. 

Go over to the [dashboard](https://console.cloud.google.com/run/) and poke around a bit to see what you have running there.

Once you are done, remember to cleanup by deleting the service -- otherwise it could suck up all your credits: 

`gcloud run services delete hello-cloud-run`


## Variation: Managed Kubernetes Cluster

We've already run some high-level managed versions of our API, and now we are going to take things a bit more into our own hands, running our service in Kubernetes. We will use Google Kubernetes Engine, Google's managed Kubernetes cluster, so we only have to _use_ Kubernetes, not host it ourselves. 

! Note that this may get a little bit tricky on your local machine. If you have trouble with further installation and configuration, you access the [gCloud Shell](https://cloud.google.com/shell) through your browser, giving you a command line interface allowing you to interact with your project. 

### Additional Software 

- [Install kubectl](https://kubernetes.io/docs/tasks/tools/), the command line interface for interacting with Kubernetes itself. 


### Run our container using Kubernetes
Now it's time to run our Docker container on our own Kubernetes Cluster. 

Enable the Google Kubernetes Engine API: 

`gcloud services enable container.googleapis.com`

Now we can create a Kubernetes cluster: 

`gcloud container clusters create hello-cloud-cluster --num-nodes=1`

You may crash out with an error that says _Please specify location_. Let's set it to Frankfurt: 

`gcloud config set compute/zone europe-west3-b`

and try again to create the cluster with the above command. Now you should get a few yellow warnings, but no red errors. 

And now we are ready to interact with our Kubernetes cluster!

Use the gcloud-provided tool to configure your kubectl on your machine for interacting with your cluster on gcloud: 

`gcloud container clusters get-credentials hello-cloud-cluster`

Now, try to find out a bit about your cluster using `kubectl describe`, for example `kubectl describe nodes`, which will show a whole lot of hard to understand information about your kubernetes cluster. 

Create a _deployment_ based on our Docker image, effectively declaring that we want our Docker image to run in Kubernetes:

`kubectl create deployment hello-cloud-server --image=europe-west3-docker.pkg.dev/cloud-variations-fs2021/hello-cloud/hello-cloud:latest`

Once you have run this, it is running already, but we have to expose it on the network to see it, mapping our local port 5000 to the public port 80 for HTTP: 

`kubectl expose deployment hello-cloud-server --type LoadBalancer --port 80 --target-port 5000`

You can now find the public (external) IP address of your application using: 

`kubectl get service hello-cloud-server`

In my case, I see 34.107.66.217, which I can now access in the browser at http://34.107.66.217 or locally via curl again, `curl 34.107.66.217`. Note that by provisioning your own kubernetes cluster, you do not have an automatically assigned domain -- and therefore also no encryption on the connection.  

That's "it"! Your very own Docker container running on your very own Kubernetes Cluster. 

Before you leave: shut off your Kube cluster, otherwise you'll run out of money, shutting off the load balancer and then your cluster: 

`kubectl delete service hello-cloud-server`

`gcloud container clusters delete hello-cloud-cluster`


## Cleanup! 

That's "it". Before leaving, cleanup your account, otherwise it will suck all of your credits dry. We've all been there. If you are completely done, you can "shut down" the project entirely, and everything will be deleted soon. Alternatively, you can keep the FaaS or PaaS service running for a few cents or euros a month. It is highly recommendable to shut off the kubernetes (GKE) instances once you are finished with the tutorial. They get pricey quickly. 

## Make This Your Own

Now that you have run through four variations, you are encouraged to make this your own. Here are a few ideas for continuing to explore cloud models for operations: 

- Change what the app itself does. You can edit the message, or add a route. 

- Consider other ways of running this application on the cloud. For instance, use GCP's virtual machine's directly (Compute Engine) and consider hosting your application directly, running on the machine itself. What do you have to configure yourself, and what are the differences to the managed services we have used here? 

- Run through this again with a programming language of your choice, again creating a hello world application and deploying it many ways. 

- Add a second simple application. It could be a frontend which consumes this backend api (representing a standard web app setup with a frontend and a backend), a separate stand-alone server application with another route (representing a microservice-like architecture), or an internal-facing api which is not exposed on the public internet but which our existing app can call to (representing an n-tier architecture). Consider how you would deploy both of these applications, either together or separately, and configure them to have different resources and uptimes. 

- Use a managed API service, for example for translation or natural language processing on our highly sophisticated message. How does this service differ from ones which we are defining ourselves? What would it take for you to create an API like this yourself, even if you had the model accessible? 

- Add a database layer using a managed service. You can put the message we are returning into that database. What do you have to consider to connect this application to the database, with each of these methods? What database services are available, and which are appropriate for this application? 

## Troubleshooting 

Weird problems can occur. Here are a few we've seen so far, and possibly ways to remedy them. 

### Too Many Versions 
If you see an error like this, you need to delete old (unused) versions of your app. 

> ERROR: (gcloud.app.deploy) INVALID_ARGUMENT: Your app may not have more than 15 versions. Please delete one of the existing versions before trying to create a new version

You can do this by clicking through the gCloud Console and manually deleting them. Or, you can use a fancy command like this: 

``gcloud app versions delete `gcloud app versions list --filter="traffic_split=0" --format="table(version.id)"` ``

This monstrous command is really two in one. The inner command, within backticks (`` ` ``), is executed first. This will list all versions of the app which have no traffic flowing to them (hence the `--filter`), but will only list the versions id and no other information (hence the `--format`). This list will be parsed, line by line, by the outer command, which will try to delete those app versions. 





