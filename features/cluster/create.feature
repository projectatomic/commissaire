Feature: Creating A Cluster

  Scenario: Creating a new cluster without authentication
     Given we are anonymous
      when we create the cluster honeynut
      then commissaire will deny access

  Scenario: Creating a new cluster with authentication
     Given we have a valid username and password
      when we create the cluster honeynut
      then commissaire will allow access
       and commissaire will note creation

  Scenario: Recreating a compatible cluster with authentication
     Given we have a valid username and password
      when we create the cluster honeynut
      then commissaire will allow access
       and commissaire will note creation
