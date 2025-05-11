# HR-LLM-Agent 🤖
This basically takes in an cv from candidate and turn their information into structure data (excel)

## To-run the code 
1- create a file inside backend called `api_key`

2- add your groq `api_key` inside a variable and call it `API_KEY` and If you do not have one go to [Groq](groq.com)
  ``` python
  API_KEY = "api"
```

3- create a python virtual environment (recommend 3.12)

``` bash 
python -m venv env
```

4- Activate the virtual environment

``` bash 
env\Scripts\activate
```

`NOTE: creating a virtual environment in python for macOS and linux is different` here is a [link](https://gist.github.com/MichaelCurrin/3a4d14ba1763b4d6a1884f56a01412b7)

5- Download all the dependency from the requirements.txt file
``` bash
pip install -r requirements.txt
```

6- And then run the main
```
python python main.py
```
