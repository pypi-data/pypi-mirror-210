# fabcohort
A small demo library for a fab_cohort about cohort analysis

### Installation
```
pip install fabcohort
```

### Get started
How to do cohort analysis with this lib:

#### **FUNCTION1**: 
Vanilla cohort analysis 

Pandas df.head(5) should look like - 
| user_id | date | count |
| -------- | -------- | -------- |
| 5fb507360cd5c0   | 2023-04-01   | 1   |
| weg507360cwfw3   | 2023-03-01   | 1   |
| 6001ef966c13w3   | 2023-02-01   | 1   |
| weg507360cwfw3   | 2023-04-01   | 1   |
| 6001ef966c13w3   | 2023-03-01   | 1   |

```Python
from fab_cohort import Cohort

# Instantiate a Cohort object
cohort = Cohort()

# Call the count_cohort method
result = cohort.count_cohort(df)

```

#### **FUNCTION2**: 
Cohort analysis by segments

Pandas df.head(5) should look like - 
| user_id | date | segment | count |
| -------- | -------- | -------- | -------- |
| 5fb507360cd5c0   | 2023-04-01   | A,B   | 1   |
| weg507360cwfw3   | 2023-03-01   | A,    | 1   |
| 6001ef966c13w3   | 2023-02-01   | C,D   | 1   |
| weg507360cwfw3   | 2023-04-01   | B,D   | 1   |
| 6001ef966c13w3   | 2023-03-01   | A,B   | 1   |

```Python
from fab_cohort import Cohort

# Instantiate a Cohort object
cohort = Cohort()

# Call the count_cohort_segments method
result = cohort.count_cohort_segments(df)

# (Optional) if you have multiple segments just parse it
result[['segment1', 'segment2']] = result['segment'].str.split(',', expand=True)
result.drop('segment', axis=1, inplace=True)

```

#### **FUNCTION3**: 
Convert the count to percentage

```Python
# once the above result is obtained

# Call the count_cohort method
result_pct = cohort.to_pct(result)

# (Optional) if you have multiple segments just parse it
result[['segment1', 'segment2']] = result['segment'].str.split(',', expand=True)
result.drop('segment', axis=1, inplace=True)

```