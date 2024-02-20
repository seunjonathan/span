#from curate_parquet.py import *
from curate_parquet import process_command_line
from curate_parquet import get_or_create_spark
#i have a python file called curate_parquet.py that has a function called process_command_line(spark) that takes in a spark session and does some stuff with it.
#i want to call this function from another python file called spark_main.py, so why is this not working?
'''
    Example command line:
        python spark_main.py -s bronze -d silver -t T_CUSTOMERTYPE1 -v TOPSv2 -i n -j '[{"table_name":"T_CUSTOMERTYPE","renaming_instructions":"select pk_CustomerType_in, Code_ch as Tier_Code, Name_vc as Tier_Name, LastUpdate_ts, Deleted_dt from T_CUSTOMERTYPE"}]' -a '[{"error_message":"","validation_command":""}]'
'''

spark = get_or_create_spark('Local-Spark-App')

process_command_line(spark)
