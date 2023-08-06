
# we dont care if the job was created or updated, we just want to know if it is waiting to run:
JOB_WAITING = '''
subscription  JobWaiting(
  $workerCode: String!
){
  jobs(
    filter: {
      workerCode: $workerCode
      jobStatus: WAITING
    }){
    action
    successful
    messages{field message}
    result{
      id
      userId
      input
      context
      output
      progress
      jobStatus
      queue {
        id
        name
        alias
        type
        enabled
        context # for rehydration
        schedule
        query
        lockRequired
        # locks(orderBy:{desc:ID} limit: 1){
          # id
          # active
          # startAt
          # endAt
        # }
      }
      worker{
        id
        code
        name
      }
    }
  }
}
'''

JOB_UPDATED = '''
subscription {
  jobUpdated{
    successful
    messages{
      field
      message
    }
    result{
      id
      jobStatus
    }
  }
}
'''

LOCKS_UPDATED = '''
subscription locksUpdated {
  queueLocks {
    successful
    action
    messages {
      field
      message
    }
    result {
      id
      insertedAt
      updatedAt
      active
      startAt
      endAt
      queue {
        id
        name
      }
    }
  }
}
'''
