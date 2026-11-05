# Evaluation results

Model: muse-spark-1.3. Prices in USD per 1M tokens: input 1.25, cached 0.15, output 4.25.

A run passes only if it finished before the step cap, its target and protected tests pass, and it edited only files its task allows. Cost per passing task divides total spend, including failed runs, by the number of passing runs.

## By mode

| Group | Runs | Pass rate | Finished | Out-of-scope runs | Avg prompt | Avg cached | Avg output | Avg steps | Avg reads suppressed | Avg cost/run | Cost per passing task |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 20 | 100% | 100% | 0 | 10485 | 5683 | 1202 | 5.8 | 0.0 | $0.0120 | $0.0120 |
| truncate-only | 20 | 100% | 100% | 0 | 9429 | 6216 | 1308 | 5.9 | 0.0 | $0.0105 | $0.0105 |
| optimized | 20 | 100% | 100% | 0 | 9284 | 6523 | 1271 | 5.8 | 0.2 | $0.0098 | $0.0098 |

## By task

| Group | Runs | Pass rate | Finished | Out-of-scope runs | Avg prompt | Avg cached | Avg output | Avg steps | Avg reads suppressed | Avg cost/run | Cost per passing task |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tr1_heavy_surcharge / baseline | 5 | 100% | 100% | 0 | 8549 | 4693 | 818 | 5.0 | 0.0 | $0.0090 | $0.0090 |
| tr1_heavy_surcharge / truncate-only | 5 | 100% | 100% | 0 | 7320 | 5042 | 963 | 5.2 | 0.0 | $0.0077 | $0.0077 |
| tr1_heavy_surcharge / optimized | 5 | 100% | 100% | 0 | 6962 | 4712 | 796 | 5.0 | 0.0 | $0.0069 | $0.0069 |
| tr2_grand_total / baseline | 5 | 100% | 100% | 0 | 7820 | 4542 | 1019 | 5.0 | 0.0 | $0.0091 | $0.0091 |
| tr2_grand_total / truncate-only | 5 | 100% | 100% | 0 | 8081 | 5221 | 1194 | 5.2 | 0.0 | $0.0094 | $0.0094 |
| tr2_grand_total / optimized | 5 | 100% | 100% | 0 | 8223 | 6476 | 1221 | 5.2 | 0.0 | $0.0083 | $0.0083 |
| tr3_summary_order / baseline | 5 | 100% | 100% | 0 | 9088 | 3652 | 848 | 5.0 | 0.0 | $0.0109 | $0.0109 |
| tr3_summary_order / truncate-only | 5 | 100% | 100% | 0 | 7704 | 5352 | 948 | 5.0 | 0.0 | $0.0078 | $0.0078 |
| tr3_summary_order / optimized | 5 | 100% | 100% | 0 | 7764 | 4994 | 894 | 5.0 | 0.0 | $0.0080 | $0.0080 |
| tr4_reject_discount / baseline | 5 | 100% | 100% | 0 | 16484 | 9844 | 2124 | 8.2 | 0.0 | $0.0188 | $0.0188 |
| tr4_reject_discount / truncate-only | 5 | 100% | 100% | 0 | 14613 | 9247 | 2126 | 8.2 | 0.0 | $0.0171 | $0.0171 |
| tr4_reject_discount / optimized | 5 | 100% | 100% | 0 | 14189 | 9912 | 2175 | 8.2 | 1.0 | $0.0161 | $0.0161 |
