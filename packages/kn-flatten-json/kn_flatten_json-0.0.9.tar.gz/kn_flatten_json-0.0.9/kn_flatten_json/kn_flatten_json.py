import requests
from pyspark.sql import SparkSession, DataFrame
from urllib.parse import urlparse
import json
import re
from pyspark.sql.functions import *
from pyspark.sql.types import *


def flatten_api(spark=None, url=None, method=None, body=None, authToken=None, username=None, password=None,sep="_"):
                      
    # replace unwanted characters from columns of api data
    def replace_dots_except_integers(string):
        pattern = r'\b\d+\.\d+\b|\b\d+\b'

        dots_within_integers = re.findall(pattern, string)

        result = re.sub(r'\.', '', string)

        for dot in dots_within_integers:
            result = result.replace(dot.replace('.', ''), dot)

        return result
                     
    headers = {"Content-Type": 'application/json'}
    request_func = getattr(requests, method.lower(), None)

    try:
        valid_separators = ['_']  # List of valid separators
        if sep not in valid_separators:
            raise ValueError(
                f"Invalid separator '{sep}'. Please use one of the following separators: {', '.join(valid_separators)}")

        # Check if url is a valid URL
        if not urlparse(url).scheme:
            raise ValueError("Invalid URL provided Please Check the value of url.")

        # Check if spark is an instance of SparkSession
        if not isinstance(spark, SparkSession):
            raise ValueError("spark must be an instance of SparkSession.")

        # Validate authentication variables if provided
        if username is not None and authToken is not None:
            raise ValueError("Both 'username' and 'authToken' cannot be provided at the same time.")

        if password is not None and authToken is not None:
            raise ValueError("Both 'password' and 'authToken' cannot be provided at the same time.")

        # validate method is of post and get type only

        if request_func is None or method.upper() not in ["GET", "POST"]:
            raise ValueError("Invalid method. Only 'GET' and 'POST' methods are supported.")

        # set authtype variable for authentication type basic or Token #############################
        if username == None and authToken == None:
            auth = False
            if body is not None:
                if not isinstance(body, dict):
                    raise ValueError("Invalid value for 'body'. It must be a dictionary.")
        else:
            auth = True
            if username != None:
                authtype = 'basic'
                if not isinstance(username, str) or username.strip() == "":
                    raise ValueError("Invalid value for 'username'. It must be a non-empty string.")
                if not isinstance(password, str) or password.strip() == "":
                    raise ValueError("Invalid value for 'password'. It must be a non-empty string.")
                if body is not None:
                    if not isinstance(body, dict):
                        raise ValueError("Invalid value for 'body'. It must be a dictionary.")
            else:
                authtype = 'token'
                if not isinstance(authToken, str) or authToken.strip() == "":
                    raise ValueError("Invalid value for 'authToken'. It must be a non-empty string.")
                if body is not None:
                    if not isinstance(body, dict):
                        raise ValueError("Invalid value for 'body'. It must be a dictionary.")
        if body != None and auth == True:
            if authtype == 'basic':
                auth = (username, password)
                response = request_func(url=url,
                                        auth=auth, headers=headers, json=body, verify=True)
            else:
                headers = {
                    'Authorization': 'Bearer ' + authToken,
                    'Content-Type': 'application/json'}
                response = request_func(url=url,
                                        headers=headers, json=body, verify=True)
        elif body != None and auth == False:
            response = request_func(url=url,
                                    headers=headers, json=body, verify=True)
        elif body == None and auth == True:
            if authtype == 'basic':
                auth = (username, password)
                response = request_func(url=url,
                                        auth=auth, headers=headers, verify=True)
            else:
                headers = {
                    'Authorization': 'Bearer ' + authToken,
                    'Content-Type': 'application/json'}
                response = request_func(url=url,
                                        headers=headers, verify=True)
        else:
            response = request_func(url=url,
                                    headers=headers, verify=True)

        res = response.text
        res1 = replace_dots_except_integers(res)

        if ':\"\"' in res:
            res1 = res1.replace(':\"\"', ':\"None\"')
        else:
            res1 = res1.replace(':\'\'', ':\'None\'')
        df = spark.read.json(spark.sparkContext.parallelize([res1]))

        # compute Complex Fields (Arrays, Structs and Maptypes) in Schema
        complex_fields = dict(
            [
                (field.name, field.dataType)
                for field in df.schema.fields
                if type(field.dataType) == ArrayType
                   or type(field.dataType) == StructType
                   or type(field.dataType) == MapType
            ]
        )

        while len(complex_fields) != 0:
            col_name = list(complex_fields.keys())[0]

            # if StructType then convert all sub element to columns.
            # i.e. flatten structs
            if type(complex_fields[col_name]) == StructType:
                expanded = [
                    col(col_name + "." + k).alias(col_name + sep + k)
                    for k in [n.name for n in complex_fields[col_name]]
                ]
                df = df.select("*", *expanded).drop(col_name)

            # if ArrayType then add the Array Elements as Rows using the explode function
            # i.e. explode Arrays
            elif type(complex_fields[col_name]) == ArrayType:
                df = df.withColumn(col_name, explode_outer(col_name))

            # if MapType then convert all sub element to columns.
            # i.e. flatten
            elif type(complex_fields[col_name]) == MapType:
                keys_df = df.select(explode_outer(map_keys(col(col_name)))).distinct()
                keys = list(map(lambda row: row[0], keys_df.collect()))
                key_cols = list(
                    map(
                        lambda f: col(col_name).getItem(f).alias(str(col_name + sep + f)),
                        keys,
                    )
                )
                drop_column_list = [col_name]
                df = df.select(
                    [
                        col_name
                        for col_name in df.columns
                        if col_name not in drop_column_list
                    ]
                    + key_cols
                )

            # recompute remaining Complex Fields in Schema
            complex_fields = dict(
                [
                    (field.name, field.dataType)
                    for field in df.schema.fields
                    if type(field.dataType) == ArrayType
                       or type(field.dataType) == StructType
                       or type(field.dataType) == MapType
                ]
            )

        return df

    except ValueError as e:
        print(str(e))

def kpt_flatten_json(df=None,sep="_"):
    try:
        # Check if df is an instance of DataFrame
        if not isinstance(df, DataFrame):
            raise ValueError("df must be an instance of Dataframe.")
            
        complex_fields = dict(
            [
                (field.name, field.dataType)
                for field in df.schema.fields
                if type(field.dataType) == ArrayType
                or type(field.dataType) == StructType
                or type(field.dataType) == MapType
            ]
        )
        while len(complex_fields) != 0:
            col_name = list(complex_fields.keys())[0]
            if type(complex_fields[col_name]) == StructType:
                expanded = [
                    col(col_name + "." + k).alias(col_name + sep + k)
                    for k in [n.name for n in complex_fields[col_name]]
                ]
                df = df.select("*", *expanded).drop(col_name)

            elif type(complex_fields[col_name]) == ArrayType:
                df = df.withColumn(col_name, explode_outer(col_name))
            elif type(complex_fields[col_name]) == MapType:
                keys_df = df.select(explode_outer(map_keys(col(col_name)))).distinct()
                keys = list(map(lambda row: row[0], keys_df.collect()))
                key_cols = list(
                    map(
                        lambda f: col(col_name).getItem(f).alias(str(col_name + sep + f)),
                        keys,
                    )
                )
                drop_column_list = [col_name]
                df = df.select(
                    [
                        col_name
                        for col_name in df.columns
                        if col_name not in drop_column_list
                    ]
                    + key_cols
                )
            complex_fields = dict(
                [
                    (field.name, field.dataType)
                    for field in df.schema.fields
                    if type(field.dataType) == ArrayType
                    or type(field.dataType) == StructType
                    or type(field.dataType) == MapType
                ]
            )

        return df
    except ValueError as e:
        print(str(e))
