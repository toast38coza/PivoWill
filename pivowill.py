import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template
import requests
import json


class PivotalPlugin(WillPlugin):


    @respond_to("^show me pivotal projects")
    def show_projects(self, message):
        
        key = self._get_user_key(message, "pivotal_token")
        token = self.load(key,False)
        
        url = self._get_url("/projects")
        response = requests.get(url, headers={"X-TrackerToken":token})
        parsed_response = json.loads(response.content)

        if response.status_code == 200:
            context = {
                    "projects": parsed_response,
                    "account_id": account_id,
                    }
            self.say(rendered_template("pivotalprojects.html", context), message=message, html=True)            
            
        else:
            self.reply(message, "Uh-oh. There was an error: {0}" . format (parsed_response.get("error") ))

    @respond_to("set my pivotal auth key to (?P<auth_token>.*)")
    def set_auth_token_for_user(self, message, auth_token):
    	key = self._get_user_key(message, "pivotal_token")
    	self.save(key, auth_token)
        self.reply(message, "I've saved your auth token.")

    @respond_to("what's default project again?")
    def say_default_project(self, message):
        
        key = self._get_user_key(message, "pivotal_project")
        project = self.load(key, False)

        if project:
            self.say("Your default project is {0}" . format(project))
        else:
            self.say("You don't have a default project. Set one by telling me: 'set my default pivotal project to <project_id>' ")

    @respond_to("set my default pivotal project to (?P<project_id>.*)")
    def set_default_project(self, message, project_id):
    	key = self._get_user_key(message, "pivotal_project")
    	self.save(key, project_id)

        self.reply(message, "{0} is now your default project" . format(project_id))


    @respond_to("state of current iteration")
    def current_iteration_state(self, message):
        ## todo: the instructions should be generalized ..
        
        key = self._get_user_key(message, "pivotal_token")
        token = self.load(key,False)
        project_id = self.load( self._get_user_key(message, "pivotal_project"), False)

        if token: 
            if project_id:
                self.say("asking pivotal about the current iteration ..", message = message)
                ## this can also be reused
                url = self._get_url( "/projects/{0}/iterations" . format (project_id) )
                self.say(url, message=message)
                headers = {'X-TrackerToken': token}
                params =  {'scope': 'current'}

                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    
                    current_iteration = response.json()[0]
                    iteration_title = "Iteration {0}: {1} - {2}" . format (current_iteration.get("number"), current_iteration.get("start"), current_iteration.get("finish"))
                    self.say(iteration_title , message=message)
                    story_breakdown = [ story.get("current_state") for story in current_iteration.get("stories")]
                    story_states = ["unstarted", "started", "finished", "delivered"]

                    for state in story_states:
                        count = story_breakdown.count(state)
                        self.say("{0} stories: {1}" .format (state, count) , message=message)
                else:
                    self.say("I got an error from Pivotal {0}: {1}" . format (response.status_code, response.content) )
            else:
                self.say("You need to specify which project you're working on", message=message)
                self.say("To see all the projects, tell me: 'show me pivotal projects' ", message=message)
                self.say("To se your project, tell me: 'set my default pivotal project to ..' ", message=message)
        else: 
            self.say("You need to set you auth token. Tell me: 'set my pivotal auth key to <your token here>'", message=message)
            self.say("to get your token: In PivotalTracker, click your name -> Profile .. it's at the bottom of the page 'API TOKEN' ", message=message)

    @respond_to("show my work")
    def show_work(self, message):
    	key = self._get_user_key(message, "pivotal_token")
    	token = self.load(key,False)
        project_id = self._get_user_key("pivotal_project", False)

        if token: 
            
            if project_id:
                self.say("Still not sure how to do this .. check back in a few days ..", message=message)

            else:
                self.say("You need to specify which project you're working on", message=message)
                self.say("To see all the projects, tell me: 'show me pivotal projects' ", message=message)
                self.say("To se your project, tell me: 'set my default pivotal project to ..' ", message=message)
    	else: 
    		self.say("You need to set you auth token. Tell me: 'set my pivotal auth key to <your token here>'", message=message)
    		self.say("to get your token: In PivotalTracker, click your name -> Profile .. it's at the bottom of the page 'API TOKEN' ", message=message)

    def _get_user_key(self,message, key):

    	user = message.sender.nick
    	key = "{0}_{1}" . format (user, key)
    	return key

    def _get_url(self,path):

    	base_url = "https://www.pivotaltracker.com/services/v5"
    	return "{0}{1}" . format (base_url, path)
