[[_TOC_]]
<br>
# PRISM Misses Pipeline failure - Due to `disconnected_at`.
<br>

<IMG  src="https://dev.azure.com/seaspan-edw/dc79f102-b651-4c74-9c83-85a2733f6cfb/_apis/wit/attachments/d95fd543-253d-453e-a757-9ec429dd5a39?fileName=image.png"  alt="Image"/>

<br>
<br>

Previously according to #2487 , it was observed that these failures are due to incomplete JSON data. I.e. a flatten command is expecting some named JSON object that is missing. The flatten command was adjusted to return NULL for missing object rather than failing.

At the moment, it seems the MISSES pipeline is still failing for some other reasons. This need to be investigated and corrected.

**Expected Behaviour**
In all cases, the pipeline is expected to succeed on it's daily run.


**Actual Behaviour**

![2.png](/.attachments/2-8c86c0f0-fcde-4c7f-bae9-d16ae10dec85.png)



The following distinct errors have been observed:
Databricks execution failed with error state Terminated. For more details please check the run page url: https://adb-4379826858178347.7.azuredatabricks.net/?o=4379826858178347#job/977756986937981/run/19089308.

<br>
<br>

- **ATTEMPTED SOLUTION**

Due to the pipeline failure referenced in bug #2532   in MISSES_SHORE_POWER_UTILIZATION <br>


![image (2).png](https://dev.azure.com/seaspan-edw/dc79f102-b651-4c74-9c83-85a2733f6cfb/_apis/git/repositories/9e8bce23-7718-45e9-b6b4-9ac8354c6c73/pullRequests/940/attachments/image%20%282%29.png) 

We adjusted the flatten command to have `disconnect_at` use the get_json_object function just as how the issue with the `connected_at` field in bug #2487 was resolved. 

We added `get_json_object(to_json(reasons_info),'$.disconnected_at ') as disconnected_at` to the code, but unfortunately it didn't work well. Though the pipeline run and tests succeeded, it returned `disconnected_at` as all NULL even though there was data present, see figure below.

![image.png](https://dev.azure.com/seaspan-edw/dc79f102-b651-4c74-9c83-85a2733f6cfb/_apis/git/repositories/9e8bce23-7718-45e9-b6b4-9ac8354c6c73/pullRequests/940/attachments/image.png) 

**- ROOT CAUSE.**

We discovered that the problem is that the second element in the `reasons` array does not contain `disconnected_at` Instead, it has `connected_at`, but the first element is already processed by the get_json_object and returned NULL and also cannot find `disconnected_at` in the second element.

![image (4).png](https://dev.azure.com/seaspan-edw/dc79f102-b651-4c74-9c83-85a2733f6cfb/_apis/git/repositories/9e8bce23-7718-45e9-b6b4-9ac8354c6c73/pullRequests/940/attachments/image%20%284%29.png) 


**- RESOLUTION**

To fix this issue, we tried to handle each element separately, ensuring that it only try to extract keys that exist within each JSON object. We used a CASE WHEN statements to check if the key exists before attempting to extract the value. Then it seems to work well now and returned the values as below.

![image (3).png](https://dev.azure.com/seaspan-edw/dc79f102-b651-4c74-9c83-85a2733f6cfb/_apis/git/repositories/9e8bce23-7718-45e9-b6b4-9ac8354c6c73/pullRequests/940/attachments/image%20%283%29.png) 


<br>
<br>


_________________________________________________
# PRISM Misses Pipeline failure - Due to `connected_at`.


![7.png](/.attachments/7-b7d064f9-e2d0-4277-abf4-f1075580066f.png)


**OBSERVATIONS.**
The following errors were observed:

- MISSES_DUAL_FUEL_ENGINE_GAS_MODE: _AnalysisException: cannot resolve 'fuel_oil_consumption.fuel_amount_.*'

- MISSES_SHORE_POWER_UTILIZATION: AnalysisException: _No such struct field connected_at in disconnected_at, type, undocked_at_;

- MISSES_DUAL_FUEL_ENGINE_GAS_MODE: _AnalysisException: [UNRESOLVED_COLUMN.WITH_SUGGESTION] A column or function parameter with name `voyage`.`number` cannot be resolved._

**ROOT CAUSE.**
These failures are due to incomplete incoming JSON data. 
The flatten command was expecting to JSON objects that is not present in the incoming data.

**SOLUTION**
The flatten command was amended so that at all times the pipeline succeeds and the column set to NULL when some of the field of the JSON object is not provided.
<br>
<br>
_________________________________________________

# Missing Rows in `vw_MISSES_ENERGY_CONSUMPTION` 
<br>

**OBSERVATION**
Observed that the data that was fetched on a particular run was missing some data,   however, when calling the API with the same `from_date`, the response contains the missing rows. 

PROBABLE CAUSE

The `from_date` query parameter is constructed in the pipeline by appending a Z to the Watermark_End as stored in cfgBronze.

![8.5.png](/.attachments/8.5-de09136a-b16a-4ec9-9a9e-092e0c31827f.png)

![8.png](/.attachments/8-530f4104-8e9f-4cae-93c9-8de63794b83c.png)
Using this time in the REST API really does return no results which is the cause of the missing data.

![9.png](/.attachments/9-fb55a46a-17b5-4284-b1d0-ffbf7d15ebb7.png)

**SOLUTION**

Internally, the pipeline has been aligned to use UTC when setting and using a watermark datetime. The PRISM REST API was also called using a UTC time (without timezone query, it defaults to expecting UTC times)
![10.png](/.attachments/10-c04d00eb-a44d-464b-b11f-a56ac847f3ef.png)
So, the `watermark_end` will be stored in UTC only.