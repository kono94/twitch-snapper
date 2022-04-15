import { createLogger, format, transports } from "winston"

const myFormat = format.combine(
  format.timestamp({ format: "MMM-DD-YYYY HH:mm:ss" }),
  format.align(),
  format.printf((info) => `${info.level}: ${[info.timestamp]}: ${info.message}`)
)
const logger = createLogger({
  transports: [
    new transports.Console({ format: myFormat }),
    new transports.File({
      filename: "logs/server.log",
      format: myFormat,
    }),
  ],
})

export default logger
