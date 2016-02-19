Feature: Deleting Hosts

  Scenario: Deleting a host without authentication
     Given we are anonymous
       and we have a host at 10.2.0.2
      when we delete the host 10.2.0.2
      then commissaire will deny access

  Scenario: Deleting a host with authentication
     Given we have a valid username and password
       and we have a host at 10.2.0.2
      when we delete the host 10.2.0.2
      then commissaire will allow access
       and commissaire will note it's gone
