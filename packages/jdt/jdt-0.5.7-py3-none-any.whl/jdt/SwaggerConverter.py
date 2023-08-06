#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
# Alan Viars

import argparse
import json
from collections import OrderedDict
import os


DEFAULT_SMART_ON_FHIR_SECURITY_DESCRIPTION = os.getenv("DEFAULT_SMART_ON_FHIR_DESCRIPTION_SECURITY_DESCRIPTION",
                                                       """
1. See the [General Security Considerations](/Authorization_Authentication_and_Registration.html) section for requirements 
and recommendations. 1. A server **SHALL** reject any unauthorized requests by returning an `HTTP 401` unauthorized response code.
"""
                                                       )


def get_scopes():
    scopes = {"openid": "default",
              "fhirUser": "who is logged in",
              "profile": "default",
              "system/*.*": "All interactions allowed for all available resources",
              "system/*.read": "All read interactions allowed for all available resources",
              "system/*.write": "All write interactions allowed for all available resources",
              "patient/*.*": "All interactions allowed for a single patient for all available resources",
              "patient/*.read": "All read interactions allowed for single patient for all available resources",
              "patient/*.write": "All write interactions allowed for single patient for all available resources"
              }
    return scopes


# def get_component_parameters():
#    parameter_str = \
#    """
#    {"rid":{
#               "name":"rid",
#               "in":"path",
#               "description":"id of the resource (=Resource.id)",
#               "required":true,
#               "allowEmptyValue":false,
#               "style":"simple",
#               "schema":{
#                  "type":"string"
#               }
#            },
#            "hid":{
#               "name":"hid",
#               "in":"path",
#               "description":"id of the history entry (=Resource.meta.versionId)",
#               "required":true,
#               "allowEmptyValue":false,
#               "style":"simple",
#               "schema":{
#                  "type":"string"
#               }
#            },
#            "summary":{
#               "name":"_summary",
#               "in":"query",
#               "description":"Requests the server to return a designated subset of the resource",
#               "allowEmptyValue":true,
#               "style":"form",
#               "schema":{
#                  "type":"string",
#                  "enum":[
#                     "true",
#                     "text",
#                     "data",
#                     "count",
#                     "false"
#                  ]
#               }
#            },
#            "format":{
#               "name":"_format",
#               "in":"query",
#               "description":"Specify alternative response formats by their MIME-types (when a client is unable acccess accept: header)",
#               "allowEmptyValue":true,
#               "style":"form",
#               "schema":{
#                  "type":"string",
#                  "format":"mime-type"
#               }
#            },
#            "pretty":{
#               "name":"_pretty",
#               "in":"query",
#               "description":"Ask for a pretty printed response for human convenience",
#               "allowEmptyValue":true,
#               "style":"form",
#               "schema":{
#                  "type":"boolean"
#               }
#            },
#            "elements":{
#               "name":"_elements",
#               "in":"query",
#               "description":"Requests the server to return a collection of elements from the resource",
#               "allowEmptyValue":true,
#               "style":"form",
#               "explode":false,
#               "schema":{
#                  "type":"array",
#                  "format":"string",
#                  "items":{
#                     "format":"string"
#                  }
#               }
#            },
#            "count":{
#               "name":"_count",
#               "in":"query",
#               "description":"The maximum number of search results on a page. The server is not bound to return the number requested, but cannot return more",
#               "schema":{
#                  "type":"number"
#               }
#            }
#         }
#    """
#    return json.loads(parameter_str, object_pairs_hook=OrderedDict)


def get_metadata():
    metadata_str = \
        """{"summary": "Access to the Server's Capability Statement",
     "description": "All FHIR Servers return a CapabilityStatement that describes what services they perform",
     "get": {
         "summary": "Return the server's capability statement",
                "responses": {
                    "default": {
                        "description": "Error, with details",
                        "content": {
                        "application/fhir+json": {
                            "schema": {
                                "$ref": "https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                            }
                        }
                        }
                    },
                    "200": {
                        "description": "the capbility statement",
                        "content": {
                        "application/fhir+json": {
                            "schema": {
                                "$ref": "https://hl7.org/fhir/R4/fhir.schema.json#/definitions/CapabilityStatement"
                            }
                        }
                        }
                    }
                },
                "parameters": [
                    {
                        "$ref":"#/components/parameters/format"
                    },
                    {
                        "$ref":"#/components/parameters/pretty"
                    },
                    {
                        "$ref":"#/components/parameters/summary"
                    },
                    {
                        "$ref":"#/components/parameters/elements"
                    }
                ]
            }
        }"""
    return json.loads(metadata_str, object_pairs_hook=OrderedDict)


def get_interaction_stub(description):
    pass


def build_200_get_response(resource_type_name):
    response_str = \
        """
    {"description": "A RESOURCE_TYPE_NAME with specified resource id.",
     "content":{"application/fhir+json":{"schema":{"$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"}}}}
    """
    response_str = response_str.replace(
        "RESOURCE_TYPE_NAME", resource_type_name)
    response_200 = OrderedDict()
    response_200['200'] = json.loads(
        response_str, object_pairs_hook=OrderedDict)
    return response_200

# def build_eob_specific_parameters():
#    # returns a list of objects
#    eob_params_str = \
#        """
#        [
#        {
#                     "name":"_id",
#                     "in":"query",
#                     "schema":{
#                        "type":"string"
#                     },
#                     "description":"Logical id of this artifact"
#                  },
#                  {
#                     "name":"patient",
#                     "in":"query",
#                     "schema":{
#                        "type":"string"
#                     },
#                     "description":"The reference to the patient"
#                  },
#                  {
#                     "name":"_lastUpdated",
#                     "in":"query",
#                     "schema":{
#                        "type":"string",
#                        "pattern":"([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1])(T([01][0-9]|2[0-3]):[0-5][0-9]:([0-5][0-9]|60)(\\.[0-9]+)?(Z|(\\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00)))?)?)?"
#                     },
#                     "description":"When the resource version last changed"
#                  },
#                  {
#                     "name":"type",
#                     "in":"query",
#                     "schema":{
#                        "type":"string"
#                     },
#                     "description":"The type of the ExplanationOfBenefit"
#                  },
#                  {
#                     "name":"identifier",
#                     "in":"query",
#                     "schema":{
#                        "type":"string"
#                     },
#                     "description":"The business/claim identifier of the Explanation of Benefit"
#                  },
#                  {
#                     "name":"service-date",
#                     "in":"query",
#                     "schema":{
#                        "type":"string",
#                        "pattern":"([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1])(T([01][0-9]|2[0-3]):[0-5][0-9]:([0-5][0-9]|60)(\\.[0-9]+)?(Z|(\\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00)))?)?)?"
#                     },
#                     "description":"Date of the service for the EOB. The service-date search parameter simplifies search, since a client doesn't need to know that for inpatient and outpatient institutional EOB dates they need to search by billablePeriod.period.start, for a pharmacy EOB by item.servicedDate, and for a professional and non-clinician EOB - by item.servicedPeriod.period.start."
#                  }
#            ]
#            """
#    return json.loads(eob_params_str, object_pairs_hook=OrderedDict)


def build_oauth2_security_section(scopes, authorization_server_url, name="smart_on_fhir_oauth2"):
    security = {
        "type": "oauth2",
        "description": "Smart on FHIR implementation of OAuth2",
        "name": name,
        "in": "header",
        "scheme": "bearer",
        "flows": [{
            "authorizationCode": {
                "authorizationUrl": f'{authorization_server_url}/authorize',
                "tokenUrl": f'{authorization_server_url}/token',
                "refreshUrl": f'{authorization_server_url}/refresh',
                "scopes": scopes
            }
        }]
    }
    return security


def build_default_fhir_response():
    default_response = OrderedDict()
    default_json_str = \
        """
    {
        "description": "Error, with details",
        "content": {
            "application/fhir+json": {
                "schema": {
                    "$ref": "https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                }
            }
        }
    }
    """
    to_od_object = json.loads(default_json_str, object_pairs_hook=OrderedDict)
    default_response['default'] = to_od_object
    return default_response


def build_parameters(parameter_key_list):
    parameters = []
    for key in parameter_key_list:
        parameters.append({"$ref": f"#/components/parameters/{key}"})
    return parameters


def build_component_parameters(parameter_key_list):
    parameters = OrderedDict()
    for key in parameter_key_list:
        parameters[key] = {
            "name": key,
            "in": "path",
            "required": True,
            "depricated": False
        }
    return parameters


def smart_on_fhir_seciurity(description=DEFAULT_SMART_ON_FHIR_SECURITY_DESCRIPTION):
    return OrderedDict(("type", "apiKey",),
                       ("name", "authorization",),
                       ("in", "header",),
                       ("description", description))


def create_openapi_document_base(info_title, info_description, info_license_name, info_license_url,
                                 version, info_contact_name, info_contact_email, info_contact_url,
                                 externalDocs_url, externalDocs_description, openapi_version="3.0.3"):

    # Create an OpenAPI
    openapi = OrderedDict()

    # info inludes  title, desc, license, version, and contact info
    openapi['openapi'] = openapi_version
    openapi['info'] = OrderedDict()
    openapi['info']['title'] = info_title
    openapi['info']['description'] = info_description
    openapi['info']['license'] = OrderedDict()
    openapi['info']['license']['name'] = info_license_name
    openapi['info']['license']['url'] = info_license_url
    openapi['info']['version'] = version
    openapi['info']['contact'] = OrderedDict()
    openapi['info']['contact']['name'] = info_contact_name
    openapi['info']['contact']['email'] = info_contact_email
    openapi['info']['contact']['url'] = info_contact_url

    # external docs
    openapi['externalDocs'] = OrderedDict()
    openapi['externalDocs']['url'] = externalDocs_url
    openapi['externalDocs']['description'] = externalDocs_description

    # paths stub - other defs will fill out those.
    openapi['paths'] = OrderedDict()
    openapi['paths']['/metadata'] = get_metadata()

    # components stub - other defs will fil out those.
    openapi['components'] = OrderedDict()
    openapi['components']['parameters'] = OrderedDict()
    # return the ordered dict
    return openapi


def build_openapi_security_for_paths(scopes, security_name="smart_on_fhir_oauth2"):
    security = [{security_name: scopes}, ]
    return security


def add_openapi_paths(openapi, cs, authorization_server_url, fhir_server_base_url,
                      security_name="smart_on_fhir_oauth2"):
    """"Add the paths to the OpenAPI document using the "rest" section forom the FHIR Capability Statement."""
    results = OrderedDict()
    results['openapi'] = openapi
    results['errors'] = []
    add_security_section = False
    for rest in cs['rest']:

        if "security" in rest.keys():
            security = rest['security']
            if "service" in security.keys():
                for service in security['service']:
                    # get coding, text and description
                    # print(service['coding'])
                    for code in service['coding']:
                        if "code" in code.keys():
                            if code['code'] == "SMART-on-FHIR":
                                add_security_section = True

        # find the rest object that represents the server
        if rest["mode"] == "server":
            for resource in rest["resource"]:
                # iterate over every resource and create a paths object for every interaction it has.
                # use existing openapi sample for bootstrap
                if "interaction" in resource.keys():
                    for i in resource["interaction"]:
                        if i["code"] == "read":
                            path = "/%s/{rid}" % (resource["type"])
                            results['openapi']['paths'][path] = OrderedDict()

                            # get/read
                            results['openapi']['paths'][path]['get'] = OrderedDict()
                            results['openapi']['paths'][path]['get']['description'] = "Returns a specified %s resource with a given resource id" % (
                                resource["type"])
                            results['openapi']['paths'][path]['get']['responses'] = OrderedDict(
                            )
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_default_fhir_response())
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_200_get_response(resource["type"]))
                            parameter_list = ['rid', 'summary',
                                              'format', 'pretty', 'elements']
                            results['openapi']['paths'][path]['get']['parameters'] = build_parameters(
                                parameter_list)

                            iteration_parameters = build_component_parameters(
                                parameter_list)
                            for key in iteration_parameters:
                                if key not in results['openapi']['components']['parameters'].keys():
                                    results['openapi']['components']['parameters'][key] = iteration_parameters[key]

                            scopes = [f'patient/{resource["type"]}.read', ]
                            if add_security_section:
                                results['openapi']['paths'][path]['get']['security'] = build_openapi_security_for_paths(scopes=scopes,
                                                                                                                        security_name="smart_on_fhir_oauth2")
                        elif i["code"] == "vread":
                            # get/vread
                            path = "/%s/{rid}/_history/{hid}" % (
                                resource["type"])
                            results['openapi']['paths'][path] = OrderedDict()
                            results['openapi']['paths'][path]['get'] = OrderedDict()
                            results['openapi']['paths'][path]['get']['description'] = "Returns a specified %s resource with a given resource id and a specific historical version" % (
                                resource["type"])
                            results['openapi']['paths'][path]['get']['responses'] = OrderedDict(
                            )
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_default_fhir_response())
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_200_get_response(resource["type"]))
                            parameter_list = [
                                'rid', 'hid', 'summary', 'format', 'pretty', 'elements']
                            results['openapi']['paths'][path]['get']['parameters'] = build_parameters(
                                parameter_list)

                            iteration_parameters = build_component_parameters(
                                parameter_list)
                            for key in iteration_parameters:
                                if key not in results['openapi']['components']['parameters'].keys():
                                    results['openapi']['components']['parameters'][key] = iteration_parameters[key]

                            # Add security
                            scopes = [f'patient/{resource["type"]}.read', ]
                            if add_security_section:
                                results['openapi']['paths'][path]['get']['security'] = build_openapi_security_for_paths(scopes=scopes,
                                                                                                                        security_name="smart_on_fhir_oauth2")

                        elif i["code"] == "history-instance":
                            # get/history-instance
                            path = "/%s/{rid}/_history" % (resource["type"])
                            results['openapi']['paths'][path] = OrderedDict()
                            results['openapi']['paths'][path]['get'] = OrderedDict()
                            results['openapi']['paths'][path]['get']['description'] = "Returns a bundle of all versions for the %s resource with given resource id" % (
                                resource["type"])
                            results['openapi']['paths'][path]['get']['responses'] = OrderedDict(
                            )
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_default_fhir_response())
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_200_get_response(resource["type"]))
                            parameter_list = ['rid', 'summary',
                                              'format', 'pretty', 'elements']
                            results['openapi']['paths'][path]['get']['parameters'] = build_parameters(
                                parameter_list)

                            iteration_parameters = build_component_parameters(
                                parameter_list)
                            for key in iteration_parameters:
                                if key not in results['openapi']['components']['parameters'].keys():
                                    results['openapi']['components']['parameters'][key] = iteration_parameters[key]

                            # Add security
                            scopes = [f'patient/{resource["type"]}.read', ]
                            if add_security_section:
                                results['openapi']['paths'][path]['get']['security'] = build_openapi_security_for_paths(scopes=scopes,
                                                                                                                        security_name="smart_on_fhir_oauth2")
                        elif i["code"] == "history-type":
                            # get/history-type
                            path = "/%s/_history" % (resource["type"])
                            results['openapi']['paths'][path] = OrderedDict()
                            results['openapi']['paths'][path]['get'] = OrderedDict()
                            results['openapi']['paths'][path]['get']['description'] = "Returns a bundle of all versions for the %s resource that match provided search parameters" % (
                                resource["type"])
                            results['openapi']['paths'][path]['get']['responses'] = OrderedDict(
                            )
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_default_fhir_response())
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_200_get_response(resource["type"]))
                            parameter_list = ['summary',
                                              'format', 'pretty', 'elements']
                            results['openapi']['paths'][path]['get']['parameters'] = build_parameters(
                                parameter_list)
                            # Add the search Parameters
                            if "searchParam" in i.keys():
                                for param in i["searchParam"]:
                                    results['openapi']['paths'][path]['get']['parameters'].append({
                                        "$ref": f'#components/parameters/{param["name"]}'
                                    })
                                    parameter_list.append(param["name"])

                            iteration_parameters = build_component_parameters(
                                parameter_list)
                            for key in iteration_parameters:
                                if key not in results['openapi']['components']['parameters'].keys():
                                    results['openapi']['components']['parameters'][key] = iteration_parameters[key]

                            # Add security
                            scopes = [f'patient/{resource["type"]}.read', ]
                            if add_security_section:
                                results['openapi']['paths'][path]['get']['security'] = build_openapi_security_for_paths(scopes=scopes,
                                                                                                                        security_name="smart_on_fhir_oauth2")
                        elif i["code"] == "search-type":
                            # get/search-type
                            path = "/%s" % (resource["type"])
                            results['openapi']['paths'][path] = OrderedDict()
                            results['openapi']['paths'][path]['get'] = OrderedDict()
                            results['openapi']['paths'][path]['get']['description'] = "Returns a bundle of the %s resource that match provided search parameters" % (
                                resource["type"])
                            results['openapi']['paths'][path]['get']['responses'] = OrderedDict(
                            )
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_default_fhir_response())
                            results['openapi']['paths'][path]['get']['responses'].update(
                                build_200_get_response(resource["type"]))
                            parameter_list = ['summary',
                                              'format', 'pretty', 'elements']
                            results['openapi']['paths'][path]['get']['parameters'] = build_parameters(
                                parameter_list)
                            if "searchParam" in i.keys():
                                for param in i["searchParam"]:
                                    results['openapi']['paths'][path]['get']['parameters'].append({
                                        "$ref": f'#components/parameters/{param["name"]}'
                                    })
                                    parameter_list.append(param["name"])

                            iteration_parameters = build_component_parameters(
                                parameter_list)
                            for key in iteration_parameters:
                                if key not in results['openapi']['components']['parameters'].keys():
                                    results['openapi']['components']['parameters'][key] = iteration_parameters[key]

                            # Add security
                            scopes = [f'patient/{resource["type"]}.read', ]
                            if add_security_section:
                                results['openapi']['paths'][path]['get']['security'] = build_openapi_security_for_paths(scopes=scopes,
                                                                                                                        security_name="smart_on_fhir_oauth2")
                        # continue to add each of the following interactions
                        # elif i["code"] == "update":
                        # elif i["code"] == "patch":
                        # elif i["code"] == "delete":
                        # elif i["code"] == "create":
                        else:
                            # skip system interactions (not related to any resource)
                            pass
        else:
            # ignoring the client object, if its even there (unlikely)
            pass
    return results


def add_openapi_components(openapi, cs, authorization_server_url,
                           scopes=get_scopes(), security_name="smart_on_fhir_oauth2"):
    """Add the comentents to the OpenAPI document using the "rest" section forom the FHIR Capability Statement."""
    results = OrderedDict()
    results['openapi'] = openapi
    results['errors'] = []
    # restpart = cs['rest']
    # print("Create OpenAPI components.")
    results['openapi']['components']['securitySchemes'] = build_oauth2_security_section(scopes,
                                                                                        authorization_server_url=authorization_server_url,
                                                                                        name=security_name)
    return results


def open_and_read_cap_statement(input_capability_statement_file):
    cs = OrderedDict()
    # Open and read in the CS and/or config file containing a CS
    fh = open(input_capability_statement_file, 'rU')
    j = fh.read()
    j = json.loads(j, object_pairs_hook=OrderedDict)

    # Make sure it is what we are looking for
    if not isinstance(j, type(OrderedDict())):
        error_message = "File " + \
            str(input_capability_statement_file) + \
            " did not contain a JSON object, i.e. {}."
        print(error_message)
        raise Exception(error_message)
    # Get the cap statement from config file or as raw resource file.
    if 'CapabilityStatement' in j.keys():
        cs = j['CapabilityStatement']
    if 'resourceType' in j:
        if j['resourceType'] == 'CapabilityStatement':
            cs = j
    """Open the file and fetch the Capability statement"""
    return cs


def capstatement2swagger(cs, authorization_server_url="https://api.example.com",
                         fhir_server_base_url="https://fhir.example.com/baseR4",
                         security_name="smart_on_fhir_oauth2"):
    """Input an OrderedDict containing a FHIR Capabaility Statement"""

    result = OrderedDict()
    result['openapi'] = OrderedDict()
    # Get the contact info from the list
    info_contact_name = ""
    info_contact_email = ""
    info_contact_url = ""
    if "contact" in cs.keys():
        for contact in cs['contact']:
            if 'telecom' in contact.keys():
                for telecom in contact['telecom']:
                    if 'system' in telecom.keys():
                        if telecom['system'] == 'email':
                            info_contact_email = telecom['value']
                        if telecom['system'] == 'url':
                            info_contact_url = telecom['value']

    info_title = ""
    info_description = ""
    info_version = ""
    if "title" in cs.keys():
        info_title = cs["title"]
    if "description" in cs.keys():
        info_description = cs["description"]
    if "Version" in cs.keys():
        info_version = cs["version"]

    # Get the external document URL form the first list element in the CS
    externalDocs_url = ""
    if 'implementationGuide' in cs.keys():
        for ig in cs['implementationGuide']:
            externalDocs_url = ig
            break

    # create the base openAPI object
    openapi = create_openapi_document_base(info_title=info_title, info_description=info_description,
                                           info_license_name=os.getenv(
                                               "CS_INFO_LICENSE_NAME", "Creative Commons Zero v1.0 Universal"),
                                           info_license_url=os.getenv(
                                               "CS_INFO_LICENSE_URL", "http://spdx.org/licenses/CC0-1.0.html"),
                                           version=info_version, info_contact_name=info_contact_name,
                                           info_contact_email=info_contact_email,
                                           info_contact_url=info_contact_url,
                                           externalDocs_url=externalDocs_url,
                                           externalDocs_description=os.getenv("CS_EXTERNAL_DOCS_DESCRIPTION", "External Docs Description"),)

    # Add the "components" part including the security
    openapi_results = add_openapi_components(openapi, cs, authorization_server_url,
                                             get_scopes(), security_name=security_name)

    # Add the "paths" part
    openapi_results = add_openapi_paths(openapi_results['openapi'], cs, authorization_server_url,
                                        fhir_server_base_url, security_name=security_name)

    return openapi_results


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(
        description='Load in Capability Statement')

    parser.add_argument(
        dest='input_capability_statement_file',
        action='store',
        help='Input the Capability Statement file to load here.')

    parser.add_argument(
        dest='output_openapi_file',
        action='store',
        help="Enter the output filename.  This is the openapi document suitable for Swagger.")

    parser.add_argument('--auth_server',
                        dest='authorization_server_url',
                        action='store',
                        help='Authorization server base url.',
                        default='https://api.example.com')

    parser.add_argument('--fhir_server_base',
                        dest='fhir_server_base_url',
                        action='store',
                        help='FHIR Base URL.',
                        default='https://fhir.example.com/baseR4')

    args = parser.parse_args()

    result = capstatement2swagger(open_and_read_cap_statement(args.input_capability_statement_file),
                                  args.authorization_server_url, args.fhir_server_base_url)

    fh = open(args.output_openapi_file, 'w')
    fh.write(json.dumps(result['openapi'], indent=4))
    fh.close()
