Feature: Deleting A Cluster

  Scenario: Deleting a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we delete the cluster honeynut
      then commissaire will deny access

  Scenario: Deleting a cluster with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
      when we delete the cluster honeynut
      then commissaire will allow access
       and commissaire will note it's gone
