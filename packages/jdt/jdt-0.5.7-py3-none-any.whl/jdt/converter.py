import json

def converter(cs, SLAP_URL, scopesObject):
    title = ""
    description = ""
    if "id" in cs.keys():
        title = cs["id"]
    if "description" in cs.keys():
        description = cs["description"]

    swag = {
            "openapi": "3.0.2",
            "info": {
                "title": f'{title} Capability Statement',
                "description": description,
                "license": {
                    "name": "Creative Commons Zero v1.0 Universal",
                    "url": "http://spdx.org/licenses/CC0-1.0.html"
                },
                "version": "1.0.0",
                "contact": {
                    "name": "HL7 Financial Management Working Group",
                    "email": "fm@lists.HL7.org",
                    "url": "http://www.hl7.org/Special/committees/fm/index.cfm"
                }
            },
            "externalDocs": {
                "url": cs["url"],
                "description": "FHIR Capability Statement"
            },
            "paths": {
                "/metadata": {
                    "summary": "Access to the server's Capability Statement",
                    "get": {
                        "summary": "Return the Capability Statement",
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
                                "description": "The Capability Statement",
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
                                "$ref": "#/components/parameters/format"
                            },
                            {
                                "$ref": "#/components/parameters/pretty"
                            },
                            {
                                "$ref": "#/components/parameters/summary"
                            },
                            {
                                "$ref": "#/components/parameters/elements"
                            }
                        ]
                    }
                }
            }
        }

    components = {
      "parameters": {
        "rid": {
          "name": "rid",
          "in": "path",
          "description": "id of the resource (\u003dResource.id)",
          "required": True,
          "allowEmptyValue": False,
          "style": "simple",
          "schema": {
            "type": "string"
          }
        },
        "hid": {
          "name": "hid",
          "in": "path",
          "description": "id of the history entry (\u003dResource.meta.versionId)",
          "required": True,
          "allowEmptyValue": False,
          "style": "simple",
          "schema": {
            "type": "string"
          }
        },
        "summary": {
          "name": "_summary",
          "in": "query",
          "description": "Requests the server to return a designated subset of the resource",
          "allowEmptyValue": True,
          "style": "form",
          "schema": {
            "type": "string",
            "enum": [
              "true",
              "text",
              "data",
              "count",
              "false"
            ]
          }
        },
        "format": {
          "name": "_format",
          "in": "query",
          "description": "Specify alternative response formats by their MIME-types (when a client is unable acccess accept: header)",
          "allowEmptyValue": True,
          "style": "form",
          "schema": {
            "type": "string",
            "format": "mime-type"
          }
        },
        "pretty": {
          "name": "_pretty",
          "in": "query",
          "description": "Ask for a pretty printed response for human convenience",
          "allowEmptyValue": True,
          "style": "form",
          "schema": {
            "type": "boolean"
          }
        },
        "elements": {
          "name": "_elements",
          "in": "query",
          "description": "Requests the server to return a collection of elements from the resource",
          "allowEmptyValue": True,
          "style": "form",
          "explode": False,
          "schema": {
            "type": "array",
            "format": "string",
            "items": {
              "format": "string"
            }
          }
        },
        "count": {
          "name": "_count",
          "in": "query",
          "description": "The maximum number of search results on a page. The server is not bound to return the number requested, but cannot return more",
          "schema": {
            "type": "number"
          }
        }
      }
    }

    security = [{
        "type": "oauth2",
        "description": "Smart on FHIR implementation of Oauth2",
        "name": "Authorization",
        "in": "header",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "flows": [{
            "authorizationCode": {
                "authorizationUrl": f'{SLAP_URL}/authorize',
                "tokenUrl": f'{SLAP_URL}/token',
                "scopes": scopesObject
            }
        }]
    }]

    for rest in cs['rest']:
        # find the rest object that represents the server
        if rest["mode"] == "server":
            for resource in rest["resource"]:
                # iterate over every resource and create a paths object for every interaction it has.  use existing openapi sample for bootstrap
                for i in resource["interaction"]:
                    if i["code"] == "read":
                        swag['paths'][f'/{resource["type"]}/' + '{rid}'] = {
                                "get": {
                                    "description": f'Returns a specified {resource["type"]} resource with a given resource id',
                                    "responses": {
                                        "default": {
                                            "description":"Error, with details",
                                            "content":{
                                                "application/fhir+json":{
                                                    "schema":{
                                                        "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                    }
                                                }
                                            }
                                        },
                                        "200": {
                                            "description": f'A {resource["type"]} with specified resource id',
                                            "content":{
                                                "application/fhir+json":{
                                                    "schema":{
                                                        "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "security": {
                                        "oauth2": [
                                            f'patient/{resource["type"]}.read'
                                        ]
                                    },
                                    "parameters":[
                                        {
                                            "$ref":"#/components/parameters/rid"
                                        },
                                        {
                                            "$ref":"#/components/parameters/summary"
                                        },
                                        {
                                            "$ref":"#/components/parameters/format"
                                        },
                                        {
                                            "$ref":"#/components/parameters/pretty"
                                        },
                                        {
                                            "$ref":"#/components/parameters/elements"
                                        }
                                    ]
                                }
                            }
                    elif i["code"] == "vread":
                         swag['paths'][f'/{resource["type"]}/' + '{rid}/_history/{hid}'] = {
                             "get": {
                                 "description": f'Returns a specified {resource["type"]} resource with a given resource id and a specific historical version',
                                 "responses": {
                                     "default": {
                                         "description":"Error, with details",
                                         "content":{
                                             "application/fhir+json":{
                                                 "schema":{
                                                     "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                 }
                                             }
                                         }
                                     },
                                     "200": {
                                         "description": f'A {resource["type"]} with specified resource id and specified version id',
                                         "content":{
                                             "application/fhir+json":{
                                                 "schema":{
                                                     "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                 }
                                             }
                                         }
                                     }
                                 },
                                "security": {
                                    "oauth2": [
                                        f'patient/{resource["type"]}.read'
                                    ]
                                },
                                 "parameters":[
                                     {
                                         "$ref":"#/components/parameters/rid"
                                     },
                                     {
                                         "$ref":"#/components/parameters/hid"
                                     },
                                     {
                                         "$ref":"#/components/parameters/summary"
                                     },
                                     {
                                         "$ref":"#/components/parameters/format"
                                     },
                                     {
                                         "$ref":"#/components/parameters/pretty"
                                     },
                                     {
                                         "$ref":"#/components/parameters/elements"
                                     }
                                 ]
                             }
                         }
                    elif i["code"] == "history-instance":
                         swag['paths'][f'/{resource["type"]}/' + '{rid}/_history'] = {
                             "get": {
                                 "description": f'Returns a bundle of all versions for the {resource["type"]} resource with given resource id',
                                 "responses": {
                                     "default": {
                                         "description":"Error, with details",
                                         "content":{
                                             "application/fhir+json":{
                                                 "schema":{
                                                     "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                 }
                                             }
                                         }
                                     },
                                     "200": {
                                         "description": f'A bundle of all versions for the {resource["type"]} resource with specified resource id',
                                         "content":{
                                             "application/fhir+json":{
                                                 "schema":{
                                                     "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                 }
                                             }
                                         }
                                     }
                                 },
                                "security": {
                                    "oauth2": [
                                        f'patient/{resource["type"]}.read'
                                    ]
                                },
                                 "parameters":[
                                     {
                                         "$ref":"#/components/parameters/rid"
                                     },
                                     {
                                         "$ref":"#/components/parameters/summary"
                                     },
                                     {
                                         "$ref":"#/components/parameters/format"
                                     },
                                     {
                                         "$ref":"#/components/parameters/pretty"
                                     },
                                     {
                                         "$ref":"#/components/parameters/elements"
                                     }
                                 ]
                             }
                         }
                    elif i["code"] == "history-type":
                         swag['paths'][f'/{resource["type"]}/_history'] = {
                             "get": {
                                 "description": f'Returns a bundle of all versions for the {resource["type"]} resources that match provided search parameters',
                                 "responses": {
                                     "default": {
                                         "description":"Error, with details",
                                         "content":{
                                             "application/fhir+json":{
                                                 "schema":{
                                                     "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                 }
                                             }
                                         }
                                     },
                                     "200": {
                                         "description": f'A bundle of all versions for the {resource["type"]} resource s that match provided search parameters',
                                         "content":{
                                             "application/fhir+json":{
                                                 "schema":{
                                                     "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                 }
                                             }
                                         }
                                     }
                                 },
                                "security": {
                                    "oauth2": [
                                        f'user/{resource["type"]}.read'
                                    ]
                                },
                                 "parameters":[
                                     {
                                         "$ref":"#/components/parameters/summary"
                                     },
                                     {
                                         "$ref":"#/components/parameters/format"
                                     },
                                     {
                                         "$ref":"#/components/parameters/pretty"
                                     },
                                     {
                                         "$ref":"#/components/parameters/elements"
                                     }
                                 ]
                             }
                         }
                         if "searchParam" in i.keys():
                             for param in i["searchParam"]:
                                 swag['paths'][f'/{resource["type"]}/_history']["get"]["parameters"].append({
                                     "$ref":f'#components/parameters/{param["name"]}'
                                 })
                                 components["parameters"][param["name"]] = {
                                      "name": param["name"],
                                      "in": "path",
                                      "required": False,
                                      "allowEmptyValue": False,
                                      "description": param["definition"],
                                      "schema": {
                                        "type": param["type"]
                                      }
                                    }
                    elif i["code"] == "search-type":
                         swag['paths'][f'/{resource["type"]}'] = {
                             "get": {
                                 "description": f'Returns a bundle of all versions for the {resource["type"]} resources that match provided search parameters',
                                 "responses": {
                                     "default": {
                                         "description":"Error, with details",
                                         "content":{
                                             "application/fhir+json":{
                                                 "schema":{
                                                     "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                 }
                                             }
                                         }
                                     },
                                     "200": {
                                         "description": f'A bundle of all versions for the {resource["type"]} resource s that match provided search parameters',
                                         "content":{
                                             "application/fhir+json":{
                                                 "schema":{
                                                     "$ref":"https://hl7.org/fhir/R4/fhir.schema.json#/definitions/OperationOutcome"
                                                 }
                                             }
                                         }
                                     }
                                 },
                                "security": {
                                    "oauth2": [
                                        f'patient/{resource["type"]}.read'
                                    ]
                                },
                                 "parameters":[
                                     {
                                         "$ref":"#/components/parameters/summary"
                                     },
                                     {
                                         "$ref":"#/components/parameters/format"
                                     },
                                     {
                                         "$ref":"#/components/parameters/pretty"
                                     },
                                     {
                                         "$ref":"#/components/parameters/elements"
                                     }
                                 ]
                             }
                         }
                         if "searchParam" in i.keys():
                             for param in i["searchParam"]:
                                 swag['paths'][f'/{resource["type"]}']["get"]["parameters"].append({
                                     "$ref":f'#components/parameters/{param["name"]}'
                                 })
                                 components["parameters"][param["name"]] = {
                                      "name": param["name"],
                                      "in": "path",
                                      "required": False,
                                      "allowEmptyValue": False,
                                      "description": param["definition"],
                                      "schema": {
                                        "type": param["type"]
                                      }
                                    }
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
    
    swag["security"] = security
    swag["components"] = components
    return swag
    

if __name__ == "__main__":
    cs = json.loads(open("sampleCS.json", 'r').read())
    scopes = {
      "fhirUser":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/fhirUser"
      ],
      "openid":[
         "openid"
      ],
      "system/*.*":[
         
      ],
      "system/*.read":[
         
      ],
      "system/*.write":[
         
      ],
      "patient/*.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPatient.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPatient.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPractitioner.read"
      ],
      "patient/*.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPatient.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPatient.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPractitioner.read"
      ],
      "patient/*.write":[
         
      ],
      "user/*.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPatient.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPatient.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPractitioner.read"
      ],
      "user/*.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPatient.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FOrganization.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPatient.read",
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPractitioner.read"
      ],
      "user/*.write":[
         
      ],
      "patient/Coverage.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read"
      ],
      "patient/Coverage.write":[
         
      ],
      "user/Coverage.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read"
      ],
      "user/Coverage.write":[
         
      ],
      "patient/Coverage.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FCoverage.read"
      ],
      "user/Coverage.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FCoverage.read"
      ],
      "patient/ExplanationOfBenefit.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read"
      ],
      "patient/ExplanationOfBenefit.write":[
         
      ],
      "user/ExplanationOfBenefit.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read"
      ],
      "user/ExplanationOfBenefit.write":[
         
      ],
      "patient/ExplanationOfBenefit.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FExplanationOfBenefit.read"
      ],
      "user/ExplanationOfBenefit.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FExplanationOfBenefit.read"
      ],
      "patient/Organization.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FOrganization.read"
      ],
      "patient/Organization.write":[
         
      ],
      "user/Organization.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FOrganization.read"
      ],
      "user/Organization.write":[
         
      ],
      "patient/Organization.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FOrganization.read"
      ],
      "user/Organization.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FOrganization.read"
      ],
      "patient/Patient.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPatient.read"
      ],
      "patient/Patient.write":[
         
      ],
      "user/Patient.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPatient.read"
      ],
      "user/Patient.write":[
         
      ],
      "patient/Patient.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPatient.read"
      ],
      "user/Patient.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPatient.read"
      ],
      "patient/Practitioner.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPractitioner.read"
      ],
      "patient/Practitioner.write":[
         
      ],
      "user/Practitioner.read":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPractitioner.read"
      ],
      "user/Practitioner.write":[
         
      ],
      "patient/Practitioner.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/patient%2FPractitioner.read"
      ],
      "user/Practitioner.*":[
         "https://nwsfdevrbyhtenantb2c.onmicrosoft.com/nw-sf-dev-uses0-rbyh-safhirapi-app/user%2FPractitioner.read"
      ]
    }
    scopesObject = {
        "fhirUser": "required scope",
        "openid": "required scope",
        "patient/*.*": "perform all actions for a given patient",
        "patient/*.read": "read all resources for a given patient",
        "user/*.*": "perform all actions for multiple patients",
        "user/*.read": "read all resources for multiple patients",
    }
    for key in scopes.keys():
        if len(scopes[key]) != 0 and key not in ["fhirUser", "openid", "patient/*.*", "user/*.*", "patient/*.read", "user/*.read", "user/*.write", "patient/*.write"]:
            scopesObject[key] = f'{key.split(".")[-1]} the {(key.split("/")[-1]).split(".")[0]} resource'
    
    data = converter(cs, "https://slap.com", scopesObject)
    print(json.dumps(data, indent=4))