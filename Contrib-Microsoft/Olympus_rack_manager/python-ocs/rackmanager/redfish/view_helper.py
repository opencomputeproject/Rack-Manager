# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import resources
import json
import re
import ocslog
from bottle import static_file, template, request, response, HTTP_CODES, HTTPResponse, HTTPError
from controls.utils import completion_code
from collections import OrderedDict
from ocsrest.pre_check import get_pre_check_status_code, get_mode

##
# Special keys for response data.
##
manager_config_key = "RackManagerConfig"
response_status_key = "ResponseStatus"
invalid_property_value_key = "PropertyValueNotInList"
invalid_property_type_key = "PropertyValueTypeError"
read_only_property_key = "PropertyNotWriteable"
action_param_error_key = "ActionParameterError"
missing_error_key = "Missing"
param_unknown_key = "Unknown"
param_type_error_key = "WrongType"

property_error_keys = [
    invalid_property_value_key,
    invalid_property_type_key,
    read_only_property_key
]
top_level_status_keys = [
    response_status_key,
    invalid_property_value_key,
    invalid_property_type_key,
    read_only_property_key,
    action_param_error_key
]

def run_pre_check (func, *args, **kwargs):
    """
    Execute a pre-check call for the request.  This call will only return if the pre-check was
    successful.  Otherwise, an exception will be thrown.
    
    :param func: The pre-check call to execute.
    :param args: Arguments that will be passed to the pre-check call.
    :param kwargs: Arguments that will be passed to the pre-check call.
    """
    
    try:
        output = func (*args, **kwargs)
        code = get_pre_check_status_code (output)
        if (code != 200):
            result = {}
            append_response_information (result, output)
            raise_status_response (code, result)
            
    except (HTTPResponse, HTTPError):
        raise
    
    except:
        ocslog.log_exception ()
        raise HTTPError (status = 500)
    
def return_static_file_resource (name):
    """
    Serve a static file for the specified resource.
    
    :param name: The name of the resource.
    
    :return The static file information to return for the request.
    """
    
    resource = resources.find_resource (name)
    return static_file (resource.file, resource.path)

def return_redfish_resource (name, values = dict (), status = 200):
    """
    Serve a JSON object for for the specified Redfish resource.
    
    :param name: The name of the Redfish resource.
    :param values: A dictionary of values to use for fields of the object.
    :param status: The HTTP status code to return with the object.
    
    :return The JSON object response to return for the request.
    """
    
    append_rack_manager_configuration (values)
    resource = resources.find_resource (name)
    response.content_type = "application/json"
    response.status = status
    if (resource.template):
        response.body = [get_response_body (resource.template, values)]
    else:
        response.body = [get_error_body (status, values)]
    return response

def return_redfish_default_resource (name):
    """
    Serve a JSON object using the default representation of the specified Redfish resource.
    
    :param name: The name of the Redfish resource.
    
    :return The JSON object response to return to the request.
    """
    
    response.content_type = "application/json"
    response.status = 200
    response.body = [json.dumps (get_json_default_resource (name, ordered = True), indent = 4,
        separators = [",", ": "])]
    return response

def return_status_response (status, result):
    """
    Serve a JSON object that represents a generic status response.
    
    :param status: The HTTP status code to report in the response.
    :param result: The response dictionary with the status information.
    
    :return The JSON object response to return for the requset.
    """
    
    response.content_type = "application/json"
    response.status = status
    response.body = [get_error_body (status, result)]
    return response

def raise_status_response (status, result):
    """
    Raise an HTTPResponse exception with generic error status reported.  This function always
    raises an excetpion and never returns directly.
    
    :param status: The HTTP status code to report in the response.
    :param result: The response dictionary with the status information.
    """
    
    raise HTTPResponse (status = status, body = get_error_body (status, result),
        **{"Content-Type" : "application/json"})
    
def get_response_body (template_src, template_values):
    """
    Build the response body for a JSON object built from a template.
    
    :param template_src: The path to the source template for the object.
    :param template_values: A dictionary containing the values to populate into the template.
    
    :return A string representation of the JSON object that can be used as the response body.
    """
     
#     print template_values
#     tmpl = template (template_src, template_values)
#     print tmpl
#     print "Context:", tmpl[980:1000]
    body = json.loads (template (template_src, template_values), object_pairs_hook = OrderedDict)
    merge_property_errors (body, build_message_status (template_values))
    return json.dumps (body, indent = 4, separators = [",", ": "])

def get_error_body (status, msg = None):
    """
    Build a response body for an error response.
    
    :param status: The HTTP status code for the error.
    :param msg: A message to use instead of the standard HTTP status message.
    
    :return The body for the HTTP response.
    """
    
    if (msg is None):
        msg = create_response_with_status (description = HTTP_CODES[status])
    elif (isinstance (msg, basestring)):
        msg = create_response_with_status (description = msg)
    
    error = OrderedDict ([("error", build_message_status (msg, include_type = True))])
    return json.dumps (error, indent = 4, separators = [",", ": "])

def build_extended_info_entry (code = completion_code.success, message = "", include_type = False):
    """
    Build a single entry for the list of extended message information for a response object.
    
    :param code: The completion code to report in the entry.
    :param message: The message for the entry error description.  This will not be populated if
    the code indicates a success.
    :param include_type: A flag indicating ef the Message object type should be included in the
    entry.
    
    :return A dictionary that can be used as part of a JSON object in the response.
    """
    
    entry = OrderedDict ()
    if include_type:
        entry["@odata.type"] = "/redfish/v1/$metadata#Message.v1_0_0.Message"
        
    entry["Oem"] = OrderedDict ([
        ("Microsoft", OrderedDict ([
            ("@odata.type", "#Ocs.v1_0_0.Message"),
            ("CompletionCode", code)
        ]))
    ])
    
    if (message):
        entry["Oem"]["Microsoft"]["Description"] = message
        
    return entry
    
def build_message_status (status, include_type = False):
    """
    Build an object representation for the status of a request.
    
    :param status: A dictionary containing the status information for the request.
    :param include_type: A flag indicating if the Message object type should be included in the
    output. 
    
    :return A dictionary that can be used as a JSON object in the response.
    """
    
    annotations = OrderedDict ()
    
    for key in property_error_keys:
        if (key in status):
            build_property_errors (key, status[key], annotations)
        
    extended_info = []
    
    if (action_param_error_key in status):
        for _, errors in status[action_param_error_key].items ():
            for error in errors:
                extended_info.append (build_extended_info_entry (code = completion_code.failure,
                    message = error, include_type = include_type))
                
    if (response_status_key in status):
        for error in status[response_status_key]:
            message = error.get (completion_code.desc, "")
            extended_info.append (build_extended_info_entry (code = error[completion_code.cc_key],
                message = message, include_type = include_type))
            
    if (not extended_info):
        if (not annotations):
            extended_info.append (build_extended_info_entry (
                message = status.get (completion_code.desc, ""), include_type = include_type))
        else:
            extended_info.append (build_extended_info_entry (code = completion_code.failure,
                include_type = include_type))
        
    if (extended_info):
        annotations["@Message.ExtendedInfo"] = extended_info
    return annotations

def build_property_errors (error_type, status, annotated, dict_type = OrderedDict):
    """
    Update the status object with annotations for property-specific errors.
    
    :param error_type: The type of property error to add to the status.
    :param status: A dictionary containing the error information for the request for the specific
    type of property error.
    :param annotated: The dictionary object that will be updated with the error information.
    :param dict_type: The type of dictionary to use when creating new sub-object entries in the
    annotated output.
    """
    
    for prop, msg in status.items ():
        if (hasattr (msg, "keys")):
            if (prop not in annotated):
                annotated[prop] = dict_type ()
                
            build_property_errors (error_type, msg, annotated[prop], dict_type)
        elif (isinstance (msg, list)):
            if (prop not in annotated):
                annotated[prop] = []
                
            if (len (annotated[prop]) < len (msg)):
                annotated[prop].extend (
                    [dict_type () for i in range (len (annotated[prop]), len (msg))])
                
            for i, entry in enumerate (msg):
                build_property_errors (error_type, entry, annotated[prop][i], dict_type)
        else:
            annotated["{0}@Message.ExtendedInfo".format (prop)] = OrderedDict ([
                ("MessageId", "Base.1.0.{0}".format (error_type)),
                ("Message", msg)
            ])
                
def create_response_with_status (code = completion_code.failure, description = ""):
    """
    Create a new dictionary that contains response status information with the provided information.
    
    :param code: The completion code to use for the status entry.
    :param description: The error description for the status entry.
    
    :return The new dictionary appropriate to use as a response structure.
    """
    
    if (hasattr (code, "keys")):
        result = {}
        append_response_information (result, code)
        return result
    else:
        return {
            response_status_key : [{
                completion_code.cc_key : code,
                completion_code.desc : description
            }]
        }

def update_and_replace_status_information (result, data):
    """
    Merge status information from one set of response information into another, and remove any
    status information already present in the destination set of information.  If there is no status
    information available for replacement, the response will no longer contain status information.
    
    :param result: The dictionary that contains the information to provide in the response.  This
    will be updated with the new status information.
    :param data: The dictionary that contains the status information to use as a replacement.  If
    this is empty, no update is performed.
    """
    
    if (data):
        for key in top_level_status_keys:
            result.pop (key, None)
            if (key in data):
                result[key] = data[key]

def append_rack_manager_configuration (result):
    """
    Append the current rack manager configuration to the set of response information.
    
    :param result: The dictionary that contains the information to provide in the response.  This
    will be updated to include the current configuration.
    """
    
    result[manager_config_key] = get_mode ()
    
def append_response_information (result, data):
    """
    Add error information to be provided as part of the response.
    
    :param result: The dictionary that contains the information to provide in the response.  This
    will be updated with the additional data.
    :param data: The dictionary of information to add to the response information.
    """
    
    merge_all_property_errors (result, data)
    merge_action_parameter_errors (result, data)
    merge_response_status (result, data)
     
    if (completion_code.cc_key in data):
        if (data[completion_code.cc_key] == completion_code.success):
            result.update (data)
        else:
            if (response_status_key not in result):
                result[response_status_key] = []
                
            result[response_status_key].append (data)
    else:
        result.update (data)
        
def merge_response_status (result, data, copy = False):
    """
    Merge all response status information from one dictionary into another one.
    
    :param result: The dictionary that will be merged into.
    :param data: The dictionary whose response status will be merged.  The response status
    information will not be present in this dictionary at the end of the operation.
    :param copy: A flag indicating that the response status information should be left in the source
    dictionary.
    """
    
    for key in [response_status_key]:
        if (key in data):
            if (key in result):
                result[key].extend (data[key])
            else:
                result[key] = data[key]
                
            if (not copy):
                del data[key]
    
def merge_action_parameter_errors (result, data, copy = False):
    """
    Merge all action parameter error information from one dictionary into another one.
    
    :param result: The dictionary that will be merged into.
    :param data: The dictionary whose parameter errors will be merged.  The parameter errors will
    not be present in this dictionary at the end of the operation.
    :param copy: A flag indicating that the parameter errors should be left in the source
    dictionary.
    """
    
    if (action_param_error_key in data):
        if (action_param_error_key in result):
            action_error = result[action_param_error_key]
            for error_type, errors in data[action_param_error_key].items ():
                if (error_type in action_error):
                    action_error[error_type].extend (errors)
                else:
                    action_error[error_type] = errors
        else:
            result[action_param_error_key] = data[action_param_error_key]
            
        if (not copy):
            del data[action_param_error_key]

def merge_all_property_errors (result, data, copy = False):
    """
    Merge all property error information from one dictionary into another one.
    
    :param result: The dictionary that will be merged into.
    :param data: The dictionary whose property errors will be merged.  The property errors will not
    be present in this dictionary at the end of the operation.
    :param copy: A flag indicating that the property errors should be left in the source dictionary.
    """
    
    for key in property_error_keys:
        if (key in data):
            if (key in result):
                merge_property_errors (result[key], data[key])
            else:
                result[key] = data[key]
                
            if (not copy):
                del data[key]
            
def merge_property_errors (result, data):
    """
    Merge property error information from two dictionaries.
    
    :param result: The dictionary containing response information will receive the merged
    information.
    :param data: The dictionary that may contain property errors that need to be merged.
    """
    
    for key in data:
        if key in result:
            if (hasattr (data[key], "keys")):
                merge_property_errors (result[key], data[key])
            elif (isinstance (data[key], list)):
                for i, entry in enumerate (data[key]):
                    if (i < len (result[key])):
                        merge_property_errors (result[key][i], entry)
                    else:
                        result[key].append (entry)
            else:
                pass # Ignore this situation, it should never happen."
        else:
            result[key] = data[key]
            
def append_property_error (result, name, message):
    """
    Add error information for a specific property.
    
    :param result: The dictionary that will hold the property error information.
    :param name: The name of the property that has the error.  If a property is in a sub-object,
    this will be list of all parents, with the root being first and the property last.
    :param message: The error message to report for the property.
    """
    
    if (not isinstance (name, basestring)):
        last = result
        key = None
        for parent in name[:-1]:
            entry = re.match ("\[(\d+)\]", parent)
            if (entry):
                if (not key in last):
                    last[key] = []
                
                entry = int (entry.group (1))
                min_len = entry + 1
                if (len (last[key]) < min_len):
                    last[key].extend ([dict () for _ in range (len (last[key]), min_len)])
                    
                last = last[key][entry]
                key = None
            else:
                if key:
                    if (not key in last):
                        last[key] = {}
                    last = last[key]
                
                key = parent
        
        # We don't know the type of object to create for a key until we see the next path segment,
        # so here we need to create a container for the last segment.  If the last segment
        # references a list, then this will be skipped.
        if key:
            if (not key in last):
                last[key] = {}
            last = last[key]
            
        name = name[-1]
        result = last
      
    result[name] = message
    
def append_invalid_property_value (result, name, message):
    """
    Add error information to the response for a property that is specified with an invalid value.
    
    :param result: The dictionary that contains the response information.  This will be updtaed with
    the error information.
    :param name: The name of the property that has the value that is not valid.  If a property is
    a sub-object, this will be list of all parents, with the root being first and the property last.
    :param message: The error message to supply for the property.
    """
    
    if (invalid_property_value_key not in result):
        result[invalid_property_value_key] = {}
    
    append_property_error (result[invalid_property_value_key], name, message)

def append_invalid_property_type (result, name):
    """
    Add error information to the response for a property that is not the correct type.
    
    :param result: The dictionary that contains the response information.  This will be updtaed with
    the error information.
    :param name: The name of the property that has the type that is not valid.  If a property is
    a sub-object, this will be list of all parents, with the root being first and the property last.
    """
    
    if (invalid_property_type_key not in result):
        result[invalid_property_type_key] = {}
        
    append_property_error (result[invalid_property_type_key], name, 
        "The property {0} is not the correct type.".format (
            name if isinstance (name, basestring) else name[-1]))
        
def append_read_only_property (result, name):
    """
    Add error information to the response for a property that is specified with an invalid value.
    
    :param result: The dictionary that contains the response information.  This will be updtaed with
    the error information.
    :param name: The name of the property that has the value that is not valid.  If a property is
    a sub-object, this will be list of all parents, with the root being first and the property last.
    """
    
    if (read_only_property_key not in result):
        result[read_only_property_key] = {}
        
    append_property_error (result[read_only_property_key], name, 
        "The property {0} is a read-only value.".format (
            name if isinstance (name, basestring) else name[-1]))
    
def append_parameter_error (result, error, message):
    """
    Add error information to the response for a parameter supplied with an action that has an error.
    
    :param result: The dictionary that contains the information for the response.  This will be
    updated with the error information.
    :param error: The type of action parameter error.
    :param message: The error message for the parameter.
    """
    
    if (action_param_error_key not in result):
        result[action_param_error_key] = {}
    
    if (error not in result[action_param_error_key]):
        result[action_param_error_key][error] = []
        
    result[action_param_error_key][error].append (message)
    
def append_missing_parameter_error (result, name):
    """
    Add error information to the response for a missing action parameter.
    
    :param result: The dictionary that contains the information for the response.  This will be
    updated with the error information.
    :param name: The name of the missing parameter.
    """
    
    append_parameter_error (result, missing_error_key, 
        "Parameter {0} is missing from the request body.".format (name))
    
def append_unknown_parameter_error (result, name):
    """
    Add error information to the response for an unknown action parameter.
    
    :param result: The dictionary that contains the information for the response.  This will be
    updated with the error information.
    :param name: The name of the unknown parameter.
    """
    
    append_parameter_error (result, param_unknown_key,
        "Parameter {0} is not a valid parameter.".format (name))
    
def append_parameter_type_error (result, name):
    """
    Add error information to the response for a parameter that has the wrong type.
    
    :param result: The dictionary that contains the information for the response.  This will be
    updated with the error information.
    :param name: The name of the parameter with the wrong type.
    """
    
    append_parameter_error (result, param_type_error_key,
        "Parameter {0} is not the correct type.".format (name))

def has_completion_errors (result):
    """
    Indicate if the specified response information contains information about errors executing
    requsets.
    
    :param result: The response information to check.
    
    :return True if the response contains error information.
    """
    
    return (response_status_key in result)

def transform_dict_keys (values, key_func, dict_type = dict):
    """
    Recursively transform the keys of a dictionary.
    
    :param values: The dictionary of values whose keys will be transformed.
    :param key_func: The transformation function to generate the new keys.
    :param dict_type: The type of dictionary to use for the modified keys.
    
    :return The new dictionary with the transformed keys.
    """
    
    transformed = dict_type ()
    
    for key, value in values.items ():
        new_key = key_func (key)
        if (hasattr (value, "keys") and (key != response_status_key)):
            transformed[new_key] = transform_dict_keys (value, key_func, dict_type)
        elif (isinstance (value, list) and (key != response_status_key)):
            update = []
            for entry in value:
                if (hasattr (entry, "keys")):
                    update.append (transform_dict_keys (entry, key_func, dict_type))
                else:
                    update.append (entry)
            transformed[new_key] = update
        elif (key == completion_code.cc_key):
            transformed[key] = value
        else:
            transformed[new_key] = value
    
    return transformed

def replace_key_spaces (values, dict_type = dict):
    """
    Replaces the spaces and dashes in all key names in the provided dictionary with an underscore,
    unless that key is for a completion code.
    
    :param values: The dictionary of values whose keys need to be adjusted.
    :param dict_type: The type of dictionary to use for the modified keys.
    
    :return The new dictionary that contains no keys with spaces, except for completion codes.
    """
    
    def replace_spaces (key):
        if (isinstance (key, basestring)):
            return key.replace (" ", "_").replace ("-", "_")
        else:
            return key
    
    return transform_dict_keys (values, replace_spaces, dict_type)

def remove_key_leading_number (values, dict_type = dict):
    """
    Make sure that all keys start with a character instead of a number.  Any key that starts with a
    number will be replaced with one that prepends and underscore.
    
    :param values: The dictionary of values whose keys need to be adjusted.
    :param dict_type: The type of dictionary to use for the modified keys.
    
    :return The new dictionary that contains not keys that start with a number.
    """
    
    def prepend_underscore (key):
        if (isinstance (key, basestring)):
            return "_" + key if (key[0].isdigit ()) else key
        else:
            return key
    
    return transform_dict_keys (values, prepend_underscore, dict_type)

def flatten_nested_objects (values, parent = "", dict_type = dict):
    """
    Flattens a tree of objects represented as nested dictionaries into a single dictionary with no
    nesting.  All error information and completion codes will remain unchanged.
    
    :param values:  The dictionary of values to flatten.
    :param dict_type: The type of dictionary to use for the new values.
    
    :return The new flattened dictionary.
    """
    
    flat = dict_type ()
    for key, value in values.items ():
        new_key = parent + "_" + key if parent else key
        if (key in top_level_status_keys):
            flat[key] = value
        elif (hasattr (value, "keys")):
            flat.update (flatten_nested_objects (value, new_key, dict_type))
        else:
            flat[new_key] = value
            
    return flat

def get_json_request_data ():
    """
    Get the JSON data for the request.
    
    :return The JSON data in the request, or an empty dictionary if no JSON data was provided.
    """
    
    if request.json is not None:
        return request.json
    else:
        return {}
    
def get_json_default_resource (name, ordered = False, values = dict ()):
    """
    Get the JSON data for the default representation of a resource.
    
    :param name: The name of the resource to get.
    :param ordered: A flag indicating that the JSON object should preserve the parameter ordering.
    :param values: Additional values to pass to the template.
    
    :return The JSON data for the default resource.
    """
    
    values["TemplateDefault"] = True
    append_rack_manager_configuration (values)
    
    resource = resources.find_resource (name)
    body = template (resource.template, values)
    return json.loads (body, object_pairs_hook = OrderedDict if ordered else dict)
