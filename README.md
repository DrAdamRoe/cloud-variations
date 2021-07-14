
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

Once you are running, you should be able to see a JSON response in the browser by navigating to http://localhost:5000 or by using cURL to GET a response, e.g. `curl localhost:5000`


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

## Variation: Platform-as-a-Service (Google App Engine)


Create an instance of an App, either from the CLI or through the dashboard. Be sure to get the projectId from the previous step: 

`gcloud app create --project=cloud-variations-fs20201 --region=europe-west3`

again, you can check it's status at the CLI or the dashboard: 

`gcloud app describe --project=cloud-variations-fs20201`

Note that at this stage, you have created an application, but there is nothing being served yet. You will automatically have a custom URL for this project, which has the format PROJECT_ID.appspot.com, in my case https://cloud-variations-fs20201.appspot.com. If you navigate to your own URL, you will get a 404: there is nothing being served there yet. 

Now, we can deploy our app! The application configuration is entirely described in a single file, called `app-engine.yaml`. To deploy, we will tell app engine to use the configuration we have detailed in that file: 

`gcloud app deploy app-engine.yaml`

And there we have it: your app is deployed! Look at that yaml file and see what we need to describe the infrastructure: a runtime (python version), an instance class (the size of the VM we will us, in this case, [F2](https://cloud.google.com/appengine/docs/standard), with a half GB of RAM), and some routing rules - similar to what we would need to define for a web server application like nginx, Caddy, or Apache. This tells app engine to respond to any request with the response of our application (as opposed to a redirect request, serving a static file, or an error, for instance.

## Variation: Functions-as-a-Service (Google Cloud Functions)

Enable the cloud functions service on your project:

`gcloud services enable cloudfunctions.googleapis.com`

And now we will deploy a single _function_ from our application, the function index(): 

`gcloud functions deploy hello_cloud --runtime python38 --trigger-http --allow-unauthenticated --max-instances 2 --set-build-env-vars=GOOGLE_FUNCTION_SOURCE=api/hello_cloud.py`

This reads as: "Hey Google, deploy a Cloud Function for me called hello_cloud, which is both the name of the function that I've defined as well as the name that you'll use to identify the function. That function in the file api/hello_cloud.py. It should use the Python 3.8 runtime, anyone can access it on the internet without authentication, but only allow 2 instance to not run up my bill. Run the function if there is an HTTP request to the URI". 

## Variation: Managed Kuberentes Cluster (GKE)
