Feature: Examining A Cluster

  Scenario: Examining an empty cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we get the cluster honeynut
      then commissaire will deny access

  Scenario: Examining an empty cluster with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
      when we get the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a dict
       and the provided cluster status is ok
       and the provided cluster total hosts is 0
       and the provided cluster available hosts is 0
       and the provided cluster unavailable hosts is 0
