// Create a person node
QUERY createPerson (name: String, tags: [String], text: String) =>
    person <- AddN<Person>({
        name: name,
        tags: tags,
        text: text
    })
    RETURN person

// Create a team node
QUERY createTeam (name: String, text: String) =>
    team <- AddN<Team>({
        name: name,
        text: text
    })
    RETURN team

// Add a person as a regular team member
QUERY addTeamMember (person_id: ID, team_id: ID) =>
    person <- N<Person>(person_id)
    team <- N<Team>(team_id)
    edge <- AddE<Person_member_of_Team>()::From(person)::To(team)
    RETURN edge

// Add a person as a manager of a team
QUERY addTeamManager (person_id: ID, team_id: ID) =>
    person <- N<Person>(person_id)
    team <- N<Team>(team_id)
    edge <- AddE<Person_manager_of_Team>()::From(person)::To(team)
    RETURN edge

// Get all members for a given team
QUERY getTeamMembers (team_id: ID) =>
    team <- N<Team>(team_id)
    members <- team::In<Person_member_of_Team>
    RETURN members

// Get all managers for a given team
QUERY getTeamManagers (team_id: ID) =>
    team <- N<Team>(team_id)
    managers <- team::In<Person_manager_of_Team>
    RETURN managers

// Lookup helpers by name
QUERY getPersonByName (person_name: String) =>
    person <- N<Person>::WHERE(_::{name}::EQ(person_name))
    RETURN person

QUERY getTeamByName (team_name: String) =>
    team <- N<Team>::WHERE(_::{name}::EQ(team_name))
    RETURN team

// (Optional) list all people / teams
QUERY getAllPeople () =>
    people <- N<Person>
    RETURN people

QUERY getAllTeams () =>
    teams <- N<Team>
    RETURN teams
