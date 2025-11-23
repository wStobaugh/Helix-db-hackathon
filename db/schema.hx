// Person = individual employee
N::Person {
    // For fast lookup by name
    INDEX name: String,

    // Skillset, personality, domain tags, etc.
    // Example: ["backend", "introvert", "golang", "manager-track"]
    tags: [String],

    // Natural language summary of this person
    text: String,

    // Optional metadata you can use later
    created_at: Date DEFAULT NOW
}

// Team = group that people get assigned into
N::Team {
    // Team name (e.g. "Platform Infra", "Applied ML - Risk")
    INDEX name: String,

    // Natural language summary of the team
    text: String,

    created_at: Date DEFAULT NOW
}

// Edge: Person is a (regular) member of a Team
E::Person_member_of_Team {
    From: Person,
    To: Team,
    Properties: {
    }
}

// Edge: Person is a manager of a Team
E::Person_manager_of_Team {
    From: Person,
    To: Team,
    Properties: {
    }
}
