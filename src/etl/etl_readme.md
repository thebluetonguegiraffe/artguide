# 🧵 ETL Pipeline: Threads and Queues Overview

This document explains how the ETL pipeline works internally, focusing on **which threads interact with which queues**, and how data flows through each stage.

---

## 🧩 Pipeline Overview

The ETL process consists of **three main stages**, connected by **two queues**:

| Stage               | Thread                 | Produces / Consumes                                             | Queue Interaction                       |
| ------------------- | ---------------------- | --------------------------------------------------------------- | --------------------------------------- |
| **Extract**   | Main thread            | Produces batches                                                | ➡️ puts data into `transform_queue` |
| **Transform** | TransformWorker thread | Consumes from `transform_queue`, produces into `load_queue` | 🔄 uses both                            |
| **Load**      | LoadWorker thread      | Consumes from `load_queue`                                    | ⬇️ loads to the database              |

Inside `transform()`, there is a **ThreadPoolExecutor (5 threads by default)** that processes each painting in parallel — these **do not interact with any queues**.

- **Threads**: Allow multiple stages to run simultaneously
- **Queues**: Allow threads to communicate securely and simply

---

## 🧠 Active Threads Summary

| Thread Type                | Count         | Uses Queues                                                        | Description                              |
| -------------------------- | ------------- | ------------------------------------------------------------------ | ---------------------------------------- |
| Main thread                | 1             | ✅ produces into `transform_queue`                               | Runs `extract()`, orchestrates the ETL |
| Transform worker           | 1             | ✅ consumes from `transform_queue`, produces into `load_queue` | Performs data transformation             |
| Load worker                | 1             | ✅ consumes from `load_queue`                                    | Loads data into the database             |
| Transform internal threads | 5 (per batch) | ❌                                                                 | Parallelize `parse_painting()` calls   |

#### Why we should use different threads?

If you ran everything in the main thread sequentially, it would look like this:

```
`for batch in self.extract():
    enriched = self.transform(batch)  # Waits here
    self.load(enriched)  # Then waits here
```

So:

* **Separate threads** : Enable **pipeline parallelism** (multiple stages running at once)
* **ThreadPoolExecutor** : Enables **data parallelism** (processing multiple items within a stage)
