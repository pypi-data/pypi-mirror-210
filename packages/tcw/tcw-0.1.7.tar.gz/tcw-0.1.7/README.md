# TCW: Tiny Contest Winners
A simple web app to create ephemeral raffle contests.

## Description
Allows someone to create a contest. When the contest has expired, the winners
will be randomly selected and emailed to the original contest creator.

## Contest Expiration
A contest is finished once its expiration time has passed, or once the max
number of entrants is reached.

## Contest Entrants
The contest creator is responsible for managing the signup link to the contest,
and distributing it to potential entrants. There is no search or recovery
option for a lost contest link.

## Notifications
This app does not notify the winners. The contest creator will be notified by
email of the winners once the contest expires. It is the responsibility of the
contest creator to notify entrants if they won.

## Storage of Contest data
Once a Contest has expired, and the creator of the contest has been notified
of the winners, all information about the contest is removed from the database.
This information cannot be recovered.
