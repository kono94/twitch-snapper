## Backlog

- ✅ <b>Support multiple channel trackers</b>
  - ✅ Hold IRC connection as singletone
  - ✅ (design) handle each channel in a separate wrapper-thread or process them in a single method on receiving a new message, assigning them to the channel they were sent to
  - ✅ extend keyword map to handle multiple channels OR a separate callback function per channel
- ✅ <b>Create clips of keyword-triggered moments</b>
  - ✅ Call the twitch API to create a clip and save said clip to the DB
  - ✅ Mark the point in time in the VOD (however not always available due to streamer's settings -> turned off or behind subscription pay-wall)
- ✅ <b>Come up with a simple database schema</b>
  - ✅ We might want to use PostgresSQL as a database which should be slightly different to standard MariaDB/MySQL?
  - ✅ Maybe we also want to integrate an ORM in Python and Flask?
- ✅ <b>Test the flexibility of Flask in terms of frontend design and reactive capabilities</b>
  - ✅ A server-side rendered site might be sufficient for the moment
  - ✅ Simply display the saved clip on a static website
  - Sort function for keywords and streamers
- ✅ <b>Make frontend dynamic via infinite scrolling</b>
- Refactor database model
  - Keywords will become a seperate table with image; This way, one can sort clips by individual keywords + easily construct a filter page based on keyword.
    This can also be done by just selecting all keywords from all clips, but this does not contain attributes for keywords like images
  - Cross table for streams and keywords that include keyword_trigger per individual keyword
- Check if channel allows clips
  - broadcaster with id=woowakgood does not allow clip generation...
