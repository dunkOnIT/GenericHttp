import requests
import werkzeug
import logging
import datetime
import inspect
import json

logger = logging.getLogger(__name__)

# GenericHttp class

class GenericHttp:
    """
    A class which takes an HTTP object as input and abstracts it to allow a generic set of methods to run against it.

    Supported objects:
        * flask.Request
        * requests.PreparedRequest
        * requests.Response

    ==============

    Explanation by example: I want to log the HTTP calls from a flask.Request object, a requests.Request object and a 
    requests.Response object. All of these will result in similar structure when logged and have similar abstract attributes
    (headers, parameters, url, etc), but have different methods for accessing these properties. 

    This class allows any of those 3 objects to be passed in, and creates a uniform set of methods for working with their properties.
    """
    
    def __init__(self, http_object):
        """
        Initialise the object with the following parameters:
            * object_type = the type of the object, for calling the correct methods to extract its properties
            * has_json = boolean to represent whether or not the body contains JSON
            * basic_info = Dictionary of fundamental elements of the object (method, url, whether it is a resopnse, etc)
            * parameters = Dict of any paramters included in the URL of the object
            * headers = Dictionary of headers from the object
            * body = The body of the object, stored in whatever format is returned by the object 
        """
        self.object_type = type(http_object)
        self.has_json = False

        self.basic_info = self.get_basic_info(http_object)
        self.parameters = self.get_parameters(http_object)
        self.headers = self.get_headers(http_object)
        self.body = self.get_body(http_object)
        

    def get_basic_info(self, http_object):
        """
        Init method - takes an http_object as input and returns a dictionary of the basic information relating to that object. 
        """

        basic_info = {
            "request_type":"",
            "request_url":"",
            "is_response":"", 
            "response_code":"",
            "response_reason":""
        }

        if(isinstance(http_object, requests.Response)):
            basic_info["request_type"] = None
            basic_info["request_url"] = http_object.url
            basic_info["is_response"] = True
            basic_info["response_code"] = http_object.status_code
            basic_info["response_reason"] = http_object.reason

        elif(isinstance(http_object, requests.PreparedRequest)):
            basic_info["request_type"] = http_object.method
            basic_info["request_url"] = http_object.url
            basic_info["is_response"] = False
            basic_info["response_code"] = None
            basic_info["response_reason"] = None

        elif(isinstance(http_object, werkzeug.local.LocalProxy)):
            basic_info["request_type"] = http_object.method
            basic_info["request_url"] = http_object.full_path
            basic_info["is_response"] = False
            basic_info["response_code"] = None
            basic_info["response_reason"] = None

        return basic_info

    def get_parameters(self, http_object):
        """
        Init method - takes an http_object as input and returns a dictionary of the parameters relating to that object. 
        """

        if(isinstance(http_object, requests.Response)):
            parameters = get_params_from_url(http_object.url)
            pass

        elif(isinstance(http_object, requests.PreparedRequest)):
            parameters = get_params_from_url(http_object.url)
            pass

        elif(isinstance(http_object, werkzeug.local.LocalProxy)):
            parameters = http_object.args
            pass

        return parameters
        
    def get_headers(self, http_object):
        """
        Init method - takes an http_object as input and returns a dictionary of the headers relating to that object. 

        All supported objects currently use the same property name, but this method was created to easily add more 
        supported objects in the future, which may use other property names.
        """

        return http_object.headers
        
    def get_body(self, http_object):
        """
        Init method - takes an http_object as input and returns the body of the object. Does not expect a particular type 
        of body, but will set the self.has_json property. 
        """
        self.has_json = check_header_for_json(self.headers)
        

        if(isinstance(http_object, requests.Response)):
            if(self.has_json):
                return http_object.json()
            else: 
                return http_object.text

        elif(isinstance(http_object, requests.PreparedRequest)):
            return http_object.body

        elif(isinstance(http_object, werkzeug.local.LocalProxy)):
            if(self.has_json):
                return http_object.get_json()
            else: 
                return http_object.get_data()

        return

    def log_object(self):
        """
        Logs a GenericHttp object at the INFO level. JSON received in a response object will be dumped to a separate file for ease of parsing. 
        
        Logging occurs in the following sections:
            * Basic info
            * Parameters
            * Headers
            * Body

        """

        # Log uppercase of the type of HTTP object we are processing
        logger.info("\n\n=== LOGGING {} ===".format(str(self.object_type).upper()))

        # Log basic info
        logger.info("\n\n* Basic info *")

        if(self.basic_info["is_response"]): # log status code and reason if dealing with a Response object
            logger.info("Status code - " + str(self.basic_info["response_code"])) 
            logger.info("Reason -  " + str(self.basic_info["response_reason"]))
        else: # if it's a request, note the request type
            logger.info("Request type - " + str(self.basic_info["request_type"]))
        logger.info("URL - " + self.basic_info["request_url"]) # For all objects, log the target url

        # Log parameters

        if not (self.parameters == None):
            logger.info("\n\n* Parameters *")
            log_dict(self.parameters)

        # Log headers 

        logger.info("\n\n* Headers *")
        log_dict(self.headers)

        # Log content

        logger.info("\n\n* Content *")

        if(self.has_json and self.basic_info["is_response"]):
            # If the object is a response and contains json, save the json to its own file

            # Determine datetime_string
            datetime_string = datetime.now().strftime("%Y-%m-%d %H.%M.%S") 

            # Determine caller_function
            if(inspect.stack()[1].function == "process_request"):
                caller_function = inspect.stack()[2].function 
            else:
                caller_function = inspect.stack()[1].function 

            # Build filename
            filename = datetime_string + "-" + caller_function + ".json"
            full_file_string = "request_logs/" + filename

            # Write json to file
            with open(full_file_string, "w+") as outfile:
                json.dump(self.body, outfile, indent=4)

            logger.info("JSON dumped to " + full_file_string)
        else: 
            logger.info(self.body)


# Helper functions

def get_params_from_url(url):
    logger.info("Retrieving params from URL: " + url)
    param_start = url.find("?")

    if (param_start == -1): 
        return None
    
    param_dict = {}
    param_string = url[param_start+1:]
    param_list = param_string.split("&")

    for param in param_list:
        param_split = param.find("=")
        param_dict[param[:param_split]] = param[param_split+1:]

    return param_dict

def check_header_for_json(headers):
    if ("content-type" in headers.keys() and 
    "application/json" in headers["content-type"]):
        return True
    else:
        return False

def log_dict(dict):
    for key in dict.keys():
        logger.info(key + " - " + dict[key])  