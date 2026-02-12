require("dotenv").config();
const axios = require("axios");

const express = require("express");

const app = express();
app.use(express.json()); // JSON body parse karega

app.post("/webhook", async (req, res) => {
    console.log("Webhook received!");

    const action = req.body.action;

    if (action === "opened") {
        const repoOwner = req.body.repository.owner.login;
        const repoName = req.body.repository.name;
        const prNumber = req.body.number;

        console.log("PR Opened:", prNumber);

        const url = `https://api.github.com/repos/${repoOwner}/${repoName}/pulls/${prNumber}/files`;

        try {
            const response = await axios.get(url, {
                headers: {
                    Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
                    Accept: "application/vnd.github+json"
                }
            });

            console.log("Changed Files:");
            response.data.forEach(file => {
                console.log("File:", file.filename);
            });

        } catch (error) {
            console.error("Error fetching PR files:", error.message);
        }
    }

    res.status(200).send("Received");
});
app.listen(3000, () => {
    console.log("Server running on port 3000");
});