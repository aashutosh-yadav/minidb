
## The Skeleton of a Relational Database

```
┌─────────────────────────────────┐
│         SQL Interface           │  ← What the user types
├─────────────────────────────────┤
│         Query Parser            │  ← Turns SQL string into a plan
├─────────────────────────────────┤
│        Query Executor           │  ← Runs the plan (scan, join, filter)
├─────────────────────────────────┤
│          B+ Tree Index          │  ← Fast lookups
├─────────────────────────────────┤
│         Buffer Pool             │  ← Memory management
├─────────────────────────────────┤
│         Page Manager            │  ← Fixed-size chunks on disk
├─────────────────────────────────┤
│           Disk / File           │  ← Actual storage
└─────────────────────────────────┘
```