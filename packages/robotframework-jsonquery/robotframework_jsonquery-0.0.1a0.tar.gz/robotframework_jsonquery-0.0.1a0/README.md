# robotframework-jsonquery [![tests](https://github.com/otemek/robotframework-jsonquery/actions/workflows/robotlib.yml/badge.svg?branch=master)](https://github.com/otemek/robotframework-jsonquery/actions/workflows/robotlib.yml)
Simple wrapper for libraries used to query json files with different query language implementations
- jsonpath-ng.ext (extended version with e.g. filters)
- jsonpath-ng
- jmespath

Example:
```Robot Framework
*** Settings ***
Library    JsonQuery    jsonpath-ng.ext

*** Test Cases ***
Read and query json file
    ${file}    Read Json File    sample.json
    Query Json    ${file}    friends[?(@.id>1)]    #jsonpath-ng.ext syntax

```

```Robot Framework
*** Settings ***
Library    JsonQuery    jmespath

*** Test Cases ***
Read and query json file
    ${file}    Read Json File    sample.json
    Query Json    ${file}    friends[?id>`1`]    #jmespath syntax

```
