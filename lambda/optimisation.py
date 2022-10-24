import csv
from io import StringIO
import json
from unittest import result
import boto3
import pandas as pd

from ortools.linear_solver import pywraplp
from ortools.linear_solver import pywraplp

s3_client = boto3.client("s3")
S3_BUCKET = 'optimisationdata'

def write_results(results):
    csv_buffer = StringIO()
    results.to_csv(csv_buffer, index=False)

    response = s3_client.put_object(
        Bucket=S3_BUCKET, Key="results.csv", Body=csv_buffer.getvalue()
    )
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        print(f"Successful S3 put_object response. Status - {status}")
    else:
        print(f"Unsuccessful S3 put_object response. Status - {status}")

def load_data(object_key):    
    datafile = s3_client.get_object(Bucket=S3_BUCKET, Key=object_key)
    databody = datafile['Body']
    data_string = databody.read().decode('utf-8')

    data_df = pd.read_csv(StringIO(data_string))
    return data_df

def data_processing(data):
    return data

def batch_optimisation(data):
    single_result = optimisation(data)
    if single_result is not None:
        results_batch = pd.concat([single_result]*len(data), ignore_index=True)
    else:
        results_batch = None
    return results_batch

def optimisation(data):
    # Create the mip solver with the SCIP backend
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        return
    
    # Define the variables in the problem
    infinity = solver.infinity()
    # x and y are integer non-negative variables
    x = solver.IntVar(0.0, infinity, "x")
    y = solver.IntVar(0.0, infinity, "y")

    print("Number of variables =", solver.NumVariables())

    # Define the constraints in the problem
    # x + 7 * y <= 17.5
    solver.Add(x + 7 * y <= 17.5)

    # x <= 3.5
    solver.Add(x <= 3.5)

    print("Number of constraints =", solver.NumConstraints())

    # Maximize x + 10 * y
    solver.Maximize(x + 10 * y)

    # Define the objective function for the problem
    status = solver.Solve()

    print("\nAdvanced usage:")
    print('Problem solved in %f millisenconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

    objective_value = solver.Objective().Value()
    x_value = x.solution_value()
    y_value = y.solution_value()

    # Display the solution
    if status == pywraplp.Solver.OPTIMAL:
        print("Solution:")
        print("Objective value =", objective_value)
        print("x =", x_value)
        print("y =", y_value)
        result_dict = {"obj": [objective_value], "x": [x_value], "y": [y_value]}
        result_df = pd.DataFrame(result_dict)
        return result_df
    else:
        print("The problem does not have an optimal solution.")
        return None

def handler(event, context):

    print('request: {}'.format(json.dumps(event)))
    # load data from s3
    object_key = 'data.csv'
    data = load_data(object_key)

    # processing data
    data = data_processing(data)

    # optimisation: batch or single
    batch = 1
    if batch:
        results = batch_optimisation(data)
    else:
        results = optimisation(data)

    # write results to s3
    if results is not None:
        write_results(results)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'successful!'
    }