import express from 'express'
import BodyParser from 'body-parser'

const app = express()

const PORT = process.env.NODE_ENV === 'development' ? 5000 : 80

app.use(BodyParser.json())




app.listen(PORT, () => {
    console.log(`[ INFO ] App is ready @ ${PORT}`)
})

// Express has problems w/ SIGINT
process.on('SIGINT', () => process.exit())
