CREATE CONSTRAINT IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Organization) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Location) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Date) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Product) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Event) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:WorkOfArt) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Law) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Language) REQUIRE n.name IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.name IS UNIQUE
MERGE (n:Person {name: 'Ross Eustace'})
MERGE (n:Person {name: 'David Schwimmer'})
MERGE (n:Organization {name: 'NBC'})
MERGE (n:Organization {name: 'Friends'})
MERGE (n:Person {name: 'Ross'})
MERGE (n:Person {name: 'Rachel Green'})
MERGE (n:Organization {name: 'Guide'})
MERGE (n:Organization {name: 'Entertainment Weekly\'s'})
MERGE (n:Person {name: 'Kevin Bright'})
MERGE (n:Person {name: 'Schwimmer'})
MERGE (n:Entity {name: 'the most intelligent member'})
MERGE (n:Entity {name: 'the group'})
MERGE (n:Entity {name: 'His relationship'})
MERGE (n:Entity {name: 'the best TV couples'})
MERGE (n:Entity {name: 'all time'})
MERGE (n:Entity {name: 'TV Couples".[5'})
MERGE (n:Entity {name: 'the executive producers'})
MERGE (n:Entity {name: 'the show'})
MERGE (n:Entity {name: 'the writers'})
MERGE (n:Entity {name: 'the show.[6'})
MERGE (n:Entity {name: 'His relationship with Rachel Green'})
MERGE (n:Entity {name: 'Entertainment Weekly \'s " 30 Best'})
MERGE (n:Entity {name: 'Ross \'s character in Schwimmer \'s voice'})
MERGE (n:Entity {name: 'the six main characters of the NBC sitcom Friends'})
MERGE (n:Entity {name: 'of the NBC sitcom Friends'})
MERGE (n:Entity {name: 'the most intelligent member of the group'})
MERGE (n:Entity {name: 'of the group'})
MERGE (n:Entity {name: 'with Rachel Green'})
MERGE (n:Entity {name: 'TV Guide \'s list of the best TV couples of all time , as well as'})
MERGE (n:Entity {name: 'of the best TV couples of all time , as well as'})
MERGE (n:Entity {name: 'the best TV couples of all time , as well as'})
MERGE (n:Entity {name: 'of all time'})
MERGE (n:Entity {name: 'as well as'})
MERGE (n:Entity {name: 'the executive producers of the show'})
MERGE (n:Entity {name: 'of the show'})
MERGE (n:Entity {name: 'in Schwimmer \'s voice'})
MERGE (n:Entity {name: 'his'})
MERGE (n:Entity {name: 'his goofy but lovable'})
MERGE (n:Entity {name: 'His'})
MERGE (n:Entity {name: 'TV Guide \'s'})
MERGE (n:Entity {name: 'Entertainment Weekly \'s'})
MERGE (n:Entity {name: 'Ross \'s'})
MERGE (n:Entity {name: 'Schwimmer \'s'})
MERGE (n:Entity {name: 'Schwimmer \'s voice'})

            MATCH (a), (b)
            WHERE a.name = 'the writers' AND b.name = 'Ross \'s character in Schwimmer \'s voice'
            MERGE (a)-[r:DEVELOPING]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'His relationship with Rachel Green' AND b.name = 'Entertainment Weekly \'s " 30 Best'
            MERGE (a)-[r:INCLUDED]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'His relationship with Rachel Green' AND b.name = 'with Rachel Green'
            MERGE (a)-[r:WITH]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'Ross \'s character in Schwimmer \'s voice' AND b.name = 'in Schwimmer \'s voice'
            MERGE (a)-[r:IN]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'the six main characters of the NBC sitcom Friends' AND b.name = 'of the NBC sitcom Friends'
            MERGE (a)-[r:OF]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'the most intelligent member of the group' AND b.name = 'of the group'
            MERGE (a)-[r:OF]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'TV Guide \'s list of the best TV couples of all time , as well as' AND b.name = 'of the best TV couples of all time , as well as'
            MERGE (a)-[r:OF]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'the best TV couples of all time , as well as' AND b.name = 'of all time'
            MERGE (a)-[r:OF]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'the best TV couples of all time , as well as' AND b.name = 'as well as'
            MERGE (a)-[r:AS]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'the executive producers of the show' AND b.name = 'of the show'
            MERGE (a)-[r:OF]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'his' AND b.name = 'his goofy but lovable'
            MERGE (a)-[r:HAS]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'His' AND b.name = 'His relationship with Rachel Green'
            MERGE (a)-[r:HAS]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'TV Guide \'s' AND b.name = 'TV Guide \'s list of the best TV couples of all time , as well as'
            MERGE (a)-[r:HAS]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'Entertainment Weekly \'s' AND b.name = 'Entertainment Weekly \'s " 30 Best'
            MERGE (a)-[r:HAS]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'Ross \'s' AND b.name = 'Ross \'s character in Schwimmer \'s voice'
            MERGE (a)-[r:HAS]->(b)
            

            MATCH (a), (b)
            WHERE a.name = 'Schwimmer \'s' AND b.name = 'Schwimmer \'s voice'
            MERGE (a)-[r:HAS]->(b)
            