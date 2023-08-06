


# Quick start With SDK

> Welcome to neurodeploy SDK

> The SDK is under directory neurodeploy

  1. Install python package:

   `pip install neurodeploy`

  2. Import the library:

   `import neurodeploy as nd`

  2. Auth to API:

   - By getting your JWT token

   `nd.user.login(your_username,your_password)`

  3. Create and upload your model:

   - Model push

   `nd.model.push(your_model_name,your_model_file_path,libray_forml,file_extention)`

  4. Predict your model:

   `nd.model.predict(your_model_name,your_data)`


# Quick start With neuro

> Welcome to neurodeploy neuro

  1. Pull the repo:

   `git pull REPO_URL`

  2. Auth to API:
   - By getting your JWT token
  
   `python neuro.py  user login  --username YOUR_USER_NAME  --password YOUR_PASSWORD`
  
  3. Create and upload your model:
   - Model push
  
   `python neuro.py model push --name YOUR_MODEL_NAME --file-path /YOUR_PATH/YOUR_MODEL_FILE_NAME`
  
  4. Predict your model:
  
   `python neuro.py model predict --name YOUR_MODEL_NAME  --data '{"payload": [[1, 2, 3, 4, 5]]}'`
  
---
# neuro usage
---
  ### neuro help
 `python neuro.py  --help`

 `python neuro.py  model --help`

  ### neuro usage
   #### Authentificate neuro:

  There si differents way to connect your neuro to neurodeploy:

    1.By JWT token                 : For simple temporary usage

    2.By access_key and secret_key : For ci/cd pipeline

    3.By neuro config                : For user admin computer

  1. By JWT token:

  - Excute neuro cmd login to get your jwt token  with you username password for your account created by the UI

    `python neuro.py  user login  --username YOUR_USER_NAME  --password YOUR_PASSWORD` 

         `jwt token is stored locally and expire each 24 hours need to login a second time to renew your token
`
  2. By access_key and secret_key

  - Get you acces key secret key from the ui

  - Set envirement variables:

    `export ND_SECRET_KEY="xxxxxxxxxxx"`   

    `export ND_ACCESS_KEY="xxxxxxxxxxx"`

         `credentials ares stored locally in your machine no expiration`

  3. By neuro config

  - Execute neuro conf file with you username password for your account created by the UI

    `python neuro.py  configure update`

         `Save neuro config`

         `Enter your username: your_user_name`

         `Enter your password: xxxx`

         `Repeat for confirmation: xxx`


   #### Using neuro:
   ##### Managing model 

- Delete model: 

 `python neuro.py  model delete  --name YOUR_MODEL_NAME`
- List models:

 `python neuro.py  model list`
- Get model:

 `python neuro.py  model get  --name YOUR_MODEL_NAME`

   ##### Managing credentials
- Create credential

 `python neuro.py  credentials create --name CREDENTIAL_NAME  --description YOUR_DESC`
- Delete credential

 `python neuro.py  credentials delete  --name CREDENTIAL_NAME`
- List credentials

 `python neuro.py  credentials list`

   ##### Managing apikeys
 python neuro.py apikeys create --description API_KEY_DESCRIPTION`
   {'status_code': 200, 'api_key': 'efee5b0a-86cf-4f02-86b0-2790261af541'}

 `python neuro.py apikeys list`

 `python neuro.py apikeys delete --apikey API_KEY`
  {'status_code': 200, 'message': "Successfully deleted API key 'efee5b0a-86cf-4f02-86b0-2790261af541'."}



---
# Generate doc
  - Execute bash script to build doc: doc.sh

   `sh doc.sh`

     You can find pdf under doc/build

---
# Venv and requirement
  - To activate venv

   `source venv/bin/activate`

  - Install requirement: 

   `pip install -r  requirements.txt`
---
# Run tests
  - Execute bash script for tests

  `sh test.sh`

---
# Build package
  - Execute bash script for build

  `sh build.sh`
---
# Build neuro Binary
  - Execute bash script for build binary

  `sh bin.sh `

    You can find bin file here dist/neuro
---
# Env vars
| ENV VAR Name | Description | Values | 
|--------------|:-----------:|:------:|
|  ND_SECRET_KEY         |    User acces key value to auth to api |xxxx
|  ND_ACCESS_KEY         |    User secret key value to auth to api|xxxx
|  ND_DEFAULT_LIB        |    Default ml library used|tensorflow/sklearn
|  ND_DEFAULT_FILETYPE   |    Default ml model file extention|H5/pickel
|  ND_DEFAULT_CONFDIR    |    Default neuro configuration path to store username / token / credentials|~.nd
|  ND_DEFAULT_ENDPOINT   |    Default neurodeploy endpoint domain name|.neurodeploy.com


---


