# Introduction 
This project implements a REST API in Python using Flask. It's purpose is to enable data stored as Delta Tables
to be made available via a REST endpoint. The requirements for this project will come from Beaver Labs.

# Getting Started
The code here is intended to be used to provision an Azure Web app.

## 1. Installation process
* First deploy an Azure Web app.
* Upon creation the app should be configured for `Code` not `Container` &
`Linux` not `Windows`
* `Python 3.8 or 3.9` should be selected as the language.
* The `Startup Command` for the Web app should be configured as `gunicorn --bind=0.0.0.0 --workers=4 startup:app`
* Git clone the repository
* Select `Deploy` from VS Code's Azure extension.

## 2. Software dependencies
All dependencies for this project are captured in the file `requirements.txt`. Briefly these dependencies include
Azure python libraries, e.g. for accessing Azure storage accounts and the _delta-lake-reader_ for Azure.
See [delta-lake-reader 0.2.10](https://pypi.org/project/delta-lake-reader/)

## 3. Development and Test
This project implements a Flask based REST endpoint in Python. Visual Studio Code is recommended as the IDE. 
Currently there are no units tests implemented. It is recommended that you use the VS Code Thunder Client extension or
Postman to manually test the endpoints. Unit tests will be added appropriately as more code and complexity is added.
To run the Flask server in development mode, git clone the repository. Then create a Python virtual environment and activate it:
```
    python -m venv .venv
    source .venv/Scripts/activate
```

Install the dependencies:
```
    pip install -r requirements.txt
```

* You may hit the following error: `ERROR: Could not install packages due to an OSError: [WinError 5] Access is denied: 'C:\\Users\\SarbjitSarkaria\\AppData\\Local\\Temp\\pip-uninstall-lt6qik7g\\pip.exe'
Check the permission`. In this case, just run `pip install adlfs` and then try again.
_TODO:_ This needs to be fixed. 

Create a `.env` file and add values for the following variables. Ensure that you the environment you are running in has access
to the storage account. E.g. when running locally on your laptop, you may have to add your local IP to the storage account's
firewall setting. When running in a Web app, you may need to configure the Web app so that it is connected to the same
virtual network used by the storage account:
```
API_KEY='<a long string used to protect access to API>'
ACCOUNT_NAME='<storage account name>'
STORAGE_ACCOUNT_CONNECTION_STRING='<connection string>'
FLASK_APP='startup.py'
```

To run the server, enter the following commands in a BASH shell and follow the instructions. Note that you can also start the
server from VS Code's "Run and Debug" icon/menu. Just select _Python:Flask_ from the pull-down menu:
```
    export FLASK_APP=startup.py
    flask run
```

# Build and Provision
There is no need to build the project. To provision your Web app in the Azure cloud, invoke the upload option in VS Code's Azure 
extension and select your target Web app resource. Upon successfull completion, VS Code will ask if you would like to upload settings.
Select `Yes` and this will copy over the environment variables in the `.env` file over to the Web app. Note that you may wish
to replace the `Storage_Account_Connection_String` with a reference to a secret in a key vault. E.g.:
`@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/mysecret/)` and secure access to key vault using managed identity

The project also provides a Dockerfile. This gives you the option of deploying the server as a container. In this case the
following differences should be observed:

1. When creating the Web app in Azure, select the `Container` option, not `Code`.
2. Create a Container registry in Azure. (Dockerhub can be used but not recommended for security reasons)
3. Make sure VS Code's Docker extension is installed and then right click on the file called `Dockerfile` and select 
`Build Image in Azure`
4. You do not need a `Startup Command`

__Note that it is important that Flask is only used in the development environment__. In production, [Gunicorn](https://gunicorn.org/)
is recommended. If Windows is your development environment, you will find that `pip install gunicorn` will install but not run
as some dependencies are not supported in Windows, even in a BASH shell.

# Questions
Please direct any questions to sarbjit@procogia.com

# FAQ
1. Q: Why is there a Dockerfile included? A: The app was originally deployed as a container. This is now optional.