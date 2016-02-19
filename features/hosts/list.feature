Feature: Listing Hosts

  Scenario: List all hosts without authentication
     Given we are anonymous
      when we list all hosts
      then commissaire will deny access

  Scenario: List all hosts with authentication
     Given we have a valid username and password
      when we list all hosts
      then commissaire will allow access