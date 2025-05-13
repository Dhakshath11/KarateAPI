@PutRequest
Feature: Update user in DB

  Background:
    * url baseURL
    * header Accept = 'application/json'
    * header x-api-key = 'reqres-free-v1'

  @UpdateUser
  Scenario: Update Existing User
    Given path 'api/users/2'
    And request {"name": "morpheus", "job": "zion resident"}
    When method PUT
    Then status 200
    And print response

