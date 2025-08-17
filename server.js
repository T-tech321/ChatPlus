// server.js
const express = require("express");
const { spawn } = require("child_process");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.json());
app.use(express.static("public"));

let context = "";

app.post("/chat", (req, res) => {
    const userMessage = req.body.message;
    context += `User: ${userMessage}\nAI: `;

    // Call Python script for generation
    const py = spawn("python", ["ai_core.py", context]);
    let aiResponse = "";
    py.stdout.on("data", (data) => { aiResponse += data.toString(); });
    py.on("close", () => {
        context += aiResponse + "\n";
        res.json({ response: aiResponse });
    });
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
