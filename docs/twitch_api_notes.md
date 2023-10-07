### Clips

POST https://api.twitch.tv/helix/clips

broadcaster_id : string
has_delay : boolean

Returns:
edit_url: string
id: string

### User Info

GET https://api.twitch.tv/helix/users

id: id

### Video (last boradcast)

GET https://api.twitch.tv/helix/videos

user_id: string

sort: string -> Sort order of the videos. Valid values: "time", "trending", "views". Default: "time".
type: string -> type of video. Valid values: "all", "upload", "archive", "highlight". Default: "all".
