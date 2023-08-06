This is a library that makes automating events in ADOFAI levels more convenient.

List of Functions:

getFileString(filename : str): returns the ADOFAI file as a string. Many functions in this library depend on this string.

getAngles(filestring : str): takes a file string and returns the list of angles.

setAngles(angles : list, filestring : str): writes the new angles to the file string and returns the file string.

There is also one function for each event. It is recommended to use keyword arguments while calling these functions.
The arguments for these functions are the same as the fields that are present in the ingame editor.
Fields with string values (eg. ease="In Out Bounce") must have their spaces removed (ease="InOutBounce").
These functions return the event data as a string which can be added with addEvent().

Note that addDecoration() works the same as other event functions. 

addEvent(event : str, filestring : str): adds events to the file string and returns the file string. This function is also compatible with addDecoration().

writeToFile(filestring : str, filename : str): writes the modified file string to the file. 
