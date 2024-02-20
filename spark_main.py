from curate_sql2delta import *

'''
    Example command line:
        python spark_main.py -t WORKTASKS -s bronze -d silver -c TOWWORKSv2 -x '[{"destination_tablename": "WORKTASKS","flatten_command": "select col.* from (select explode(WORKTASKS) from json)"}]' -f '{"datetimes": ["LastChangedDate", "EstimatedStartDate", "ActualStartDate"], "doubles":[], "ints":[]}' -i y -k TASKGUID -w LASTCHANGEDDATE -v '[{"error_message":"","validation_command":""}]'
'''

spark = get_or_create_spark('Local-Spark-App')

process_command_line(spark)
