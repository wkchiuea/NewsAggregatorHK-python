## Jupyter Notebook Setup
1. build docker image  
   ` docker image build -t web-scrap-ipynb . `
2. run docker container  
   ` docker container run -d -p 8888:8888 --name web-scrap web-scrap-ipynb `
3. may mount local directory to directory inside container, replace "$PWD" with your directory   
   ` docker container run -d -p 8888:8888 -v "$PWD":/usr/src/app web-scrap-ipynb `
  
## Access Notebook
1. if needed, use `docker container logs web-scrap` to find notebook access token
2. go to "http://localhost:8888" to access notebook
  
## Stop Container
1. `docker container rm -vf web-scrap`