const express = require("express");
const ciweimao = require("./ciweimao");

const app = new express();

app.use((req, res, next) => {
  console.log(`[${Date.now()}] ${req.method} ${req.url}`);
  next();
});
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.post("/decrypt", (req, res) => {
  const { kind, website, data } = req.body;

  let result = null;
  if (kind === "novel" && website === "ciweimao") {
    result = ciweimao.decrypt(data);
  }
  res.json({
    data: result,
    serverTime: Date.now(),
  });
});

app.on("error", (err) => {
  console.error("server error", err);
});

const port = 3000;
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
