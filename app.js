import "dotenv/config"
import { Client as IRCClient } from "tmi.js"
import axios from "axios"
import Logger from "./util/Logger.js"

const CHANNEL = "asmongold"
let nChatters = 0

Logger.info("kek")
// Define configuration options
const opts = {
  identity: {
    username: "lul_snapper",
    password: process.env.IRC_OAUTH,
  },
  channels: [CHANNEL],
}

// Create a client with our options
const client = new IRCClient(opts)
// Connect to Twitch:
client.connect()

// Called every time a message comes in
const onMessageHandler = (target, context, msg, self) => {
  if (self) {
    return
  } // Ignore messages from the bot

  // Remove whitespace from chat message
  const trimmedMsg = msg.trim()
  console.log(trimmedMsg)
}

const fetchViewerCount = async () => {
  console.log("Fetching viewer count...")
  let chatterCount = 0
  try {
    const res = await axios.get(
      `https://tmi.twitch.tv/group/user/${CHANNEL}/chatters?`
    )
    chatterCount = res.data.chatter_count
  } catch (err) {
    console.log(err)
  }
  return chatterCount
}

// Called every time the bot connects to Twitch chat
const onConnectedHandler = async (addr, port) => {
  console.log(`* Connected to ${addr}:${port}`)
  nChatters = fetchViewerCount()
}

setInterval(() => {
  nChatters = fetchViewerCount()
}, 60 * 60)

// Register our event handlers (defined below)
client.on("message", onMessageHandler)
client.on("connected", onConnectedHandler)
