# Meetings notes

## Meeting 1.
* **DATE: 22.1.2023**
* **Participants: Martti, Juho, Kalle, Lauri**

### Minutes
Initial meeting, conversation about which type of API should be create.
What kind of background do group members have with web development and API development.
Discussion about ways of working, weeklies, action tracking, etc.
Initial actions to take in the first weeks of development.

### Action points
- Use GitHub projects to track work
- No code pushes to master, create pull request and atleast one member to approve ( 4 eye principle )
- Keep repository public
- At beginning meet biweekly, move to meet weekly when needed
- It was decided to create a dog API
- Create initial actions in GitHub projects to kickoff the project.


## Meeting 2.
* **DATE: 3.2.2023**
* **ASSISTANTS: Ivan**
* **Participants: Martti, Juho, Kalle, Lauri**

### Minutes
First return meeting with Ivan. Conversation about the initial idea of API and database model. The API meets the requirements for this course, however some additional functionality to achieve even greater score. Overview was good, API uses was found good and related work was good, but needed some tuning. 

### Action points
- Fix the wiki by given feedback, one more API usage
- Continue with current database model
- Initialize the db with minimal two entries
- Create contributing guidelines to repo


## Meeting 3.
* **DATE: 21.2.2023**
* **ASSISTANTS: Ivan**
* **Participants: Martti, Juho, Kalle, Lauri

### Minutes
Discussion about the database model that we have provided thus far. Lightly evaluating the current model. It was found that some other datatypes could be chosen for some columns (excercise time from varchar -> datetime OR float). Some work was found to be done for the database model to achieve higher grade.

### Action points
- Provide more information in README.md from the database architechture (technologies used etc...)
- Mention which software is used in wiki information (to show tables) to help assistants
- Provide all information available, e.g. database limitations, hyperlinks in README.md
- Add more restrictions to data, include to see easily in wiki
- Better README for database, include own README in database folder. Take some hint from CONTRIBUTING.md folder
- Add ondelete behavior
- 

## Meeting 4.
* **DATE: no date captured**
* **ASSISTANTS: Ivan**
* **Participants: Martti, Lauri**

### Minutes
Better routing, maybe route breeds under groups, link facts to breeds /api/groups/breed/facts/n-fact
/api/groups/terrier/breeds/23872
maybe hash groups breeds in database to not EXPOSE PRIMARY KEYS in url, maybe add url in underscore e.g. Australian_terrier or Australian%20terrier, latter is handled in SQLalchemy to result in Australian terrier
Explain addressability and uniform interface more betterly, architecture statelesness, Use better project layout from lovelace. Better the documentation

### Action points
- Discuss the routing with team
- Atleast remove url queries that expose primary keys
- add handling for both underscore and %20 in uri

## Midterm meeting
* **DATE:12.4.2023**
* **ASSISTANTS: Ivan**
* **Participants: Martti, Kalle**

### Minutes
Root route should be /api/ and be shown in dead end in Group -> GroupCollection, cannot get away, need to be connected, when you add, edit, delete you should stay in same state, not change it. Swagger to get the points from documentation, Update characteristics colletion, better hierarchy with /groups/.

### Action points
- Edit the diagram, (add, edit, delete) should not modify the state, e.g. no jump from
- Link Relations should be named only (add, edit, delete) no add-breeds
- CharacteristicCollection should be named CharecteristicItem
- Add CharacacteristicCollection to get all chars
- Better Group hierarchy by adding /groups/ infront of all items
- Add documentation via Swagger


## Final meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




