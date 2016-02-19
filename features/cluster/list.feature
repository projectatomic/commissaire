Feature: Listing Clusters

  Scenario: List all clusters without authentication
     Given we are anonymous
      when we list all clusters
      then commissaire will deny access

  Scenario: List all clusters with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
      when we list all clusters
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is ['honeynut']
