import json
import requests
import webbrowser

def title(id):
    try:
        data = json.loads(requests.get(f"https://api.scratch.mit.edu/project/{id}/").text)
        return (data["title"])
    except Exception:
        return "There is a error. Maybe the project is not shared or it does not exists."

def description(id):
    try:
        data = json.loads(requests.get(f"https://api.scratch.mit.edu/project/{id}/").text)
        return (data["description"])
    except Exception:
        return "There is a error. Maybe the project is not shared or it does not exists."
    
def views(id):
    try:
        data = jsondata = json.loads(requests.get(f"https://api.scratch.mit.edu/project/{id}/").text)
        return (data["stats"]['views'])
    except Exception:
        return "There is a error. Maybe the project is not shared or it does not exists."
    
def loves(id):
    try:
        data = jsondata = json.loads(requests.get(f"https://api.scratch.mit.edu/project/{id}/").text)
        return (data["stats"]['loves'])
    except Exception:
        return "There is a error. Maybe the project is not shared or it does not exists."
    
def favorites(id):
    try:
        data = jsondata = json.loads(requests.get(f"https://api.scratch.mit.edu/project/{id}/").text)
        return (data['stats']['favorites'])
    except Exception:
        return "There is a error. Maybe the project is not shared or it does not exists."
    
def remixes(id):
    try:
        data = jsondata = json.loads(requests.get(f"https://api.scratch.mit.edu/project/{id}/").text)
        return (data["stats"]['remixes'])
    except Exception:
        return "There is a error. Maybe the project is not shared or it does not exists."    
    
def exists(id):
    try:
        data = jsondata = json.loads(requests.get(f"https://api.scratch.mit.edu/project/{id}/").text)
        if data['code'] == 'NotFound':
            return "Project is not shared or it does not exists."
    except Exception:
            return 'Project exists'
    
def open(id):
    try:
        webbrowser.open_new('https://scratch.mit.edu/projects/{id}/')
    except Exception:
        return "There is a bad error. Please report to https://github.com/Tony14261/tscratchapiget/issues"