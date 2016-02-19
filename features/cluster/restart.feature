Feature: Restarting Clusters

  Scenario: Initiate cluster restart without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we initiate a restart of cluster honeynut
      then commissaire will deny access

  Scenario: Initiate cluster restart with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
      when we initiate a restart of cluster honeynut
      then commissaire will allow access
       and commissaire will note creation
       and commissaire will provide restart status
       and the provided status is in_process
