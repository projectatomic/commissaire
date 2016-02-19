Feature: Upgrading Clusters

  Scenario: Initiate cluster upgrade without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we initiate an upgrade of cluster honeynut
      then commissaire will deny access

  Scenario: Initiate cluster upgrade with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
      when we initiate an upgrade of cluster honeynut
      then commissaire will allow access
       and commissaire will note creation
       and commissaire will provide upgrade status
       and the provided status is in_process
