Feature: Creating Hosts

  Scenario: Creating a new host without authentication
     Given we are anonymous
      when we create the host 10.2.0.2
      then commissaire will deny access

  Scenario: Creating a new host with authentication
     Given we have a valid username and password
      when we create the host 10.2.0.2
      then commissaire will allow access
      and commissaire will note creation
      and commissaire will return the single host

  Scenario: Recreating a compatible host with authentication
     Given we have a valid username and password
       and we have a host at 10.2.0.2
      when we create the host 10.2.0.2
      then commissaire will allow access
      and commissaire will note success

  Scenario: Recreating an incompatible host with authentication
     Given we have a valid username and password
      and we have a host at 10.2.0.2
      and we set the key to bogus data
      when we create the host 10.2.0.2
      then commissaire will allow access
      and commissaire will note a conflict
