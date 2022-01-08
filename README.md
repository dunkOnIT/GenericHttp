Hi all - asking for a bit of a roast of a class I've written that I'm quite unsure of 😄 I'll give context, specific questions, and a link to a github repo where I have it stored (probably too much code for a code block in here). Primarily looking for feedback on the design/structure of the class. 

Context:
* I am building an API that will both send (using requests) and receive (using Flask) HTTP requests.
* I want to be able to log those requests by calling log_http(some_object), but the names of methods/properties for the different types of HTTP object I'm working with are all different, which was leading to a lot of branching logic in the log_http() function
* What I want to see when I log an object is literally just the HTTP request that was sent/received
* All the branching logic seemed like bad design, so my solution is to create a class called GenericHttp, which takes as an input any of the HTTP objects I'm currently working with, and creates a set of generic properties that are common to all of them, which I can then call methods on
* I'm looking for critique on GenericHttp, so I've isolated just the class and some helper functions I wrote to assist it during __init__

Questions:
Any comments/critiques are welcome - I don't know what I don't know. But just asking for generic comments seemed inappropriate given the scale of the question, so here are some of the specific things I'm curious about:

1) Are there simpler methods I'm not aware of for logging/printing different HTTP requests? 

2) Is it the right call to keep helper functions (get_params_from_url etc) separate from the GenericHttp class? I think it is, because they could be called by any number of other classes/functions, and I don't want them to also need to instantiate a GenericHttp object. 

3) My get methods (get_basic_info etc) are all called during __init__ to extract properties from the http_object I am processing. It might be the case that get methods are usually intended for allowing access to properties etc - is this a bad naming convention? If so, what would be recommended instead? 

4) self.basic_info is basically just a hodge-podge dictionary of general characteristics about an HTTP request that I'm interested in. Better way to name this/structure the data I am looking at? (Having them be individual properties seemed bloated, but perhaps it is more intuitive than having an opaque basic_info property). 
5) My get methods all follow the same general logic of having if statements that determine what type of http_object it has been given, and then they execute the object-specific methods/properties on those objects. It leads to a lot of similar-looking code which smells weird to me - is there a better way to design this/solve this problem? 

6) An http_object can either be a request or a response. They're structurally similar, but have minor variations (requests don't have response codes, responses don't have methods). Should I do more to differentiate between them/handle the 2 different types? That would seem to go against my principle of trying to make just a single, abstracted object - but perhaps it leads to shoehorning sketchy solutions. 

6.1) An example of the above - basic_info has some properties which will always be None. Am I overusing NoneType here? To me it seemed like the cleanest/simplest way of dealing with the response vs request issue, but I might be overusing/mis-using None. 

7) self.log_object: My primary object with this function is to put a nice, readable, clear HTTP request into the logs. This means the method is quite manual, going through individual properties, explicitly having different logging separators etc. I'm not sure if this is just how the sausage is made, or if there's a better/more elegant way to design functions like this.
